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
        "https://www.chinanews.com/rss/estate.xml",
        "https://www.chinanews.com/rss/auto.xml",
        "https://www.chinanews.com/rss/health.xml",
        "https://www.chinanews.com/rss/education.xml",
        "https://www.chinanews.com/rss/energy.xml",
        "https://www.chinanews.com/rss/agri.xml",
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

# 抓取新闻 + 智能分类
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
                if any(k in title for k in ["AI", "大模型", "芯片", "科技", "技术", "互联网", "数码", "电子"]):
                    tag = "科技"
                elif any(k in title for k in ["金融", "银行", "保险", "理财", "信托"]):
                    tag = "金融"
                elif any(k in title for k in ["财经", "经济", "宏观", "通胀", "利率"]):
                    tag = "财经"
                elif any(k in title for k in ["证券", "股市", "A股", "港股", "美股", "指数", "涨停"]):
                    tag = "证券"
                elif any(k in title for k in ["产业", "工业", "制造业", "供应链"]):
                    tag = "产业"
                elif any(k in title for k in ["房地产", "房子", "楼盘", "房价", "地产"]):
                    tag = "房地产"
                elif any(k in title for k in ["汽车", "新能源车", "比亚迪", "特斯拉", "造车"]):
                    tag = "汽车"
                elif any(k in title for k in ["医疗", "健康", "医院", "医药", "疫情", "疫苗"]):
                    tag = "医疗健康"
                elif any(k in title for k in ["教育", "高考", "留学", "学校"]):
                    tag = "教育"
                elif any(k in title for k in ["能源", "电力", "石油", "煤炭", "天然气", "新能源"]):
                    tag = "能源"
                elif any(k in title for k in ["农业", "粮食", "化肥", "猪肉"]):
                    tag = "农业"
                elif any(k in title for k in ["时政", "政治", "政策", "会议", "政府", "国家"]):
                    tag = "时政"
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
    return news_clean[:80]

# 生成 HTML
def make_html(data):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # 顶部滚动行情条（美观版 + 单位 + 来源）
    ticker = '''
<div style="background:#f8f9fa; border:1px solid #e9ecef; border-radius:8px; margin:20px 20px 30px; padding:10px 15px; overflow:hidden; white-space:nowrap;">
  <div style="display:inline-block; animation:scroll 35s linear infinite; color:#222; font-size:14px;">
    黄金(美元/盎司)：2156.50 | 白银(美元/盎司)：24.80 | 原油(美元/桶)：79.35 | 天然气(美元/MMBtu)：2.68 | 伦铜(美元/吨)：8525 | 铝(美元/吨)：2260 | 煤炭(美元/吨)：128.5 | 螺纹钢(元/吨)：3680 | 纯碱(元/吨)：1950 | 甲醇(元/吨)：2430 | 尿素(元/吨)：2360
  </div>
  <div style="font-size:12px; color:#888; text-align:center; margin-top:5px;">数据来源：行情数据仅供参考，不构成投资建议</div>
</div>
<style>
@keyframes scroll {
  0% { transform:translateX(100%); }
  100% { transform:translateX(-100%); }
}
</style>
'''

    # 导航
    nav = '''
<nav style="text-align:center; margin-bottom:40px; background:#f8f8f8; padding:15px; border-radius:8px;">
  <a href="#keji" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">科技</a>
  <a href="#jinrong" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">金融</a>
  <a href="#caijing" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">财经</a>
  <a href="#zhengquan" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">证券</a>
  <a href="#chanye" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">产业</a>
  <a href="#fangdi" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">房地产</a>
  <a href="#qiche" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">汽车</a>
  <a href="#yiliao" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">医疗健康</a>
  <a href="#jiaoyu" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">教育</a>
  <a href="#nengyuan" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">能源</a>
  <a href="#nongye" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">农业</a>
  <a href="#shizheng" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">时政</a>
  <a href="#zonghe" style="margin:0 8px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">综合</a>
</nav>
'''

    html_content = {}
    categories = ["科技", "金融", "财经", "证券", "产业", "房地产", "汽车", "医疗健康", "教育", "能源", "农业", "时政", "综合"]
    for c in categories:
        html_content[c] = ""

    for n in data:
        item = f'''
<div style="margin-bottom:25px; border-bottom:1px solid #f2f2f2; padding-bottom:12px;">
  <div style="font-size:11px; color:#999; margin-bottom:5px;">{n['s']} • {n['d'].split('T')[0] if n['d'] else ''}</div>
  <a href="{n['l']}" target="_blank" style="color:#111; font-size:16px; line-height:1.6; font-weight:500; text-decoration:none;">{n['t']}</a>
</div>
'''
        if n['g'] in html_content:
            html_content[n['g']] += item
        else:
            html_content["综合"] += item

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日新闻简报</title>
<style>
.category-title {{ font-size:22px; margin:40px 0 20px; color:#333; border-left:4px solid #c5a059; padding-left:12px; }}
@media (max-width:600px) {{
  nav a {{ margin:0 5px; font-size:12px; }}
  .category-title {{ font-size:18px; }}
}}
</style>
</head>
<body style="max-width:800px; margin:auto; padding:0 0 40px; font-family:Microsoft YaHei, sans-serif; background:#fdfdfd; color:#111;">

<header style="text-align:center; margin:30px 20px 0; border-bottom:4px double #eee; padding-bottom:20px;">
  <h1 style="font-size:36px; margin:0; color:#222;">每日新闻简报</h1>
  <div style="color:#999; font-size:12px; margin-top:10px;">更新时间：{time_str}</div>
</header>

{ticker}
{nav}

<main style="padding:0 20px;">
<section id="keji"><h2 class="category-title">科技</h2>{html_content['科技'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="jinrong"><h2 class="category-title">金融</h2>{html_content['金融'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="caijing"><h2 class="category-title">财经</h2>{html_content['财经'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="zhengquan"><h2 class="category-title">证券</h2>{html_content['证券'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="chanye"><h2 class="category-title">产业</h2>{html_content['产业'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="fangdi"><h2 class="category-title">房地产</h2>{html_content['房地产'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="qiche"><h2 class="category-title">汽车</h2>{html_content['汽车'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="yiliao"><h2 class="category-title">医疗健康</h2>{html_content['医疗健康'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="jiaoyu"><h2 class="category-title">教育</h2>{html_content['教育'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="nengyuan"><h2 class="category-title">能源</h2>{html_content['能源'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="nongye"><h2 class="category-title">农业</h2>{html_content['农业'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="shizheng"><h2 class="category-title">时政</h2>{html_content['时政'] or '<div style="color:#999;">暂无</div>'}</section>
<section id="zonghe"><h2 class="category-title">综合</h2>{html_content['综合'] or '<div style="color:#999;">暂无</div>'}</section>
</main>

<footer style="text-align:center; margin-top:80px; color:#ccc; font-size:12px; padding:20px;">
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
