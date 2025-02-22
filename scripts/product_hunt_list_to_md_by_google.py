import os
# from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import pytz
import time
import random
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from google import genai

# 加载 .env 文件
# load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
producthunt_client_id = os.getenv('PRODUCTHUNT_CLIENT_ID')
producthunt_client_secret = os.getenv('PRODUCTHUNT_CLIENT_SECRET')

def call_gemini_api(prompt: str, model: str = "gemini-2.0-flash-exp", temperature: float = 0.7) -> str:
    """调用Google Gemini API"""
    try:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=GOOGLE_API_KEY)
        client = genai.GenerativeModel(model)
        response = client.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                top_k=40,
                top_p=0.95,
            )
        )
        
        if response and response.text:
            return response.text.strip()
        else:
            return ""
    except Exception as e:
        print(f"API调用错误: {e}")
        return ""

class Product:
    def __init__(self, id: str, name: str, tagline: str, description: str, votesCount: int, createdAt: str, featuredAt: str, website: str, url: str, **kwargs):
        self.name = name
        self.tagline = tagline
        self.description = description
        self.votes_count = votesCount
        self.created_at = self.convert_to_beijing_time(createdAt)
        self.featured = "是" if featuredAt else "否"
        self.website = website
        self.url = url
        self.og_image_url = self.fetch_og_image_url()
        self.keyword = self.generate_keywords()
        self.translated_tagline = self.translate_text(self.tagline)
        self.translated_description = self.translate_text(self.description)

    def fetch_og_image_url(self) -> str:
        """获取产品的Open Graph图片URL"""
        print(f"正在获取URL: {self.url}")  # 打印正在请求的URL
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(self.url, headers=headers)
        print(f"请求状态码: {response.status_code}")  # 打印请求状态码
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找og:image meta标签
            og_image = soup.find("meta", property="og:image")
            if og_image:
                print(f"找到 og:image 标签: {og_image}") # 打印 og:image 标签内容
                return og_image["content"]
            # 备用:查找twitter:image meta标签
            twitter_image = soup.find("meta", name="twitter:image")
            if twitter_image:
                print(f"找到 twitter:image 标签: {twitter_image}") # 打印 twitter:image 标签内容
                return twitter_image["content"]
        print("没有找到图片 URL") # 打印未找到图片 URL 的消息
        return ""

    def generate_keywords(self) -> str:
        """生成产品的关键词，显示在一行，用逗号分隔"""
        prompt = f"根据以下内容生成3个适合的中文关键词，用英文逗号分隔开：\n\n产品名称：{self.name}\n\n标语：{self.tagline}\n\n描述：{self.description}"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                keywords = call_gemini_api(prompt, model="gemini-2.0-flash-exp")
                if keywords:
                    if ',' not in keywords:
                        keywords = ', '.join(keywords.split())
                    time.sleep(random.uniform(5, 8))  # 随机等待5-8秒
                    return keywords
                else:
                    print(f"API返回空响应，尝试重试 {attempt + 1}/{max_retries}")
            except Exception as e:
                print(f"生成关键词时发生错误（尝试 {attempt + 1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(8, 12))  # 在重试之前随机等待8-12秒
                else:
                    return "无关键词"
        
        return "无关键词"

    def translate_text(self, text: str) -> str:
        """使用Google Gemini翻译文本内容"""
        prompt = f"将以下英文翻译成地道的中文，风格与科普杂志或日常对话相似。不要有翻译外的额外内容：\n\n{text}"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                translated_text = call_gemini_api(prompt, model="gemini-2.0-flash-exp")
                if translated_text:
                    time.sleep(5)  # 在API调用后等待5秒
                    return translated_text
                else:
                    print(f"API返回空响应，尝试重试 {attempt + 1}/{max_retries}")
            except Exception as e:
                print(f"翻译文本时发生错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(8, 12))  # 在重试之前随机等待8-12秒
                else:
                    return text  # 最后一次重试失败，返回原始文本
        
        return text

    def convert_to_beijing_time(self, utc_time_str: str) -> str:
        """将UTC时间转换为北京时间"""
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
        return beijing_time.strftime('%Y年%m月%d日 %p%I:%M (北京时间)')

    def to_markdown(self, rank: int) -> str:
        """返回产品数据的Markdown格式"""
        og_image_markdown = f"![{self.name}]({self.og_image_url})"
        return (
            f"## [{rank}. {self.name}]({self.url})  \n"
            f"{og_image_markdown}  \n\n"
            f"**标语**：{self.translated_tagline}  \n"
            f"**介绍**：{self.translated_description}  \n"
            f"**票数**: 🔺{self.votes_count}  \n"
            f"**关键词**：{self.keyword}  \n"
            f"**发布时间**：{self.created_at}  \n\n"
            #f"**产品网站**: [立即访问]({self.website})  \n"
            #f"**Product Hunt**: [View on Product Hunt]({self.url})\n\n"                                  
            #f"**是否精选**：{self.featured} \n"           
            f"---\n\n"
        )

def get_producthunt_token():
    """使用 developer token 进行认证"""
    token = os.getenv('PRODUCTHUNT_DEVELOPER_TOKEN')
    print(f"token is {token};")
    if not token:
        raise Exception("Product Hunt developer token not found in environment variables")
    return token

def fetch_product_hunt_data():
    """从Product Hunt获取前一天的Top 24数据"""
    token = get_producthunt_token()
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    url = "https://api.producthunt.com/v2/api/graphql"
    
    # 添加更多请求头信息
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "DecohackBot/1.0 (https://decohack.com)",
        "Origin": "https://decohack.com",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Connection": "keep-alive"
    }
    
    base_query = """
    {
      posts(order: VOTES, postedAfter: "%sT00:00:00Z", postedBefore: "%sT23:59:59Z", after: "%s") {
        nodes {
          id
          name
          tagline
          description
          votesCount
          createdAt
          featuredAt
          website
          url
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """

    all_posts = []
    has_next_page = True
    cursor = ""

    while has_next_page and len(all_posts) < 24:
        query = base_query % (date_str, date_str, cursor)
        response = requests.post(url, headers=headers, json={"query": query})

        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from Product Hunt: {response.status_code}, {response.text}")

        data = response.json()['data']['posts']
        posts = data['nodes']
        all_posts.extend(posts)

        has_next_page = data['pageInfo']['hasNextPage']
        cursor = data['pageInfo']['endCursor']

    # 只保留前24个产品
    return [Product(**post) for post in sorted(all_posts, key=lambda x: x['votesCount'], reverse=True)[:24]]

def generate_markdown(products, date_str):
    """生成Markdown内容并保存到data目录"""
    # 获取今天的日期并格式化
    today = datetime.now(timezone.utc)
    date_today = today.strftime('%Y-%m-%d')

    markdown_content = f"# PH今日热榜 | {date_today}\n\n"
    for rank, product in enumerate(products, 1):
        markdown_content += product.to_markdown(rank)

    # 确保 data 目录存在
    os.makedirs('data', exist_ok=True)

    # 修改文件保存路径到 data 目录
    file_name = f"data/producthunt-daily-{date_today}.md"
    
    # 如果文件存在，直接覆盖
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(markdown_content)
    print(f"文件 {file_name} 生成成功并已覆盖。")


def main():
    # 获取昨天的日期并格式化
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')

    # 获取Product Hunt数据
    products = fetch_product_hunt_data()

    # 生成关键词和翻译
    for product in products:
        product.keyword = product.generate_keywords()
        product.translated_tagline = product.translate_text(product.tagline)
        product.translated_description = product.translate_text(product.description)
        time.sleep(2)  # 在每个产品的处理之间添加2秒的延迟

    # 生成Markdown文件
    generate_markdown(products, date_str)

if __name__ == "__main__":
    main()
