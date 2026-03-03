import feedparser
import datetime
import ssl
from urllib.parse import urlparse
import requests

# SSL 问题
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# 简单翻译
def translate_title(title):
    try:
        eng_chars = sum(1 for c in title if c.isalpha())
        total_chars = len([c for c in title if c.strip()])
        if total_chars == 0 or eng_chars / total_chars < 0.5:
            return title
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={requests.utils.quote(title)}"
        res = requests.get(url, timeout=3)
        return res.json()[0][0][0]
    except:
        return title

# 来源名称
def get_source_name(url):
    try:
        domain = urlparse(url).netloc
        m = {
            "zaobao": "联合早报",
            "chinanews": "中国新闻网",
            "sina": "新浪新闻",
            "ifeng": "凤凰新闻",
            "qq": "腾讯新闻",
            "163": "网易新闻",
            "thepaper": "澎湃新闻",
            "caixin": "财新网",
            "yicai": "第一财经",
            "jiemian": "界面新闻",
            "reuters": "路透社",
            "bbc": "BBC",
            "cnn": "CNN",
            "cnbc": "CNBC",
            "washingtonpost": "华盛顿邮报"
        }
        for k, v in m.items():
            if k in domain:
                return v
        return domain.split('.')[1].capitalize() if '.' in domain else "新闻"
    except:
        return "新闻"

# 判断是否国内来源
def is_chinese_source(source):
    cn_sources = [
        "中国新闻网", "新浪新闻", "凤凰新闻", "腾讯新闻",
        "网易新闻", "澎湃新闻", "财新网", "第一财经",
        "界面新闻", "联合早报"
    ]
    return any(s in source for s in cn_sources)

# 新闻源
def get_news_sources():
    return [
        "https://www.chinanews.com/rss/news.xml",
        "https://www.chinanews.com/rss/finance.xml",
        "https://www.chinanews.com/rss/tech.xml",
        "https://www.zaobao.com/rss/cs.html",
        "https://www.zaobao.com/rss/world.xml",
        "https://news.ifeng.com/rss/mainland.xml",
        "https://news.ifeng.com/rss/world.xml",
        "https://news.ifeng.com/rss/finance.xml",
        "https://news.ifeng.com/rss/tech.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://www.reuters.com/rssFeed/worldNews",
        "https://www.reuters.com/rssFeed/businessNews",
        "https://www.reuters.com/rssFeed/technologyNews",
        "https://www.cnn.com/services/rss/rss_topstories.rss",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    ]

# 抓取新闻
def get_real_news():
    sources = get_news_sources()
    all_news = []

    for url in sources:
        try:
            feed = feedparser.parse(url)
            source = get_source_name(url)
            for e in feed.entries[:12]:
                title = translate_title(e.title.strip())
                link = e.link.strip()
                pub = e.get('published', '')

                tag = "综合"
                if any(k in title for k in ["AI", "大模型", "芯片", "科技", "技术", "互联网", "数码"]):
                    tag = "科技"
                elif any(k in title for k in ["财经", "股市", "金融", "经济", "投资", "基金", "汇率"]):
                    tag = "金融"
                elif any(k in title for k in ["政治", "政策", "选举", "国会", "政府"]):
                    tag = "政治"
                else:
                    tag = "综合"

                all_news.append({
                    "t": title,
                    "l": link,
                    "g": tag,
                    "s": source,
                    "d": pub,
                    "cn": is_chinese_source(source)
                })
        except:
            continue

    # 去重
    seen = set()
    news_clean = []
    for n in all_news:
        if n["t"] not in seen and len(n["t"]) > 5:
            seen.add(n["t"])
            news_clean.append(n)

    # 同类下：国内来源排前面
    news_clean.sort(key=lambda x: (x["g"], 0 if x["cn"] else 1))
    return news_clean[:70]

# 生成 HTML
def make_html(data):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # 滚动行情条
    ticker = '''
<div style="background:#1f2937; color:white; padding:8px 0; overflow:hidden; white-space:nowrap;">
  <div style="display:inline-block; animation:scroll 30s linear infinite;">
    黄金 2156.50美元 | 白银 24.80美元 | 原油 79.35美元 | 天然气 2.68 | 伦铜 8525 | 铝 2260 | 煤炭 128.5 | 螺纹钢 3680 | 纯碱 1950 | 甲醇 2430 | 尿素 2360
  </div>
</div>
<style>
@keyframes scroll {
  0% { transform:translateX(100%); }
  100% { transform:translateX(-100%); }
}
</style>
'''

    nav = '''
<nav style="text-align: center; margin-bottom: 40px; background: #f8f8f8; padding: 15px; border-radius: 8px;">
  <a href="#tech" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">科技</a>
  <a href="#finance" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">金融</a>
  <a href="#politics" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">政治</a>
  <a href="#general" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">综合</a>
</nav>
'''

    tech_html = ''
    finance_html = ''
    politics_html = ''
    general_html = ''

    for n in data:
        item = f'''
<div style="margin-bottom: 25px; border-bottom: 1px solid #f2f2f2; padding-bottom: 12px;">
  <div style="font-size: 11px; color: #999; margin-bottom: 5px;">{n['s']} • {n['d'].split('T')[0] if n['d'] else ''}</div>
  <a href="{n['l']}" target="_blank" style="color: #111; font-size: 18px; line-height: 1.5; font-weight: 500; text-decoration: none;">{n['t']}</a>
</div>
'''
        if n['g'] == '科技':
            tech_html += item
        elif n['g'] == '金融':
            finance_html += item
        elif n['g'] == '政治':
            politics_html += item
        else:
            general_html += item

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日新闻简报</title>
<style>
.category-title {{ font-size: 24px; margin: 40px 0 20px; color: #333; border-left: 4px solid #c5a059; padding-left: 10px; }}
@media (max-width: 600px) {{
  nav a {{ margin: 0 8px; font-size: 12px; }}
  .category-title {{ font-size: 20px; }}
}}
</style>
</head>
<body style="max-width: 800px; margin: auto; padding: 0 0 40px; font-family: 'Microsoft YaHei', sans-serif; background: #fdfdfd; color: #111;">
{ticker}
<header style="text-align: center; margin:30px 20px 50px; border-bottom: 4px double #eee; padding-bottom: 20px;">
  <h1 style="font-size: 36px; margin: 0; color: #222;">每日新闻简报</h1>
  <div style="color: #999; font-size: 12px; margin-top: 10px;">更新时间：{time_str}</div>
</header>
{nav}
<main style="padding:0 20px;">
<section id="tech">
<h2 class="category-title">科技</h2>
{tech_html if tech_html else '<div style="color:#999; padding:20px;">暂无科技新闻</div>'}
</section>

<section id="finance">
<h2 class="category-title">金融</h2>
{finance_html if finance_html else '<div style="color:#999; padding:20px;">暂无金融新闻</div>'}
</section>

<section id="politics">
<h2 class="category-title">政治</h2>
{politics_html if politics_html else '<div style="color:#999; padding:20px;">暂无政治新闻</div>'}
</section>

<section id="general">
<h2 class="category-title">综合</h2>
{general_html if general_html else '<div style="color:#999; padding:20px;">暂无综合新闻</div>'}
</section>

</main>
<footer style="text-align: center; margin-top: 80px; color: #ccc; font-size: 12px; padding: 20px;">
每小时自动更新
</footer>
</body>
</html>'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 更新完成：{time_str} 共 {len(data)} 条")

# 入口
if __name__ == "__main__":
    news = get_real_news()
    make_html(news)
