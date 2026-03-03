import requests
import datetime

def get_real_news():
    # 采用金十数据 API 获取实时快讯
    url = "https://api.jin10.com" 
    headers = {"x-app-id": "web", "x-version": "1.0.0"}
    
    news_list = []
    try:
        res = requests.get(url, headers=headers).json()
        for item in res['data']:
            content = item['content'].replace('<br/>', ' ')
            # 简单逻辑分类
            tag = "财经"
            if "AI" in content or "机器人" in content or "芯片" in content: tag = "AI科技"
            elif "美" in content or "俄" in content or "联合国" in content: tag = "国际"
            
            news_list.append({"desc": content, "tag": tag, "time": item['time'].split(' ')[1][:5]})
    except:
        news_list = [{"desc": "暂时无法获取最新资讯，请稍后刷新。", "tag": "系统", "time": "00:00"}]
    return news_list

def generate_html(data):
    now_date = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%Y年%m月%d日')
    now_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%H:%M')
    
    items_html = ""
    for n in data:
        tag_color = "#1a73e8" if n['tag'] == "AI科技" else "#c5a059" if n['tag'] == "财经" else "#5f6368"
        items_html += f"""
        <div class="news-card">
            <div class="meta">
                <span class="tag" style="background: {tag_color}15; color: {tag_color}; border: 1px solid {tag_color}30;">{n['tag']}</span>
                <span class="time">{n['time']}</span>
            </div>
            <div class="content">{n['desc']}</div>
        </div>"""

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>The Global Briefing</title>
        <style>
            :root {{ --primary: #1a1a1a; --accent: #c5a059; --bg: #fdfdfd; }}
            body {{ background: var(--bg); color: var(--primary); font-family: "PingFang SC", "Hiragino Sans GB", serif; margin: 0; line-height: 1.6; }}
            .header {{ text-align: center; padding: 60px 20px 40px; border-bottom: 3px double #ddd; max-width: 800px; margin: 0 auto; }}
            .header h1 {{ font-family: "Georgia", serif; font-size: 42px; margin: 0; letter-spacing: -1px; text-transform: uppercase; }}
            .header .date {{ color: #888; font-size: 14px; margin-top: 10px; text-transform: uppercase; letter-spacing: 2px; }}
            .container {{ max-width: 800px; margin: 40px auto; padding: 0 20px; }}
            .news-card {{ margin-bottom: 40px; transition: 0.3s; position: relative; }}
            .meta {{ display: flex; align-items: center; margin-bottom: 12px; font-size: 12px; font-weight: bold; }}
            .tag {{ padding: 2px 8px; border-radius: 2px; margin-right: 12px; }}
            .time {{ color: #999; }}
            .content {{ font-size: 18px; color: #333; text-align: justify; border-left: 1px solid #eee; padding-left: 20px; }}
            .footer {{ text-align: center; padding: 40px; font-size: 12px; color: #bbb; border-top: 1px solid #eee; }}
            @media (max-width: 600px) {{ .header h1 {{ font-size: 30px; }} .content {{ font-size: 16px; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>THE GLOBAL BRIEFING</h1>
            <div class="date">{now_date} · 发送于北京 {now_time}</div>
        </div>
        <div class="container">
            {items_html}
        </div>
        <div class="footer">
            © 2026 Powered by Gemini AI Intelligence · 实时数据来源于权威财经接口
        </div>
    </body>
    </html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    generate_html(get_real_news())
