import requests
import datetime
import re

def get_news():
    # 使用最稳定的源
    url = "https://news.google.com"
    news_list = []
    try:
        r = requests.get(url, timeout=20)
        # 用最简单的正则匹配标题和链接
        titles = re.findall(r'<title>(.*?)</title>', r.text)
        links = re.findall(r'<link>(.*?)</link>', r.text)
        for i in range(1, min(len(titles), 15)):
            t = titles[i].split(' - ')[0] # 去掉来源名
            l = links[i]
            tag = "财经"
            if "AI" in t or "科技" in t: tag = "AI科技"
            news_list.append({"t": t, "l": l, "g": tag})
    except:
        news_list = [{"t": "正在同步全球资讯...", "l": "#", "g": "系统"}]
    return news_list

def make_html(data):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = now.strftime('%Y-%m-%d %H:%M')
    items = ""
    for n in data:
        items += f'<div style="margin-bottom:25px;"><span style="color:#c5a059;font-weight:bold;font-size:12px;">[{n["g"]}]</span><br><a href="{n["l"]}" target="_blank" style="text-decoration:none;color:#111;font-size:20px;font-weight:500;">{n["t"]}</a></div>'
    
    html = f"""
    <html>
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>Global Briefing</title></head>
    <body style="max-width:700px;margin:auto;padding:40px;font-family:serif;background:#fdfdfd;color:#111;">
        <h1 style="text-align:center;font-size:36px;border-bottom:3px double #eee;padding-bottom:20px;">THE GLOBAL BRIEFING</h1>
        <p style="text-align:center;color:#999;font-size:12px;">UPDATE: {time_str} BEIJING</p>
        <div style="margin-top:40px;">{items}</div>
        <div style="text-align:center;margin-top:60px;color:#ccc;font-size:10px;">© 2026 AI AUTOMATION</div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    make_html(get_news())
