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
            "tech": "科技媒体",
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

# 只保留 GitHub 能稳定抓到的国内源
def get_news_sources():
    return [
        # 国内稳定可用
        "https://www.chinanews.com/rss/news.xml",
        "https://www.chinanews.com/rss/world-us.xml",
        "https://www.chinanews.com/rss/finance.xml",
        "https://www.chinanews.com/rss/tech.xml",
        "https://www.zaobao.com/rss/cs.html",
        "https://www.zaobao.com/rss/world.xml",
        "https://news.ifeng.com/rss/mainland.xml",
        "https://news.ifeng.com/rss/world.xml",
        "https://news.ifeng.com/rss/finance.xml",
        "https://news.ifeng.com/rss/tech.xml",

        # 国外
        "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
        "https://www.reuters.com/rssFeed/usNews",
        "https://www.reuters.com/rssFeed/businessNews",
        "https://www.reuters.com/rssFeed/technologyNews",
        "https://www.cnn.com/services/rss/rss_us.rss",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    ]

# 抓取新闻
def get_real_news():
    sources = get_news_sources()
    news_list = []
    chinese_us = []
    english_us = []
    other = []

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
                elif any(k in title for k in ["美国", "白宫", "华盛顿", "纽约", "加州"]):
                    tag = "美国"
                elif any(k in title for k in ["中国", "国内", "大陆", "内地"]):
                    tag = "国内"
                elif any(k in title for k in ["国际", "欧洲", "日本", "海外"]):
                    tag = "国际"
                elif any(k in title for k in ["政治", "政策", "选举", "国会"]):
                    tag = "政治"

                item = {"t": title, "l": link, "g": tag, "s": source, "d": pub}

                if tag == "美国":
                    if source in ["中国新闻网", "联合早报", "凤凰新闻"]:
                        chinese_us.append(item)
                    else:
                        english_us.append(item)
                else:
                    other.append(item)
        except:
            continue

    final = []
    final.extend([i for i in other if i["g"] == "国内"])
    final.extend([i for i in other if i["g"] == "科技"])
    final.extend([i for i in other if i["g"] == "金融"])
    final.extend(chinese_us)
    final.extend(english_us)
    final.extend([i for i in other if i["g"] not in ["国内", "科技", "金融", "美国"]])

    seen = set()
    out = []
    for x in final:
        if x["t"] not in seen and len(x["t"]) > 5:
            seen.add(x["t"])
            out.append(x)
    return out[:70]

# 生成 HTML
def make_html(data):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')

    nav = '''
<nav style="text-align: center; margin-bottom: 40px; background: #f8f8f8; padding: 15px; border-radius: 8px;">
  <a href="#china" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">国内</a>
  <a href="#tech" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">科技</a>
  <a href="#finance" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">金融</a>
  <a href="#us" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">美国</a>
  <a href="#international" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">国际</a>
  <a href="#general" style="margin:0 12px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">综合</a>
</nav>
'''

    china_html = ''
    tech_html = ''
    finance_html = ''
    us_html = ''
    inter_html = ''
    gene_html = ''

    for n in data:
        item = f'''
<div style="margin-bottom: 25px; border-bottom: 1px solid #f2f2f2; padding-bottom: 12px;">
  <div style="font-size: 11px; color: #999; margin-bottom: 5px;">{n['s']} • {n['d'].split('T')[0] if n['d'] else ''}</div>
  <a href="{n['l']}" target="_blank" style="color: #111; font-size: 18px; line-height: 1.5; font-weight: 500; text-decoration: none;">{n['t']}</a>
</div>
'''
        if n['g'] == '国内':
            china_html += item
        elif n['g'] == '科技':
            tech_html += item
        elif n['g'] == '金融':
            finance_html += item
        elif n['g'] == '美国':
            us_html += item
        elif n['g'] == '国际':
            inter_html += item
        else:
            gene_html += item

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
<body style="max-width: 800px; margin: auto; padding: 40px 20px; font-family: 'Microsoft YaHei', sans-serif; background: #fdfdfd; color: #111;">
<header style="text-align: center; margin-bottom: 50px; border-bottom: 4px double #eee; padding-bottom: 20px;">
  <h1 style="font-size: 36px; margin: 0; color: #222;">每日新闻简报</h1>
  <div style="color: #999; font-size: 12px; margin-top: 10px;">更新时间：{time_str}</div>
</header>
{nav}
<main>
<section id="china">
<h2 class="category-title">国内新闻</h2>
{china_html if china_html else '<div style="color:#999; padding:20px;">暂无国内新闻</div>'}
</section>

<section id="tech">
<h2 class="category-title">科技新闻</h2>
{tech_html if tech_html else '<div style="color:#999; padding:20px;">暂无科技新闻</div>'}
</section>

<section id="finance">
<h2 class="category-title">金融新闻</h2>
{finance_html if finance_html else '<div style="color:#999; padding:20px;">暂无金融新闻</div>'}
</section>

<section id="us">
<h2 class="category-title">美国新闻</h2>
{us_html if us_html else '<div style="color:#999; padding:20px;">暂无美国新闻</div>'}
</section>

<section id="international">
<h2 class="category-title">国际新闻</h2>
{inter_html if inter_html else '<div style="color:#999; padding:20px;">暂无国际新闻</div>'}
</section>

<section id="general">
<h2 class="category-title">综合新闻</h2>
{gene_html if gene_html else '<div style="color:#999; padding:20px;">暂无综合新闻</div>'}
</section>

</main>
<footer style="text-align: center; margin-top: 80px; color: #ccc; font-size: 12px; padding: 20px;">
每小时自动更新 · 简报主页
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
