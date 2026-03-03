import requests
import datetime
import xml.etree.ElementTree as ET

def get_news():
    # 使用 Google News 官方标准的 RSS 接口，这是目前全球最稳定的新闻源
    url = "https://news.google.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    news_list = []
    
    try:
        # 发送请求获取 XML 数据
        response = requests.get(url, headers=headers, timeout=25)
        # 使用 XML 树状解析器，比正则表达式更精准
        root = ET.fromstring(response.content)
        
        # 遍历 XML 中的 item 节点（每个 item 代表一条新闻）
        for item in root.findall('.//item')[:15]:
            title_raw = item.find('title').text
            link = item.find('link').text
            
            # 清理标题：去掉末尾的来源后缀（例如 " - 华尔街日报"）
            clean_title = title_raw.rsplit(' - ', 1)[0]
            
            # 智能分类标签
            tag = "国际"
            if any(k in title_raw for k in ["AI", "智能", "芯片", "机器人", "大模型"]):
                tag = "AI科技"
            elif any(k in title_raw for k in ["股", "经", "财", "金", "美联储", "汇率"]):
                tag = "财经"
            
            news_list.append({"t": clean_title, "l": link, "g": tag})
            
    except Exception as e:
        # 如果抓取彻底失败，显示一条错误提示
        news_list = [{"t": f"正在尝试重新同步实时资讯 (Error: {str(e)})", "l": "#", "g": "系统"}]
        
    return news_list

def make_html(data):
    # 计算北京时间 (GitHub 服务器默认是 UTC，需要加 8 小时)
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # 构造新闻列表的 HTML 块
    items_html = ""
    for n in data:
        items_html += f"""
        <div style="margin-bottom:35px; border-bottom:1px solid #f0f0f0; padding-bottom:18px;">
            <div style="font-size:11px; color:#c5a059; font-weight:bold; margin-bottom:10px; letter-spacing:1px; text-transform:uppercase;">[{n['g']}]</div>
            <a href="{n['l']}" target="_blank" style="text-decoration:none; color:#111; font-size:22px; font-weight:500; line-height:1.4; display:block; transition:0.2s;">{n['t']}</a>
        </div>"""
    
    # 完整的网页模板
    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1.0">
        <title>The Global Briefing | 全球简报</title>
    </head>
    <body style="max-width:800px; margin:auto; padding:60px 25px; font-family:'Georgia', 'PingFang SC', serif; background:#fdfdfd; color:#111; -webkit-font-smoothing: antialiased;">
        <header style="text-align:center; margin-bottom:60px;">
            <h1 style="font-size:42px; border-bottom:3px double #ddd; padding-bottom:15px; margin:0; letter-spacing:-1px;">THE GLOBAL BRIEFING</h1>
            <div style="color:#999; font-size:12px; letter-spacing:2px; margin-top:15px; text-transform:uppercase;">UPDATE: {time_str} BEIJING</div>
        </header>
        
        <main>
            {items_html}
        </main>
        
        <footer style="text-align:center; margin-top:100px; color:#bbb; font-size:11px; letter-spacing:1px; border-top:1px solid #eee; padding-top:40px;">
            © 2026 POWERED BY GEMINI AI · AUTOMATED NEWS TERMINAL
        </footer>
    </body>
    </html>"""
    
    # 将生成的 HTML 写入文件
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    # 执行抓取并生成网页
    news_data = get_news()
    make_html(news_data)
