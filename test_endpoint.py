#!/usr/bin/env python3
"""
简单测试Product Hunt API响应
"""
import requests
import json

def test_api_endpoint():
    """测试API端点是否可访问"""
    print("=== 测试Product Hunt API端点 ===")
    
    # 测试1: 直接访问API端点
    urls_to_test = [
        "https://api.producthunt.com/v2/api/graphql",
        "https://producthunt.com/api/graphql",
        "https://api.producthunt.com/v1/graphql"
    ]
    
    # 模拟浏览器请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # 测试每个URL
    for i, url in enumerate(urls_to_test, 1):
        print(f"\n{i}. 测试GET请求: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            print(f"响应头Content-Type: {response.headers.get('content-type', 'None')}")
            
            if response.status_code == 403:
                print("检测到403错误，可能是Cloudflare防护")
                if "cloudflare" in response.text.lower():
                    print("响应中包含Cloudflare相关内容")
            elif response.status_code == 404:
                print("URL不存在")
            elif response.status_code == 200:
                print("GET请求成功")
                
        except Exception as e:
            print(f"请求失败: {e}")
    
    # 测试2: 测试GraphQL POST请求（不带认证）
    test_query = """
    {
      posts(first: 5) {
        nodes {
          id
          name
        }
      }
    }
    """
    
    for i, url in enumerate(urls_to_test, 1):
        print(f"\n{i+3}. 测试POST请求（无认证）: {url}")
        try:
            response = requests.post(
                url, 
                headers={**headers, "Content-Type": "application/json"}, 
                json={"query": test_query}, 
                timeout=10
            )
            print(f"状态码: {response.status_code}")
            print(f"响应头Content-Type: {response.headers.get('content-type', 'None')}")
            
            if response.status_code == 403:
                print("检测到403错误，可能是Cloudflare防护或需要认证")
                print(f"响应内容前200字符: {response.text[:200]}")
            elif response.status_code == 401:
                print("需要认证（这是正常的）")
                try:
                    data = response.json()
                    print(f"API响应: {json.dumps(data, indent=2)}")
                except:
                    print(f"响应内容: {response.text[:200]}")
            elif response.status_code == 200:
                try:
                    data = response.json()
                    print("POST请求成功")
                    print(f"响应数据: {json.dumps(data, indent=2)}")
                except:
                    print(f"响应不是有效的JSON: {response.text[:200]}")
                    
        except Exception as e:
            print(f"请求失败: {e}")
    
    # 测试3: 访问主页
    print(f"\n7. 测试Product Hunt主页")
    try:
        response = requests.get("https://producthunt.com", headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("主页访问成功")
            if "cloudflare" in response.text.lower():
                print("主页也有Cloudflare防护")
        else:
            print(f"主页访问失败: {response.text[:100]}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_api_endpoint()