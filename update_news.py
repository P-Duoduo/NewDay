import requests
import datetime
import re

def get_real_news():
    # 备选源列表：1.路透社 2.华尔街日报 3.联合早报 (均为镜像接口以确保稳定性)
    urls = [
        "https://rsshub.app",
        "https://rsshub.app",
        "https://rsshub.rssforever.com"
    ]
    
    news_list = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                # 使用正则表达式提取标题和链接，这种方式最稳，不会报 XML 解析错误
                titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', response.text)
                links = re.findall(r'<link>(.*?)</link>', response.text)
                
                # 如果 CDATA 提取失败，尝试普通标签提取
                if not titles:
                    titles = re.findall(r'<title>(.*?)</title>', response.text)
                
                # 过滤掉频道标题（通常是第一个）
                for i in range(1, min(len(titles), 12)):
                    t = titles[i].strip()
                    l = links[i].strip() if i < len(links) else "#"
                    
                    # 智能分类
                    tag = "国际"
                    if any(k in t for k in ["AI", "芯片", "科技", "智能", "机器人"]): tag = "AI科技"
                    elif any(k in t for k in ["股", "经", "汇", "财", "金", "银行"]): tag = "财经"
                    
                    news_list.append({"title": t, "link": l, "tag": tag})
                
                if news_list: break # 只要有一个源成功抓到数据，就停止循环
        except Exception as e:
            print(f"尝试源 {url} 失败: {e}")
            continue

    if not news_list:
        news_list = [{"title": "全球资讯同步中，请稍后手动刷新 Action 运行...", "link": "#", "tag": "系统"}]
    return news_list

def generate_html(data):
    # 处理北京时间
    now = datetime.datetime.now() + datetime.timedelta(hours=8)
    date_str = now.strftime('%Y年%m月%d日')
    time_str = now.strftime('%H:%M')
    
    items_html = ""
    for n in data:
        tag_color = "#1a73e8" if n['tag'] == "AI科技" else "#c5a059" if n['tag'] == "财经" else "#5f6368"
        items_html += f"""
        <a href="{n['link']}" target="_blank" class="news-card-link">
            <div class="news-card">
                <div class="meta">
                    <span class="tag" style="background: {tag_color}15; color: {tag_color}; border: 1px solid {tag_color}30;">{n['tag']}</span>
                    <span class="arrow">READ MORE →</span>
                </div>
                <div class="content">{n['title']}</div>
            </div>
        </a>"""

    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>The Global Briefing</title>
        <style>
            :root {{ --primary: #1a1a1a; --accent: #c5a059; --bg: #fdfdfd; }}
            body {{ background: var(--bg); color: var(--primary); font-family: "Georgia", "PingFang SC", serif; margin: 0; line-height: 1.6; }}
            .header {{ text-align: center; padding: 60px 20px 40px; border-bottom: 3px double #ddd; max-width: 800px; margin: 0 auto; }}
            .header h1 {{ font-size: 42px; margin: 0; letter-spacing: -1px; text-transform: uppercase; font-weight: 900; }}
            .header .date {{ color: #888; font-size: 13px; margin-top: 10px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }}
            .container {{ max-width: 800px; margin: 40px auto; padding: 0 20px; min-height: 600px; }}
            .news-card-link {{ text-decoration: none; color: inherit; display: block; }}
            .news-card {{ margin-bottom: 35px; padding-bottom: 25px; border-bottom: 1px solid #eee; transition: 0.2s; }}
            .news-card:hover {{ opacity: 0.7; }}
            .meta {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 11px; font-family: sans-serif; font-weight: bold; }}
            .tag {{ padding: 2px 8px; border-radius: 2px; }}
            .arrow {{ color: #bbb; letter-spacing: 1px; }}
            .content {{ font-size: 20px; color: #111; text-align: justify; font-weight: 500; line-height: 1.4; }}
            .footer {{ text-align: center; padding: 60px 40px; font-size: 11px; color: #bbb; border-top: 1px solid #eee; letter-spacing: 1px; }}
            @media (max-width: 600px) {{ .header h1 {{ font-size: 28px; }} .content {{ font-size: 17px; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>THE GLOBAL BRIEFING</h1>
            <div class="date">{date_str} · UPDATE AT {time_str} BEIJING</div>
        </div>
        <div class="container">
            {items_html}
        </div>
        <div class="footer">
            © 2026 POWERED BY GEMINI AI · DATA FROM WORLDWIDE FINANCIAL TERMINALS
        </div>
    </body>
    </html>"""
    
    with open("index.html", "w", "utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    generate_html(get_real_news())
