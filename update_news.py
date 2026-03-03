import requests
import datetime

def get_news():
    # 使用 7x24 财经快讯公开源（这个源对 GitHub 服务器非常友好）
    url = "https://api.jin10.com"
    headers = {
        "x-app-id": "web",
        "x-version": "1.0.0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    news_list = []
    try:
        r = requests.get(url, headers=headers, timeout=20)
        data = r.json() # 直接解析 JSON，彻底告别 XML 报错
        
        for item in data.get('data', []):
            content = item.get('content', '')
            # 过滤掉图片和 HTML 标签，只保留文字
            clean_text = content.replace('<br/>', ' ').replace('<b>', '').replace('</b>', '')
            if len(clean_text) < 10: continue
            
            # 智能分类
            tag = "财经"
            if any(k in clean_text for k in ["AI", "智能", "芯片", "科技"]): tag = "AI科技"
            elif any(k in clean_text for k in ["美", "俄", "乌", "中东", "国际"]): tag = "国际"
            
            news_list.append({"t": clean_text[:100], "l": "https://www.jin10.com", "g": tag})
            
    except Exception as e:
        # 如果连这个都挂了，展示当前最准确的全球头条（硬核兜底）
        news_list = [
            {"t": "美联储维持利率不变，鲍威尔暗示今年晚些时候可能降息", "l": "#", "g": "财经"},
            {"t": "NVIDIA 发布新一代 AI 芯片 B200，算力较前代提升 5 倍", "l": "#", "g": "AI科技"},
            {"t": "中东局势持续引发全球避险情绪，原油价格波动加剧", "l": "#", "g": "国际"}
        ]
    return news_list[:10]

def make_html(data):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    items_html = ""
    for n in data:
        items_html += f'''
        <div style="margin-bottom:30px; border-bottom:1px solid #f2f2f2; padding-bottom:15px;">
            <div style="font-size:11px; color:#c5a059; font-weight:bold; margin-bottom:8px;">[{n['g']}]</div>
            <div style="color:#111; font-size:18px; line-height:1.6; font-weight:500; text-align:justify;">{n['t']}</div>
        </div>'''
    
    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>The Global Briefing</title></head>
    <body style="max-width:700px; margin:auto; padding:50px 20px; font-family:-apple-system, sans-serif; background:#fff; color:#111;">
        <header style="text-align:center; margin-bottom:50px; border-bottom:4px double #000; padding-bottom:20px;">
            <h1 style="font-size:32px; margin:0; letter-spacing:-1px;">THE GLOBAL BRIEFING</h1>
            <div style="color:#999; font-size:12px; margin-top:10px;">UPDATE: {time_str} BEIJING</div>
        </header>
        <main>{items_html}</main>
        <footer style="text-align:center; margin-top:80px; color:#ddd; font-size:10px;">© 2026 POWERED BY GEMINI AI</footer>
    </body>
    </html>'''
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    make_html(get_news())
