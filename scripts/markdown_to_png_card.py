import re
from bs4 import BeautifulSoup
import markdown
import os
import sys
from datetime import datetime
import random
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    print("Markdown content (first 500 characters):")
    print(content[:500])
    if content.strip().startswith('<!DOCTYPE html>'):
        print("Error: The file appears to be HTML, not Markdown.")
        return None
    return content

def parse_product_hunt_items(markdown_content):
    product_sections = re.split(r'\n## ', markdown_content)[1:]  # 跳过标题
    products = []
    print(f"Found {len(product_sections)} product sections")
    for section in product_sections[:24]:  # 只处理前24个产品
        lines = section.strip().split('\n')
        product = {}
        for i, line in enumerate(lines):
            if i == 0:  # 第一行是标题和链接
                match = re.search(r'\[(.*?)\]\((.*?)\)', line)
                if match:
                    product['name'] = match.group(1).split('. ', 1)[-1]
                    product['url'] = match.group(2)
            elif line.startswith('!['):  # 图片行
                match = re.search(r'!\[.*?\]\((.*?)\)', line)
                if match:
                    product['image'] = match.group(1)
            elif line.startswith('**标语**：'):
                product['tagline'] = line.replace('**标语**：', '').strip()
            elif line.startswith('**介绍**：'):
                product['description'] = line.replace('**介绍**：', '').strip()
            elif line.startswith('**票数**:'):
                product['votes'] = line.replace('**票数**: ', '').strip()
            elif line.startswith('**关键词**：'):
                keywords = line.replace('**关键词**：', '').strip().split(', ')
                product['keywords'] = ' '.join([f"#{keyword.strip()}" for keyword in keywords])
        
        if all(key in product for key in ['name', 'url', 'image', 'tagline', 'description', 'votes', 'keywords']):
            products.append(product)
        else:
            print(f"Skipped a product due to missing information: {product}")
    
    print(f"Successfully parsed {len(products)} products")
    return products[:24]  # 确保返回24个产品

def create_html_card(product):
    card_html = f"""
    <div class="card">
        <div class="votes-badge">{product['votes']}</div>
        <div class="card-inner">
            <img src="{product['image']}" alt="{product['name']}" class="product-image">
            <h2><a href="{product['url']}" target="_blank">{product['name']}</a></h2>
            <p class="tagline">{product['tagline']}</p>
            <p class="description">{product['description']}</p>
            <div class="keywords">{product['keywords']}</div>
        </div>
    </div>
    """
    return card_html

def generate_pastel_color():
    r = random.randint(200, 255)
    g = random.randint(200, 255)
    b = random.randint(200, 255)
    return f"rgb({r}, {g}, {b})"

def generate_rainbow_colors(num_colors=7):
    return [f"hsl({i * 360 / num_colors}, 100%, 50%)" for i in range(num_colors)]

def create_html_page(products, date):
    rows = [products[i:i+6] for i in range(0, len(products), 6)]
    
    cards_html = ""
    for i, row in enumerate(rows):
        direction = "normal" if i % 2 == 0 else "reverse"
        cards_html += f"""
        <div class="scroll-container" data-row="{i}">
            <div class="scroll-row" style="animation-direction: {direction};">
                {''.join([create_html_card(product) for product in row * 8])}
            </div>
        </div>
        """
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 构建图片的相对路径
    contact_img_path = os.path.relpath(os.path.join(project_root, 'img', 'contact.jpg'), 
                                       os.path.join(project_root, 'website_daily'))
    
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Hot | {date}</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
        <link rel="alternate" type="application/rss+xml" title="Product Hunt Daily Hot RSS Feed" href="feed.xml">
        <style>
            :root {{
                --background-color: #f7f7f7;
                --text-color: #333333;
                --accent-color: #0066cc;
                --card-background: #ffffff;
                --card-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            body {{
                font-family: 'Poppins', sans-serif;
                background-color: var(--background-color);
                color: var(--text-color);
                margin: 0;
                padding: 0;
                line-height: 1.4;
                overflow-x: hidden;
            }}
            header {{
                background-color: #ffffff;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                padding: 0.5rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .brand h1 {{
                font-size: 24px;
                font-weight: 600;
                color: #333;
                margin: 0;
            }}
            nav ul {{
                list-style-type: none;
                padding: 0;
                margin: 0;
                display: flex;
                align-items: center;
            }}
            nav ul li {{
                margin-left: 1.5rem;
            }}
            nav ul li:first-child {{
                margin-left: 0;
            }}
            nav ul li a {{
                text-decoration: none;
                color: var(--text-color);
                font-size: 16px;
                font-weight: 400;
            }}
            .rss-icon {{
                width: 20px;
                height: 20px;
                vertical-align: middle;
                margin-right: 5px;
            }}
            .main-content {{
                padding: 1rem 2rem;  /* 减少上下padding */
            }}
            .title-container {{
                text-align: center;
                position: relative;
                padding: 10px 0;  /* 减少上下padding */
                margin-bottom: 1rem;  /* 减少底部margin */
            }}
            .title-container h1 {{
                font-size: 48px;  /* 增加页面标题的字体大小 */
                margin: 0 0 10px 0;
                font-weight: 700;  /* 加粗字体 */
                color: #333;  /* 深色字体，提高可读性 */
            }}
            .blue-line {{
                width: 50px;
                height: 3px;
                background-color: #0066cc;
                margin: 10px auto;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: scaleX(1); }}
                50% {{ transform: scaleX(1.5); }}
                100% {{ transform: scaleX(1); }}
            }}
            .date {{
                font-size: 18px;
                color: #666;
                text-align: center;
                margin-bottom: 1rem;  /* 减少底部margin */
            }}
            .robot {{
                position: absolute;
                font-size: 36px;
                transition: all 0.2s ease;
                user-select: none;
            }}
            .scroll-container {{
                overflow: hidden;
                margin-bottom: 2rem;
                width: 100%;
            }}
            .scroll-row {{
                display: flex;
                animation: scroll 180s linear infinite;  /* 增加动画时间减慢速度 */
                width: 800%;
            }}
            .card {{
                flex: 0 0 4.166%;  /* 100% / 24, 使卡片宽度约为4% */
                max-width: 4.166%;
                padding: 0.5rem;
                box-sizing: border-box;
                position: relative;
                margin-top: 1rem;  /* 为票数标签留出空间 */
            }}
            .card-inner {{
                background-color: var(--card-background);
                border-radius: 12px;
                box-shadow: var(--card-shadow);
                overflow: hidden;
                height: 100%;
                display: flex;
                flex-direction: column;
                position: relative;  /* 确保内容不会被票数标签遮挡 */
            }}
            .product-image {{
                width: 100%;
                height: 180px;
                object-fit: cover;
            }}
            h2 {{
                font-size: 16px;  /* 调整标题字体大小 */
                font-weight: 600;
                margin: 0.5rem 0;
                padding: 0 1rem;
            }}
            a {{
                color: var(--text-color);
                text-decoration: none;
                transition: color 0.3s ease;
            }}
            a:hover {{
                color: var(--accent-color);
            }}
            p {{
                margin: 0.25rem 0;
                font-size: 14px;
                padding: 0 1rem;
            }}
            .tagline {{
                text-decoration: underline wavy red;
                text-decoration-thickness: 1px;
                text-underline-offset: 3px;
                margin-bottom: 10px;
                font-weight: 500;
                color: #333;
            }}
            .description {{
                flex-grow: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-line-clamp: 3;
                -webkit-box-orient: vertical;
                font-size: 12px;  /* 调整文字大小 */
            }}
            .votes {{
                font-weight: 600;
                color: var(--accent-color);
            }}
            .keywords, .time {{
                font-size: 10px;  /* 调整关键词字体大小 */
                color: #888;
            }}
            @keyframes scroll {{
                0% {{ transform: translateX(0); }}
                100% {{ transform: translateX(-87.5%); }}  /* -7/8 of the total width */
            }}
            @keyframes float {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
            footer {{
                text-align: center;
                padding: 20px 0;
                background-color: #f0f0f0;
                color: #666;
                font-size: 14px;
                margin-top: 2rem;
            }}
            footer p {{
                margin: 0;
            }}
            .votes-badge {{
                position: absolute;
                top: -0.5rem;  /* 调整位置，使与卡片有约1/3重叠 */
                left: 0.5rem;
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                z-index: 2;  /* 确保票数标签在最上层 */
            }}
            .scroll-container:hover .scroll-row {{
                animation-play-state: paused;
            }}
            
            .keywords {{
                margin-top: 10px;
                padding-right: 10px;  /* 添加左侧内边距 */
                text-align: right;  /* 将标签靠右对齐 */
            }}
            .keyword {{
                display: inline-block;
                background-color: #f0f0f0;
                color: #333;
                padding: 2px 8px;
                margin-left: 10px;  /* 改为左距，使标签之间有间隔 */
                margin-bottom: 10px;
                border-radius: 12px;
                font-size: 12px;
            }}
            
            .scroll-container, .card, .card-inner, .card-inner * {{
                user-select: none;
                -webkit-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
            }}
            
            .about-me, .contact {{
                position: relative;
                display: inline-block;
            }}
            
            .tooltip {{
                visibility: hidden;
                background-color: #555;
                color: #fff;
                text-align: left;
                border-radius: 6px;
                padding: 10px;
                position: absolute;
                z-index: 1;
                top: 100%;
                right: 0;
                margin-top: 5px;
                opacity: 0;
                transition: opacity 0.3s;
            }}
            
            .about-me .tooltip {{
                width: 250px;
            }}
            
            .contact .tooltip {{
                width: 200px;  /* 增加宽度 */
                padding: 15px;  /* 增加内边距 */
            }}
            
            .tooltip::after {{
                content: "";
                position: absolute;
                bottom: 100%;
                right: 10%;
                margin-right: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: transparent transparent #555 transparent;
            }}
            
            .about-me:hover .tooltip, .contact:hover .tooltip {{
                visibility: visible;
                opacity: 1;
            }}
            
            .qr-code {{
                width: 100%;  /* 使图片填满容器宽度 */
                height: auto;  /* 保持宽比 */
                max-width: 180px;  /* 设置最大宽度 */
                display: block;  /* 块级显示 */
                margin: 0 auto;  /* 居中显示 */
            }}
        </style>
        <script>
        function showRSSInfo() {{
            alert('RSS订阅说明：\\n\\n1. 点击"RSS订阅"链接下载feed.xml文件。\\n2. 将此文件导入您的RSS阅读器。\\n3. 如果您没有RSS阅读器，我们推荐使用Feedly或Inoreader等在线服务。\\n\\n感谢您的订阅！');
        }}
        </script>
    </head>
    <body>
        <header>
            <div class="brand">
                <h1>Daily Hot</h1>
            </div>
            <nav>
                <ul>
                    <li>
                        <a href="feed.xml" title="RSS订阅" onclick="showRSSInfo(); return true;">
                            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FFA500'%3E%3Cpath d='M6.18 15.64a2.18 2.18 0 0 1 2.18 2.18C8.36 19 7.38 20 6.18 20C5 20 4 19 4 17.82a2.18 2.18 0 0 1 2.18-2.18M4 4.44A15.56 15.56 0 0 1 19.56 20h-2.83A12.73 12.73 0 0 0 4 7.27V4.44m0 5.66a9.9 9.9 0 0 1 9.9 9.9h-2.83A7.07 7.07 0 0 0 4 12.93V10.1Z'/%3E%3C/svg%3E" alt="RSS" class="rss-icon">
                            RSS订阅
                        </a>
                    </li>
                    <li class="about-me">
                        <a href="#about">关于我</a>
                        <span class="tooltip">我是Lark，AI开发爱好者，对人工智能的未来充满期待！</span>
                    </li>
                    <li class="contact">
                        <a href="#contact">联系与共创</a>
                        <span class="tooltip">
                            <img src="{contact_img_path}" alt="WeChat QR Code" class="qr-code">
                        </span>
                    </li>
                </ul>
            </nav>
        </header>
        <div class="container">
            <div class="main-content">
                <div class="title-container">
                    <h1>Product Hunt 每日热榜 <span id="robot" class="robot">🤖</span></h1>
                    <div class="blue-line"></div>
                    <div class="date">{date}</div>
                </div>
                {cards_html}
            </div>
        </div>
        <footer>
            <p>&copy; {datetime.now().year} Daily Hot. All rights reserved. Made by Larkspur</p>
        </footer>
        <script>
            const robot = document.getElementById('robot');
            const container = document.querySelector('.title-container');
            let x = 0;
            let y = 0;
            let vx = 0;
            let vy = 0;
            const maxSpeed = 8;  // 增加最大速度
            const acceleration = 0.8;  // 增加加速度
            const deceleration = 0.98;
            const avoidanceDistance = 100;

            function updateRobotPosition() {{
                const rect = container.getBoundingClientRect();
                
                // 随机运动
                if (Math.random() < 0.05) {{  // 增加改变方向的概率
                    vx += (Math.random() - 0.5) * acceleration * 2;  // 增加随机运动的力度
                    vy += (Math.random() - 0.5) * acceleration * 2;
                }}

                x += vx;
                y += vy;

                // 边界检查
                if (x < 0) {{ x = 0; vx = -vx * 0.8; }}
                if (x > rect.width - 60) {{ x = rect.width - 60; vx = -vx * 0.8; }}
                if (y < 0) {{ y = 0; vy = -vy * 0.8; }}
                if (y > rect.height - 60) {{ y = rect.height - 60; vy = -vy * 0.8; }}

                // 应用减速
                vx *= deceleration;
                vy *= deceleration;

                // 限制最大速度
                const speed = Math.sqrt(vx * vx + vy * vy);
                if (speed > maxSpeed) {{
                    vx = (vx / speed) * maxSpeed;
                    vy = (vy / speed) * maxSpeed;
                }}

                robot.style.left = `${{x}}px`;
                robot.style.top = `${{y}}px`;

                requestAnimationFrame(updateRobotPosition);
            }}

            function avoidMouse(e) {{
                const rect = container.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                const dx = x + 30 - mouseX;
                const dy = y + 30 - mouseY;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < avoidanceDistance) {{
                    const angle = Math.atan2(dy, dx);
                    const force = (avoidanceDistance - distance) / avoidanceDistance;

                    vx += Math.cos(angle) * force * acceleration * 3;  // 增加躲避力度
                    vy += Math.sin(angle) * force * acceleration * 3;
                }}
            }}

            container.addEventListener('mousemove', avoidMouse);
            updateRobotPosition();

            // 修改卡片交脚本
            document.querySelectorAll('.scroll-container').forEach(container => {{
                let isDragging = false;
                let startX;
                let scrollLeft;

                container.addEventListener('mousedown', (e) => {{
                    isDragging = true;
                    startX = e.pageX - container.offsetLeft;
                    scrollLeft = container.scrollLeft;
                    container.style.cursor = 'grabbing';
                }});

                container.addEventListener('mousemove', (e) => {{
                    if (!isDragging) return;
                    e.preventDefault();  // 防止默认的拖动行为
                    const x = e.pageX - container.offsetLeft;
                    const walk = (x - startX) * 2;
                    container.scrollLeft = scrollLeft - walk;
                }});

                container.addEventListener('mouseup', () => {{
                    isDragging = false;
                    container.style.cursor = 'grab';
                }});

                container.addEventListener('mouseleave', () => {{
                    isDragging = false;
                    container.style.cursor = 'grab';
                }});
            }});
        </script>
    </body>
    </html>
    """
    return html

def create_rss_feed(products, date):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "Product Hunt Daily Hot"
    ET.SubElement(channel, "link").text = "https://your-website-url.com"
    ET.SubElement(channel, "description").text = "Daily hot products from Product Hunt"
    ET.SubElement(channel, "language").text = "zh-cn"
    ET.SubElement(channel, "pubDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
    
    for product in products:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = product['name']
        ET.SubElement(item, "link").text = product['url']
        ET.SubElement(item, "description").text = f"{product['tagline']}\n\n{product['description']}"
        ET.SubElement(item, "pubDate").text = datetime.strptime(date, "%Y-%m-%d").strftime("%a, %d %b %Y %H:%M:%S %z")
    
    return ET.tostring(rss, encoding="unicode")

def main():
    # 获取脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录（假设脚本在 scripts 文件夹中）
    project_root = os.path.dirname(script_dir)
    # 设置 data 目录的路径
    data_dir = os.path.join(project_root, 'data')
    
    # 确保 data 目录存在
    if not os.path.exists(data_dir):
        print(f"错：找不到 data 目录：{data_dir}")
        sys.exit(1)

    # 确保 img 目录和 contact.jpg 文件存在
    img_dir = os.path.join(project_root, 'img')
    contact_jpg_path = os.path.join(img_dir, 'contact.jpg')
    if not os.path.exists(img_dir):
        print(f"警告：找不到 img 目录：{img_dir}")
        print("正在创建 img 目录...")
        os.makedirs(img_dir)
    if not os.path.exists(contact_jpg_path):
        print(f"错误：找不到 contact.jpg 文件：{contact_jpg_path}")
        print("请确保将 contact.jpg 文件放置在 img 目录中。")
        sys.exit(1)  # 如果文件不存在，直接退出程序
    else:
        print(f"contact.jpg 文件已找到：{contact_jpg_path}")
    
    # 获取最新的 markdown 文
    markdown_files = [f for f in os.listdir(data_dir) if f.endswith('.md')]
    if not markdown_files:
        print("错误：在 data 目录中没有找到 Markdown 文件。")
        sys.exit(1)
    
    # 根据文件中的日期排序，择最新的文件
    latest_file = max(markdown_files, key=lambda x: datetime.strptime(re.search(r'(\d{4}-\d{2}-\d{2})', x).group(1), '%Y-%m-%d'))
    markdown_path = os.path.join(data_dir, latest_file)

    # 从文件名中提取日期
    file_date = re.search(r'(\d{4}-\d{2}-\d{2})', latest_file)
    if file_date:
        file_date = file_date.group(1)
    else:
        file_date = datetime.now().strftime('%Y-%m-%d')

    # 读取markdown内容
    markdown_content = read_markdown_file(markdown_path)
    if markdown_content is None:
        return

    # 解析Product Hunt项目
    products = parse_product_hunt_items(markdown_content)[:24]  # 确保只使用前24个产品
    print(f"Number of products after parsing: {len(products)}")
    if products:
        print("First product info:")
        print(products[0])

    # 创建HTML页面
    html_content = create_html_page(products, file_date)

    # 创建并保存HTML文件到 website_daily 文件夹
    website_daily_dir = os.path.join(project_root, 'website_daily')
    os.makedirs(website_daily_dir, exist_ok=True)
    output_path = os.path.join(website_daily_dir, f'producthunt_daily_{file_date}.html')
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"HTML文件已生成: {output_path}")

    # 创建并保存RSS feed
    rss_content = create_rss_feed(products, file_date)
    rss_path = os.path.join(project_root, 'website_daily', 'feed.xml')
    with open(rss_path, 'w', encoding='utf-8') as file:
        file.write(rss_content)

    print(f"RSS feed已生成: {rss_path}")

    print("Preview of generated HTML:")
    print(html_content[:500])  # 打印前500个字符

if __name__ == "__main__":
    main()