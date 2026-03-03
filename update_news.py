import feedparser
import datetime
import ssl
from urllib.parse import urlparse
import requests

# 解决 SSL 证书问题
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# 简单英文标题翻译
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
            "appinn": "小众软件",
            "solidot": "Solidot",
            "36kr": "36氪",
            "douban": "豆瓣",
            "chinanews": "中国新闻网",
            "sina": "新浪新闻",
            "ifeng": "凤凰新闻",
            "qq": "腾讯新闻",
            "163": "网易新闻",
            "sohu": "搜狐新闻",
            "thepaper": "澎湃新闻",
            "caixin": "财新网",
            "jiemian": "界面新闻",
            "yicai": "第一财经",
            "techweb": "TechWeb",
            "ifanr": "爱范儿",
            "bbc": "BBC",
            "nytimes": "纽约时报",
            "washingtonpost": "华盛顿邮报",
            "reuters": "路透社",
            "cnn": "CNN",
            "cnbc": "CNBC",
            "techcrunch": "TechCrunch",
            "mashable": "Mashable",
            "wired": "Wired",
            "bloomberg": "彭博社",
            "forbes": "福布斯",
            "wsj": "华尔街日报",
            "ft": "金融时报"
        }
        for k, v in m.items():
            if k in domain:
                return v
        return domain.split('.')[1].capitalize() if '.' in domain else "未知来源"
    except:
        return "未知来源"

# 新闻源
def get_news_sources():
    return [
        "https://tech.sina.com.cn/rss/it.xml",
        "https://finance.sina.com.cn/rss/finance.xml",
        "https://rsshub.app/36kr/feature",
        "https://www.caixin.com/rss/finance.xml",
        "https://www.yicai.com/rss/finance.xml",
        "https://www.jiemian.com/rss/tech.xml",
        "https://www.thepaper.cn/rss_news.shtml",
        "https://news.ifeng.com/rss/world.xml",
        "https://www.chinanews.com/rss/world-us.xml",
        "https://www.163.com/rss/us.xml",
        "https://news.qq.com/rss/nw4.xml",
        "https://www.sohu.com/rss/us.xml",
        "https://www.zaobao.com/rss/cs.html",
        "https://feeds.appinn.com/appinn/",
        "https://www.solidot.org/index.rss",
        "https://techweb.com.cn/rss/allnews.xml",
        "https://www.ifanr.com/feed",
        "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
        "https://feeds.washingtonpost.com/rss/national",
        "https://www.reuters.com/rssFeed/usNews",
        "https://www.cnn.com/services/rss/rss_us.rss",
        "https://www.bloomberg.com/feeds/news.rss",
        "https://www.forbes.com/feeds/rss",
        "https://feeds.wsj.net/rss/home-page.xml",
        "https://www.ft.com/rss/home/us",
        "https://techcrunch.com/feed/",
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
            for e in feed.entries[:10]:
                title = translate_title(e.title.strip())
                link = e.link.strip()
                pub = e.get('published', '')

                tag = "综合"
                if any(k in title for k in ["AI", "大模型", "芯片", "科技", "技术", "互联网"]):
                    tag = "科技"
                elif any(k in title for k in ["财经", "股市", "金融", "经济", "投资"]):
                    tag = "金融"
                elif any(k in title for k in ["美国", "白宫", "华盛顿", "纽约", "加州"]):
                    tag = "美国"
                elif any(k in title for k in ["国际", "欧洲", "日本", "海外"]):
                    tag = "国际"
                elif any(k in title for k in ["政治", "政策", "选举", "国会"]):
                    tag = "政治"

                item = {"t": title, "l": link, "g": tag, "s": source, "d": pub}
                if tag == "美国":
                    if source in ["中国新闻网", "新浪新闻", "凤凰新闻", "腾讯新闻", "网易新闻", "搜狐新闻", "澎湃新闻", "财新网", "第一财经", "联合早报"]:
                        chinese_us.append(item)
                    else:
                        english_us.append(item)
                else:
                    other.append(item)
            if len(news_list) >= 80:
                break
        except:
            continue

    final = []
    final.extend([i for i in other if i["g"] == "科技"])
    final.extend([i for i in other if i["g"] == "金融"])
    final.extend(chinese_us)
    final.extend(english_us)
    final.extend([i for i in other if i["g"] not in ["科技", "金融"]])

    seen = set()
    out = []
    for x in final:
        if x["t"] not in seen and len(x["t"]) > 5:
            seen.add(x["t"])
            out.append(x)
    return out[:60]

# 生成 HTML（完全修复语法，无冒号报错）
def make_html(data):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')

    nav = '''
<nav style="text-align: center; margin-bottom: 40px; background: #f8f8f8; padding: 15px; border-radius: 8px;">
  <a href="#tech" style="margin: 0 15px; color: #c5a059; font-weight: bold; text-decoration: none; font-size: 14px;">科技</a>
  <a href="#finance" style="margin: 0 15px; color: #c5a059; font-weight: bold; text-decoration: none; font-size: 14px;">金融</a>
  <a href="#us" style="margin: 0 15px; color: #c5a059; font-weight: bold; text-decoration: none; font-size: 14px;">美国</a>
  <a href="#international" style="margin: 0 15px; color: #c5a059; font-weight: bold; text-decoration: none; font-size: 14px;">国际</a>
  <a href="#politics" style="margin: 0 15px; color: #c5a059; font-weight: bold; text-decoration: none; font-size: 14px;">政治</a>
  <a href="#general" style="margin: 0 15px; color: #c5a059; font-weight: bold; text-decoration: none; font-size: 14px;">综合</a>
</nav>
'''

    tech = ''
    finance = ''
    us = ''
    inter = ''
    poli = ''
    gene = ''

    for n in data:
        item = f'''
<div style="margin-bottom: 25px; border-bottom: 1px solid #f2f2f2; padding-bottom: 12px;">
  <div style="font-size: 11px; color: #999; margin-bottom: 5px;">{n['s']} • {n['d'].split('T')[0] if n['d'] else ''}</div>
  <a href="{n['l']}" target="_blank" style="color: #111; font-size: 18px; line-height: 1.5; font-weight: 500; text-decoration: none;">{n['t']}</a>
</div>
'''
        if n['g'] == '科技':
            tech += item
        elif n['g'] == '金融':
            finance += item
        elif n['g'] == '美国':
            us += item
        elif n['g'] == '国际':
            inter += item
        elif n['g'] == '政治':
            poli += item
        else:
            gene += item

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global Briefing</title>
<style>
.category-title {{ font-size: 24px; margin: 40px 0 20px; color: #333; border-left: 4px solid #c5a059; padding-left: 10px; }}
@media (max-width: 600px) {{
  nav a {{ margin: 0 8px; font-size: 12px; }}
  .category-title {{ font-size: 20px; }}
}}
</style>
</head>
<body style="max-width: 800px; margin: auto; padding: 40px 20px; font-family: Georgia, 'Songti SC', serif; background: #fdfdfd; color: #111;">
<header style="text-align: center; margin-bottom: 50px; border-bottom: 4px double #eee; padding-bottom: 20px;">
  <h1 style="font-size: 36px; margin: 0; letter-spacing: -1px; color: #222;">THE GLOBAL BRIEFING</h1>
  <div style="color: #999; font-size: 12px; margin-top: 10px; letter-spacing: 2px;">UPDATE: {time_str} BEIJING</div>
</header>
{nav}
<main>
<section id="tech">
<h2 class="category-title">科技</h2>
{tech if tech else '<div style="color: #999; padding: 20px; text-align: center;">暂无科技新闻</div>'}
</section>
<section id="finance">
<h2 class="category-title">金融</h2>
{finance if finance else '<div style="color: #999; padding: 20px; text-align: center;">暂无金融新闻</div>'}
</section>
<section id="us">
<h2 class="category-title">美国</h2>
{us if us else '<div style="color: #999; padding: 20px; text-align: center;">暂无美国新闻</div>'}
</section>
<section id="international">
<h2 class="category-title">国际</h2>
{inter if inter else '<div style="color: #999; padding: 20px; text-align: center;">暂无国际新闻</div>'}
</section>
<section id="politics">
<h2 class="category-title">政治</h2>
{poli if poli else '<div style="color: #999; padding: 20px; text-align: center;">暂无政治新闻</div>'}
</section>
<section id="general">
<h2 class="category-title">综合</h2>
{gene if gene else '<div style="color: #999; padding: 20px; text-align: center;">暂无综合新闻</div>'}
</section>
</main>
<footer style="text-align: center; margin-top: 80px; color: #ddd; font-size: 10px; border-top: 1px solid #eee; padding-top: 30px;">
© 2026 GLOBAL NEWS • 每小时自动更新
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
