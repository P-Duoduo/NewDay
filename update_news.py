import feedparser
import datetime
import ssl

# 解决 GitHub 服务器抓取时的 SSL 证书校验问题
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def get_real_news():
    # 真实可用的 RSS 源（GitHub 环境稳定）
    sources = [
        "https://www.zaobao.com/rss/cn_world.xml",       # 早报 国际
        "https://www.zaobao.com/rss/cn_china.xml",      # 早报 中国
        "https://rsshub.app/163/news/domestic",          # 网易国内
        "https://rsshub.app/163/news/tech",              # 网易科技
    ]
    
    news_list = []
    for url in sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                title = entry.title
                link = entry.link
                
                # 简单分类
                tag = "综合"
                if any(k in title for k in ["AI", "芯片", "科技", "互联网", "算法"]):
                    tag = "AI科技"
                elif any(k in title for k in ["美国", "国际", "全球", "世界", "俄乌", "欧盟"]):
                    tag = "国际"
                elif any(k in title for k in ["财经", "股市", "经济", "金融", "房价"]):
                    tag = "财经"
                
                news_list.append({"t": title, "l": link, "g": tag})
            
            if len(news_list) > 0:
                break  # 抓到一个源就停
        except:
            continue

    # 兜底：Google 新闻（英文）
    if not news_list:
        try:
            r = feedparser.parse("https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans")
            for entry in r.entries[:10]:
                title = entry.title.split(' - ')[0]
                news_list.append({"t": title, "l": entry.link, "g": "实时"})
        except:
            news_list = [{"t": "全球资讯同步中，请稍后再次手动触发运行...", "l": "#", "g": "系统"}]
            
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
        <meta name="viewport" content="width=device-width,initial-scale=1.0">
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

if __name__ == "__main__":
    make_html(get_real_news())
