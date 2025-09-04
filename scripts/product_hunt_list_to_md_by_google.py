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
from typing import Optional, List, Dict, Any

# 加载 .env 文件
# load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

producthunt_client_id = os.getenv('PRODUCTHUNT_CLIENT_ID')
producthunt_client_secret = os.getenv('PRODUCTHUNT_CLIENT_SECRET')

def call_gemini_api(prompt: str, model: str = "gemini-2.0-flash-exp", temperature: float = 0.8) -> str:
    """调用Google Gemini API"""
    print(f"\n[DEBUG] 正在调用Gemini API，模型：{model}")
    try:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        url = f"{GEMINI_API_BASE}/{model}:generateContent?key={GOOGLE_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "contents": [{
                "parts":[{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "topK": 40,
                "topP": 0.95,
            }
        }
        
        print(f"[DEBUG] 发送API请求...")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            print(f"[DEBUG] API调用成功")
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"[DEBUG] API返回结果为空")
            return ""
    except Exception as e:
        print(f"[DEBUG] API调用错误: {e}")
        return ""

class Product:
    def __init__(self, id: str, name: str, tagline: str, description: str, votesCount: int, createdAt: str, featuredAt: str, website: str, url: str, **kwargs):
        print(f"\n[DEBUG] 正在初始化产品: {name}")
        self.name = name
        self.tagline = tagline
        self.description = description
        self.votes_count = votesCount
        self.created_at = self.convert_to_beijing_time(createdAt)
        self.featured = "是" if featuredAt else "否"
        self.website = website
        self.url = url
        
        print(f"[DEBUG] 获取产品图片URL...")
        self.og_image_url = self.fetch_og_image_url()
        
        print(f"[DEBUG] 生成产品关键词...")
        self.keyword = self.generate_keywords()
        
        print(f"[DEBUG] 翻译产品标语...")
        self.translated_tagline = self.translate_text(self.tagline)
        
        print(f"[DEBUG] 翻译产品描述...")
        self.translated_description = self.translate_text(self.description)
        
        print(f"[DEBUG] 产品 {name} 初始化完成\n")

    def fetch_og_image_url(self) -> str:
        """获取产品的Open Graph图片URL"""
        print(f"正在获取URL: {self.url}")  # 打印正在请求的URL
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
        
        # 添加随机延迟
        random_delay(2, 5)
        
        try:
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] 请求失败: {e}")
            return ""
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
        prompt = f"将以下英文翻译成中文。\n\n{text}"
        
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

def get_session_headers() -> Dict[str, str]:
    """获取模拟浏览器的请求头"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15"
    ]
    
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Authorization": f"Bearer {get_producthunt_token()}",
        "Content-Type": "application/json",
        "User-Agent": random.choice(user_agents),
        "Origin": "https://producthunt.com",
        "Referer": "https://producthunt.com/",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "keep-alive"
    }

def create_session_with_retry() -> requests.Session:
    """创建带有重试策略的Session"""
    session = requests.Session()
    
    # 设置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[403, 429, 500, 502, 503, 504],
        respect_retry_after_header=True
    )
    
    # 设置适配器
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

def random_delay(min_seconds: float = 3, max_seconds: float = 8) -> None:
    """随机延迟，避免被识别为机器人"""
    delay = random.uniform(min_seconds, max_seconds)
    print(f"[DEBUG] 等待 {delay:.2f} 秒...")
    time.sleep(delay)

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 5):
    """带指数退避的重试装饰器"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # 计算延迟时间（指数退避 + 随机抖动）
                delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
                print(f"[DEBUG] 请求失败，{delay:.2f} 秒后重试 (尝试 {attempt + 1}/{max_retries}): {e}")
                time.sleep(delay)
        
    return wrapper

def fetch_product_hunt_data() -> List[Product]:
    """从Product Hunt获取前一天的Top 24数据"""
    print("[DEBUG] 初始化Session和请求头...")
    session = create_session_with_retry()
    headers = get_session_headers()
    
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    url = "https://api.producthunt.com/v2/api/graphql"
    
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

    def make_graphql_request(cursor: str) -> Dict[str, Any]:
        """发送GraphQL请求"""
        query = base_query % (date_str, date_str, cursor)
        print(f"[DEBUG] 发送请求到Product Hunt API...")
        
        try:
            response = session.post(url, headers=headers, json={"query": query}, timeout=30)
            
            print(f"[DEBUG] 响应状态码: {response.status_code}")
            print(f"[DEBUG] 响应头: {dict(response.headers)}")
            
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                print(f"[DEBUG] 警告: 响应不是JSON格式，Content-Type: {content_type}")
                print(f"[DEBUG] 响应内容前500字符: {response.text[:500]}")
                
            if response.status_code == 403:
                print(f"[DEBUG] 收到403错误，可能触发了Cloudflare防护")
                if "cf-browser-verification" in response.text or "challenge" in response.text.lower():
                    print("[DEBUG] 检测到Cloudflare挑战页面，需要更高级的绕过方法")
                    raise Exception("Cloudflare challenge detected")
                
            response.raise_for_status()
            
            # 尝试解析JSON
            try:
                return response.json()
            except json.JSONDecodeError as e:
                print(f"[DEBUG] JSON解析错误: {e}")
                print(f"[DEBUG] 响应内容: {response.text}")
                raise
                
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] 请求异常: {e}")
            raise

    all_posts = []
    has_next_page = True
    cursor = ""
    retry_count = 0
    max_retries = 3

    while has_next_page and len(all_posts) < 24:
        try:
            # 在第一次请求或后续请求之间添加随机延迟
            if cursor != "":
                random_delay(5, 10)
            
            data = make_graphql_request(cursor)
            posts = data['data']['posts']['nodes']
            all_posts.extend(posts)

            has_next_page = data['data']['posts']['pageInfo']['hasNextPage']
            cursor = data['data']['posts']['pageInfo']['endCursor']
            
            print(f"[DEBUG] 已获取 {len(posts)} 个产品，总计 {len(all_posts)} 个")
            
            # 重置重试计数
            retry_count = 0
            
        except Exception as e:
            retry_count += 1
            print(f"[DEBUG] 获取数据失败 (尝试 {retry_count}/{max_retries}): {e}")
            
            if retry_count >= max_retries:
                print("[DEBUG] 达到最大重试次数，终止请求")
                break
            
            # 指数退避
            delay = 10 * (2 ** (retry_count - 1)) + random.uniform(0, 5)
            print(f"[DEBUG] {delay:.2f} 秒后重试...")
            time.sleep(delay)

    # 只保留前24个产品
    sorted_posts = sorted(all_posts, key=lambda x: x['votesCount'], reverse=True)[:24]
    print(f"[DEBUG] 最终选取前24个产品")
    
    # 关闭session
    session.close()
    
    return [Product(**post) for post in sorted_posts]

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
    print("\n[DEBUG] 程序开始运行...")
    print(f"[DEBUG] Python版本: {os.sys.version}")
    print(f"[DEBUG] requests版本: {requests.__version__}")
    
    # 获取昨天的日期并格式化
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    print(f"[DEBUG] 处理日期: {date_str}")

    # 获取Product Hunt数据
    print("[DEBUG] 开始获取Product Hunt数据...")
    try:
        products = fetch_product_hunt_data()
        print(f"[DEBUG] 成功获取{len(products)}个产品数据")
        
        if not products:
            print("[DEBUG] 警告: 没有获取到任何产品数据")
            return
            
    except Exception as e:
        print(f"[DEBUG] 获取Product Hunt数据失败: {e}")
        print("[DEBUG] 程序异常终止")
        raise

    # 生成Markdown文件
    print("[DEBUG] 开始生成Markdown文件...")
    generate_markdown(products, date_str)
    print("[DEBUG] 程序运行完成")

if __name__ == "__main__":
    main()
