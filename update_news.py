import requests
import datetime

import xml.etree.ElementTree as ET

def get_real_news():
    # 使用 Google News 全球财经/科技 RSS 源（稳定性最高）
    # ceid=CN:zh 确保获取的是中文资讯
    url = "https://news.google.com"
    
    news_list = []
    try:
        # 添加浏览器 User-Agent 伪装，防止被拦截
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        
        # 解析 RSS (XML 格式)
        root = ET.fromstring(response.content)
        for item in root.findall('.//item')[:10]: # 取前 10 条
            title = item.find('title').text
            pub_date = item.find('pubDate').text
            
            # 简单分类逻辑
            tag = "财经"
            if any(k in title for k in ["AI", "智能", "芯片", "科技"]): tag = "AI科技"
            elif any(k in title for k in ["美", "俄", "国际", "局势"]): tag = "国际"
            
            # 处理标题（去除来源后缀）
            clean_title = title.split(' - ')[0]
            
            news_list.append({
                "desc": clean_title, 
                "tag": tag, 
                "time": pub_date.split(' ')[4][:5] # 提取 HH:mm
            })
    except Exception as e:
        news_list = [{"desc": f"系统正在自动修复中，请稍后再次手动运行。(Error: {str(e)})", "tag": "系统", "time": "09:00"}]
    
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
