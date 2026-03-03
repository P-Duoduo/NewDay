import datetime

# 模拟数据（你可以以后接入真正的 API）
news_data = [
    {"title": "AI 领域重大突破", "desc": "新型大模型效率提升 40%", "tag": "AI"},
    {"title": "全球股市收盘观察", "desc": "科技股领涨，市场情绪乐观", "tag": "财经"}
]

def generate_html():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    items = "".join([f'<div style="margin-bottom:15px; border-bottom:1px solid #eee;">'
                     f'<b style="color:#007bff;">[{n["tag"]}]</b> {n["title"]}<p style="font-size:14px; color:#666;">{n["desc"]}</p></div>' 
                     for n in news_data])
    
    html = f"<html><body style='max-width:800px; margin:auto; padding:20px;'><h1>每日全球热点</h1><p>更新时间：{now}</p><hr>{items}</body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    generate_html()
