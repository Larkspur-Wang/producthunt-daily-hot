#!/usr/bin/env python3
"""
专门针对GitHub Actions环境的Product Hunt API访问
"""
import os
import requests
import json
import time
import random
from datetime import datetime, timezone, timedelta

def get_product_hunt_data_github_actions():
    """专门针对GitHub Actions环境的数据获取"""
    print("[DEBUG] 使用GitHub Actions专用版本...")
    
    # 使用有效的token
    token = os.getenv('PRODUCTHUNT_DEVELOPER_TOKEN')
    if not token:
        raise Exception("PRODUCTHUNT_DEVELOPER_TOKEN not found in environment variables")
    
    # API端点
    url = "https://api.producthunt.com/v2/api/graphql"
    
    # 计算昨天的日期
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    print(f"[DEBUG] 获取日期: {date_str}")
    
    # 更真实的浏览器headers - 模拟真实用户
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Origin": "https://producthunt.com",
        "Referer": "https://producthunt.com/",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    # 先访问主页建立session
    print("[DEBUG] 先访问Product Hunt主页建立session...")
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        
        # 访问主页
        main_response = session.get("https://producthunt.com", timeout=30)
        print(f"[DEBUG] 主页访问状态: {main_response.status_code}")
        
        # 等待一下
        time.sleep(random.uniform(2, 5))
        
    except Exception as e:
        print(f"[DEBUG] 主页访问失败: {e}")
        session = requests.Session()
    
    # GraphQL查询
    query = f"""
    {{
      posts(first: 24, order: VOTES, postedAfter: "{date_str}T00:00:00Z", postedBefore: "{date_str}T23:59:59Z") {{
        nodes {{
          id
          name
          tagline
          description
          votesCount
          createdAt
          featuredAt
          website
          url
        }}
      }}
    }}
    """
    
    max_retries = 5  # 增加重试次数
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] 发送API请求 (尝试 {attempt + 1}/{max_retries})...")
            
            # 随机延迟，特别是重试时
            if attempt > 0:
                delay = random.uniform(10, 30)  # 更长的延迟
                print(f"[DEBUG] 等待 {delay:.1f} 秒...")
                time.sleep(delay)
            
            # 使用session发送请求
            response = session.post(url, headers=headers, json={"query": query}, timeout=60)
            
            print(f"[DEBUG] 状态码: {response.status_code}")
            print(f"[DEBUG] 响应头Content-Type: {response.headers.get('content-type', 'None')}")
            
            if response.status_code == 200:
                # 检查响应内容
                if not response.text.strip():
                    print(f"[DEBUG] 响应为空，可能被拦截")
                    if attempt == max_retries - 1:
                        return []
                    continue
                
                try:
                    data = response.json()
                    
                    if 'errors' in data:
                        print(f"[DEBUG] API错误: {data['errors']}")
                        if attempt == max_retries - 1:
                            return []
                        continue
                    
                    posts = data.get('data', {}).get('posts', {}).get('nodes', [])
                    print(f"[DEBUG] 成功获取 {len(posts)} 个帖子")
                    
                    # 按票数排序
                    posts.sort(key=lambda x: x['votesCount'], reverse=True)
                    
                    return posts[:24]
                    
                except json.JSONDecodeError as e:
                    print(f"[DEBUG] JSON解析失败: {e}")
                    print(f"[DEBUG] 响应内容前200字符: {response.text[:200]}")
                    if attempt == max_retries - 1:
                        return []
                    continue
                    
            elif response.status_code == 403:
                print(f"[DEBUG] 收到403错误，可能是Cloudflare防护")
                print(f"[DEBUG] 响应内容: {response.text[:200]}")
                if attempt == max_retries - 1:
                    return []
            elif response.status_code == 429:
                print(f"[DEBUG] 收到429错误，速率限制")
                if attempt == max_retries - 1:
                    return []
                # 更长的延迟
                delay = random.uniform(30, 60)
                print(f"[DEBUG] 速率限制，等待 {delay:.1f} 秒...")
                time.sleep(delay)
                continue
            else:
                print(f"[DEBUG] 请求失败: {response.status_code}")
                print(f"[DEBUG] 响应内容: {response.text[:200]}")
                if attempt == max_retries - 1:
                    return []
                
        except Exception as e:
            print(f"[DEBUG] 请求异常: {e}")
            if attempt == max_retries - 1:
                return []
    
    return []

# 如果直接运行此脚本进行测试
if __name__ == "__main__":
    print("=== GitHub Actions版本测试 ===")
    
    # 模拟GitHub Actions环境变量
    os.environ['PRODUCTHUNT_DEVELOPER_TOKEN'] = "0pZ43ySQCn3vifDG7-ZVukFKs5Oa_-bPcXrRmrdVa3c"
    
    products = get_product_hunt_data_github_actions()
    
    if products:
        print(f"成功获取 {len(products)} 个产品:")
        for i, product in enumerate(products[:5]):
            print(f"{i+1}. {product['name']} - {product['votesCount']} 票")
    else:
        print("未能获取数据")