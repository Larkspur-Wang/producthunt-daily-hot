import re
from bs4 import BeautifulSoup
import markdown
import os
from datetime import datetime
import random

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
                product['keywords'] = line.replace('**关键词**：', '').strip()
            elif line.startswith('**发布时间**：'):
                product['time'] = line.replace('**发布时间**：', '').strip()
        
        if all(key in product for key in ['name', 'url', 'image', 'tagline', 'description', 'votes', 'keywords', 'time']):
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
            <p class="keywords">{product['keywords']}</p>
            <p class="time">{product['time']}</p>
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
    products = products[:24]  # 确保只使用前24个产品
    rows = [products[i:i+6] for i in range(0, len(products), 6)]
    
    cards_html = ""
    for i, row in enumerate(rows):
        direction = "normal" if i % 2 == 0 else "reverse"
        cards_html += f"""
        <div class="scroll-container">
            <div class="scroll-row" style="animation-direction: {direction};">
                {''.join([create_html_card(product) for product in row * 2])}
            </div>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Product Hunt 每日热榜 | {date}</title>
        <link href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --background-color: #f7f7f7;
                --text-color: #333333;
                --accent-color: #0066cc;
                --card-background: #ffffff;
                --card-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            body {{
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: var(--background-color);
                color: var(--text-color);
                margin: 0;
                padding: 0;
                line-height: 1.4;
                overflow-x: hidden;
            }}
            .container {{
                max-width: 100%;
                margin: 0 auto;
                padding: 2rem 0;
            }}
            header {{
                text-align: center;
                margin-bottom: 2rem;
            }}
            h1 {{
                font-size: 48px;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }}
            .date {{
                font-size: 18px;
                color: #666;
            }}
            .scroll-container {{
                overflow: hidden;
                margin-bottom: 2rem;
            }}
            .scroll-row {{
                display: flex;
                animation: scroll 30s linear infinite;
                width: 200%; /* 显示8个卡片的宽度 */
            }}
            .card {{
                flex: 0 0 12.5%;
                max-width: 12.5%;
                padding: 1rem;
                box-sizing: border-box;
                position: relative;
            }}
            .card-inner {{
                background-color: var(--card-background);
                border-radius: 12px;
                box-shadow: var(--card-shadow);
                overflow: hidden;
                height: 100%;
                display: flex;
                flex-direction: column;
            }}
            .product-image {{
                width: 100%;
                height: 150px;
                object-fit: cover;
            }}
            h2 {{
                font-size: 18px;
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
                font-weight: 500;
                color: #555;
            }}
            .description {{
                flex-grow: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-line-clamp: 3;
                -webkit-box-orient: vertical;
            }}
            .votes {{
                font-weight: 600;
                color: var(--accent-color);
            }}
            .keywords, .time {{
                font-size: 12px;
                color: #888;
            }}
            @keyframes scroll {{
                0% {{
                    transform: translateX(0);
                }}
                100% {{
                    transform: translateX(-50%);
                }}
            }}
            .title-container {{
                position: relative;
                display: inline-block;
                overflow: hidden;
                padding: 0 30px;
            }}
            .robot {{
                position: absolute;
                font-size: 24px;
                transition: all 0.5s ease;
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
            .votes-badge {{
                position: absolute;
                top: 0.5rem;
                left: 0.5rem;
                background-color: rgba(0, 0, 0, 0.6);
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                z-index: 1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="title-container">
                    <h1>Product Hunt 每日热榜</h1>
                    <span class="robot" id="robot">🤖</span>
                </div>
                <div class="date">{date}</div>
            </header>
            {cards_html}
        </div>
        <footer>
            <p>&copy; 2024 Made by Lark. All rights reserved.</p>
        </footer>
        <script>
            const robot = document.getElementById('robot');
            const container = document.querySelector('.title-container');
            let direction = 1;
            let position = -30;
            let isJumping = false;

            function moveRobot() {{
                if (!isJumping) {{
                    position += direction * 2;
                    if (position > container.offsetWidth - 30 || position < -30) {{
                        direction *= -1;
                        robot.style.transform = `scaleX(${{direction}})`;
                    }}
                    robot.style.left = `${{position}}px`;
                }}

                if (Math.random() < 0.005 && !isJumping) {{  // 0.5% 概率开始跳跃
                    isJumping = true;
                    robot.style.animation = 'float 1s ease-in-out';
                    setTimeout(() => {{
                        isJumping = false;
                        robot.style.animation = 'none';
                    }}, 1000);
                }}

                requestAnimationFrame(moveRobot);
            }}

            robot.style.left = '-30px';
            robot.style.top = '50%';
            robot.style.transform = 'translateY(-50%)';
            moveRobot();
        </script>
    </body>
    </html>
    """
    return html

def main():
    # 获取最新的markdown文件
    data_dir = 'data'
    markdown_files = [f for f in os.listdir(data_dir) if f.endswith('.md')]
    if not markdown_files:
        print("Error: No Markdown files found in the data directory.")
        return
    
    # 根据文件名中的日期排序，选择最新的文件
    latest_file = max(markdown_files, key=lambda x: datetime.strptime(re.search(r'(\d{4}-\d{2}-\d{2})', x).group(1), '%Y-%m-%d'))
    markdown_path = os.path.join(data_dir, latest_file)
    #print(f"Reading file: {markdown_path}")

    # 从文件名中提取日期
    file_date = re.search(r'(\d{4}-\d{2}-\d{2})', latest_file)
    if file_date:
        file_date = file_date.group(1)
    else:
        file_date = datetime.now().strftime('%Y-%m-%d')
        #print(f"Warning: Could not extract date from filename. Using current date: {file_date}")

    # 读取markdown内容
    markdown_content = read_markdown_file(markdown_path)
    if markdown_content is None:
        #print("Error: Failed to read Markdown content. Exiting.")
        return

    # 解析Product Hunt项目
    products = parse_product_hunt_items(markdown_content)[:24]  # 确保只使用前24个产品
    print(f"Number of products after parsing: {len(products)}")
    if products:
        print("First product info:")
        print(products[0])

    # 创建HTML页面
    html_content = create_html_page(products, file_date)

    # 保存HTML文件
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'producthunt_daily_{file_date}.html')
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"HTML文件已生成: {output_path}")

    print("Preview of generated HTML:")
    print(html_content[:500])  # 打印前500个字符

if __name__ == "__main__":
    main()
