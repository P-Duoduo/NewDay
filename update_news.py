import feedparser
import datetime
import ssl
import time
import schedule

# 解决 SSL 证书问题
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def get_real_news():
    # 大量稳定 RSS 新闻源
    sources = [
        # 中文
        "https://www.zaobao.com/rss/cs.html",
        "https://feeds.appinn.com/appinn/",
        "https://www.solidot.org/index.rss",
        "https://rsshub.app/36kr/feature",
        "https://www.douban.com/feed/review/book",
        "https://www.chinanews.com.com/rss/scroll-news.xml",
        "https://tech.sina.com.cn/rss/it.xml",
        "https://finance.sina.com.cn/rss/finance.xml",
        
        # 英文国际
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.washingtonpost.com/rss/national",
        "https://www.reuters.com/rssFeed/businessNews",
        "https://www.reuters.com/rssFeed/technologyNews",
        "https://www.cnn.com/services/rss/rss_topstories.rss",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://techcrunch.com/feed/",
        "https://mashable.com/feed/",
        "https://www.wired.com/feed/rss",
    ]

    news_list = []
    for url in sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                title = entry.title
                link = entry.link

                tag = "综合"
                if any(k in title for k in ["AI", "大模型", "算法", "芯片", "科技", "Tech", "技术", "互联网"]):
                    tag = "科技"
                elif any(k in title for k in ["财经", "股市", "经济", "金融", "Business", "市场", "投资"]):
                    tag = "金融"
                elif any(k in title for k in ["国际", "美国", "欧洲", "日本", "World", "Global"]):
                    tag = "国际"
                elif any(k in title for k in ["政治", "政策", "选举", "国会"]):
                    tag = "政治"

                news_list.append({"t": title, "l": link, "g": tag})

            if len(news_list) >= 40:
                break

        except Exception:
            continue

    # 兜底 Google News
    if not news_list:
        try:
            r = feedparser.parse("https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans")
            for entry in r.entries[:15]:
                title = entry.title.split(' - ')[0]
                news_list.append({"t": title, "l": entry.link, "g": "实时"})
        except Exception:
            news_list = [{"t": "全球资讯同步中，请稍后...", "l": "#", "g": "系统"}]

    # 🔴 关键：科技、金融放最前面，然后是其他
    priority_order = {"科技": 0, "金融": 1, "综合": 2, "国际": 3, "政治": 4, "实时": 5, "系统": 6}
    news_list.sort(key=lambda x: priority_order.get(x["g"], 99))

    return news_list

def make_html(data):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')

    items_html = ""
    for n in data:
        items_html += f'''
        <div style="margin-bottom:30px; border-bottom:1px solid #f2f2f2; padding-bottom:15px;">
            <div style="font-size:11px; color:#c5a059; font-weight:bold; margin-bottom:8px; letter-spacing:1px;">[{n['g']}]</div>
            <a href="{n['l']}" target="_blank" style="color:#111; font-size:20px; line-height:1.5; font-weight:500; text-decoration:none;">{n['t']}</a>
        </div>'''

    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale1.0">
        <title>Global Briefing</title>
    </head>
    <body style="max-width:750px; margin:auto; padding:60px 20px; font-family:'Georgia', serif; background:#fdfdfd; color:#111;">
        <header style="text-align:center; margin-bottom:60px; border-bottom:4px double #eee; padding-bottom:20px;">
            <h1 style="font-size:40px; margin:0; letter-spacing:-1px;">THE GLOBAL BRIEFING</h1>
            <div style="color:#999; font-size:12px; margin-top:10px; letter-spacing:2px;">UPDATE: {time_str} BEIJING</div>
        </header>
        <main>{items_html}</main>
        <footer style="text-align:center; margin-top:100px; color:#ddd; font-size:10px; border-top:1px solid #eee; padding-top:40px;">© 2026 GLOBAL NEWS TERMINAL</footer>
    </body>
    </html>'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"✅ 新闻已更新：{time_str}")

# 定时任务
def job():
    news = get_real_news()
    make_html(news)

if __name__ == "__main__":
    job()
    schedule.every(1).hours.do(job)
    print("⏰ 已启动每小时定时更新，按 Ctrl+C 停止")
    while True:
        schedule.run_pending()
        time.sleep(60)
