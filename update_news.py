import feedparser
import datetime
import ssl
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# 解决 SSL 证书问题
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# 翻译配置（Google 翻译 API 兜底，免费可用）
def translate_title(title):
    # 先判断是否包含大量英文（简单规则：英文单词占比超过 50%）
    eng_chars = sum(1 for c in title if c.isalpha())
    total_chars = len([c for c in title if c.strip()])
    if total_chars == 0 or eng_chars / total_chars 
        return title  # 中文占比高，直接返回
    
    try:
        # 调用 Google 翻译 API（免费无 KEY，适合少量翻译）
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={requests.utils.quote(title)}"
        response = requests.get(url, timeout=5)
        result = response.json()[0][0][0]
        return result if result else title
    except:
        return title  # 翻译失败则返回原标题

# 新闻来源名称映射
def get_source_name(url):
    try:
        domain = urlparse(url).netloc
        source_map = {
            "zaobao": "联合早报",
            "appinn": "小众软件",
            "solidot": "Solidot",
            "36kr": "36氪",
            "douban": "豆瓣",
            "chinanews": "中国新闻网",
            "sina": "新浪新闻",
            "ifeng": "凤凰新闻",
            "qq": "腾讯新闻",
            "163": "网易新闻",
            "sohu": "搜狐新闻",
            "thepaper": "澎湃新闻",
            "caixin": "财新网",
            "jiemian": "界面新闻",
            "yicai": "第一财经",
            "techweb": "TechWeb",
            "ifanr": "爱范儿",
            "360doc": "360doc",
            "bbc": "BBC",
            "nytimes": "纽约时报",
            "washingtonpost": "华盛顿邮报",
            "reuters": "路透社",
            "cnn": "CNN",
            "cnbc": "CNBC",
            "techcrunch": "TechCrunch",
            "mashable": "Mashable",
            "wired": "Wired",
            "bloomberg": "彭博社",
            "forbes": "福布斯",
            "wsj": "华尔街日报",
            "ft": "金融时报"
        }
        for key, name in source_map.items():
            if key in domain:
                return name
        return domain.split('.')[1].capitalize() if '.' in domain else "未知来源"
    except:
        return "未知来源"

# 新闻源配置（按优先级排序：中文源在前，英文源在后；科技/金融/美国相关源优先）
def get_news_sources():
    return [
        # 中文核心源（科技/金融/美国相关优先）
        "https://tech.sina.com.cn/rss/it.xml",  # 新浪科技
        "https://finance.sina.com.cn/rss/finance.xml",  # 新浪财经
        "https://rsshub.app/36kr/feature",  # 36氪
        "https://www.caixin.com/rss/finance.xml",  # 财新金融
        "https://www.yicai.com/rss/finance.xml",  # 第一财经
        "https://www.jiemian.com/rss/tech.xml",  # 界面科技
        "https://www.thepaper.cn/rss_news.shtml",  # 澎湃新闻
        "https://news.ifeng.com/rss/world.xml",  # 凤凰国际（含美国）
        "https://www.chinanews.com/rss/world-us.xml",  # 中国新闻网-美国新闻
        "https://www.163.com/rss/us.xml",  # 网易美国新闻
        "https://news.qq.com/rss/nw4.xml",  # 腾讯国际新闻
        "https://www.sohu.com/rss/us.xml",  # 搜狐美国新闻
        "https://www.zaobao.com/rss/cs.html",  # 联合早报
        "https://feeds.appinn.com/appinn/",  # 小众软件
        "https://www.solidot.org/index.rss",  # Solidot
        "https://techweb.com.cn/rss/allnews.xml",  # TechWeb
        "https://www.ifanr.com/feed",  # 爱范儿
        "https://www.360doc.com/rss/finance.xml",  # 360doc财经
        "https://rsshub.app/ifeng/tech",  # 凤凰科技
        "https://rsshub.app/qq/tech",  # 腾讯科技
        
        # 英文源（美国相关）
        "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",  # BBC 美国新闻
        "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",  # 纽约时报-美国
        "https://feeds.washingtonpost.com/rss/national",  # 华盛顿邮报-美国
        "https://www.reuters.com/rssFeed/usNews",  # 路透社-美国新闻
        "https://www.cnn.com/services/rss/rss_us.rss",  # CNN 美国新闻
        "https://www.bloomberg.com/feeds/news.rss",  # 彭博社
        "https://www.forbes.com/feeds/rss",  # 福布斯
        "https://feeds.wsj.net/rss/home-page.xml",  # 华尔街日报
        "https://www.ft.com/rss/home/us",  # 金融时报-美国
        "https://techcrunch.com/feed/",  # TechCrunch
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",  # CNBC
    ]

# 抓取新闻（美国相关新闻优先国内源）
def get_real_news():
    sources = get_news_sources()
    news_list = []
    chinese_us_news = []  # 国内源的美国新闻
    english_us_news = []  # 英文源的美国新闻
    other_news = []       # 其他新闻

    for url in sources:
        try:
            feed = feedparser.parse(url)
            source = get_source_name(url)
            for entry in feed.entries[:10]:  # 每个源取前10条，避免重复
                title = translate_title(entry.title.strip())  # 英文转中文
                link = entry.link.strip()
                pub_date = entry.get('published', '')

                # 分类标签
                tag = "综合"
                if any(k in title for k in ["AI", "大模型", "算法", "芯片", "科技", "Tech", "技术", "互联网", "数码", "电子"]):
                    tag = "科技"
                elif any(k in title for k in ["财经", "股市", "经济", "金融", "Business", "市场", "投资", "基金", "汇率"]):
                    tag = "金融"
                elif any(k in title for k in ["美国", "USA", "American", "白宫", "华盛顿", "纽约", "加州"]):
                    tag = "美国"
                elif any(k in title for k in ["国际", "欧洲", "日本", "World", "Global", "海外"]):
                    tag = "国际"
                elif any(k in title for k in ["政治", "政策", "选举", "国会", "政府"]):
                    tag = "政治"

                news_item = {
                    "t": title,
                    "l": link,
                    "g": tag,
                    "s": source,
                    "d": pub_date
                }

                # 区分国内/英文美国新闻
                if tag == "美国":
                    if source in ["中国新闻网", "新浪新闻", "凤凰新闻", "腾讯新闻", "网易新闻", "搜狐新闻", "联合早报", "澎湃新闻", "财新网", "第一财经"]:
                        chinese_us_news.append(news_item)
                    else:
                        english_us_news.append(news_item)
                else:
                    other_news.append(news_item)

            if len(news_list) >= 80:  # 最多抓取80条新闻
                break

        except Exception as e:
            print(f"抓取 {url} 失败：{str(e)}")
            continue

    # 排序优先级：科技 → 金融 → 国内美国新闻 → 英文美国新闻 → 其他分类
    priority_order = {"科技": 0, "金融": 1, "美国": 2, "国际": 3, "政治": 4, "综合": 5, "实时": 6, "系统": 7}
    # 合并新闻：科技+金融 → 国内美国 → 英文美国 → 其他
    final_news = []
    # 先加科技、金融新闻（按来源优先级）
    final_news.extend([item for item in other_news if item["g"] == "科技"])
    final_news.extend([item for item in other_news if item["g"] == "金融"])
    # 再加美国新闻（国内在前，英文在后）
    final_news.extend(chinese_us_news)
    final_news.extend(english_us_news)
    # 最后加其他分类
    final_news.extend([item for item in other_news if item["g"] not in ["科技", "金融"]])

    # 去重（根据标题去重）
    seen_titles = set()
    unique_news = []
    for item in final_news:
        if item["t"] not in seen_titles and len(item["t"]) > 5:  # 过滤短标题和重复
            seen_titles.add(item["t"])
            unique_news.append(item)

    # 兜底方案
    if not unique_news:
        try:
            r = feedparser.parse("https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans")
            for entry in r.entries[:15]:
                title = translate_title(entry.title.split(' - ')[0])
                unique_news.append({"t": title, "l": entry.link, "g": "实时", "s": "Google News", "d": ""})
        except:
            unique_news = [{"t": "全球资讯同步中，请稍后刷新...", "l": "#", "g": "系统", "s": "系统", "d": ""}]

    return unique_news[:60]  # 最终保留60条新闻

# 生成 HTML（添加分类导航）
def make_html(data):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # 分类导航 HTML
    nav_html = '''
    ="text-align:center; margin-bottom:40px; background:#f8f8f8; padding:15px; border-radius:8px;">
        <a href="#tech" style="margin:0 15px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">科技</a>
        ="#finance" style="margin:0 15px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">金融        " style="margin:0 15px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">美国</a>
        <a href="#international" style="margin:0 15px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">国际</a>
        ="#politics" style="margin:0 15px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">政治
        general" style="margin:0 15px; color:#c5a059; font-weight:bold; text-decoration:none; font-size:14px;">综合 

    # 按分类生成新闻 HTML
    tech_html = ""
    finance_html = ""
    us_html = ""
    international_html = ""
    politics_html = ""
    general_html = ""

    for n in data:
        news_item = f'''
        -bottom:25px; border-bottom:1px solid #f2f2f2; padding-bottom:12px;">
            <div style="font-size:11px; color:#999; margin-bottom:5px;">{n['s']} • {n['d'].split('T')[0] if n['d'] else ''}</div>
            <a href="{n['l']}" target="_blank" style="color:#111; font-size:18px; line-height:1.5; font-weight:500; text-decoration:none;">{n['t']}  if n["g"] == "科技":
            tech_html += news_item
        elif n["g"] == "金融":
            finance_html += news_item
        elif n["g"] == "美国":
            us_html += news_item
        elif n["g"] == "国际":
            international_html += news_item
        elif n["g"] == "政治":
            politics_html += news_item
        elif n["g"] == "综合":
            general_html += news_item

    # 拼接完整 HTML（每个分类加锚点，支持导航跳转）
    full_html = f'''
    
         8">
         name="viewport" content="width=device-width,initial-scale=1.0">
        ing category-title {{ font-size:24px; margin:40px 0 20px; color:#333; border-left:4px solid #c5a059; padding-left:10px; }}
            @media (max-width: 600px) {{
                nav a {{ margin:0 8px; font-size:12px; }}
                .category-title {{ font-size:20px; }}
                a {{ font-size:16px !important; }}
            }}
        >
    
    max-width:800px; margin:auto; padding:40px 20px; font-family:'Georgia', 'Songti SC', serif; background:#fdfdfd; color:#111;">
        :center; margin-bottom:50px; border-bottom:4px double #eee; padding-bottom:20px;">
             style="font-size:36px; margin:0; letter-spacing:-1px; color:#222;">THE GLOBAL BRIEFING            :#999; font-size:12px; margin-top:10px; letter-spacing:2px;">UPDATE: {time_str} BEIJING>
        
        {nav_html}
                    
            tech">
                2 class="category-title">科技                {tech_html if tech_html else 'color:#999; padding:20px; text-align:center;">暂无最新科技新闻
                        
            finance">
                2 class="category-title">金融                {finance_html if finance_html else 'color:#999; padding:20px; text-align:center;">暂无最新金融新闻
                        
            us">
                2 class="category-title">美国                {us_html if us_html else 'color:#999; padding:20px; text-align:center;">暂无最新美国新闻
                        
            international">
                2 class="category-title">国际                {international_html if international_html else 'color:#999; padding:20px; text-align:center;">暂无最新国际新闻
                        
            politics">
                <h2 class="category-title">政治
                {politics_html if politics_html else ' style="color:#999; padding:20px; text-align:center;">暂无最新政治新闻>'}
            >
            分类 -->
             id="general">
                -title">综合>
                {general_html if general_html else ' style="color:#999; padding:20px; text-align:center;">暂无最新综合新闻>'}
            >
        
        text-align:center; margin-top:80px; color:#ddd; font-size:10px; border-top:1px solid #eee; padding-top:30px;">
            © 2026 GLOBAL NEWS TERMINAL • 每小时自动更新
        </footer>
    </body>
    >'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"✅ 新闻已更新：{time_str} • 共 {len(data)} 条")

# 执行入口（修复参数传递问题）
if __name__ == "__main__":
    news_data = get_real_news()
    make_html(news_data)

