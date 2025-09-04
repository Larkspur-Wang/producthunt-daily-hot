#!/usr/bin/env python3
"""
测试Product Hunt Developer Token - 简化版本
"""
import os
import requests
import json

def test_token():
    """测试token是否有效"""
    print("=== 测试Product Hunt Developer Token ===")
    
    # 你的token信息
    token = "0pZ43ySQCn3vifDG7-ZVukFKs5Oa_-bPcXrRmrdVa3c"
    
    # API端点
    url = "https://api.producthunt.com/v2/api/graphql"
    
    # 请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    
    # 简单测试查询
    test_query = """
    {
      posts(first: 5) {
        nodes {
          id
          name
          tagline
          votesCount
        }
      }
    }
    """
    
    print(f"使用的Token: {token[:20]}...")
    print(f"请求URL: {url}")
    
    try:
        print("\n发送请求...")
        response = requests.post(url, headers=headers, json={"query": test_query}, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("[OK] 请求成功!")
                
                # 检查是否有错误
                if 'errors' in data:
                    print(f"[WARNING] API返回错误: {data['errors']}")
                else:
                    posts = data.get('data', {}).get('posts', {}).get('nodes', [])
                    print(f"[OK] 成功获取 {len(posts)} 个帖子")
                    
                    # 显示前几个帖子
                    for i, post in enumerate(posts[:3]):
                        print(f"  {i+1}. {post['name']} - {post['votesCount']} 票")
                    
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON解析失败: {e}")
                print(f"响应内容: {response.text[:500]}")
        else:
            print(f"[ERROR] 请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
            # 分析错误类型
            if "cloudflare" in response.text.lower():
                print("[INFO] 检测到Cloudflare防护")
            elif "invalid_oauth_token" in response.text:
                print("[INFO] Token无效或已过期")
            elif "rate_limit" in response.text.lower():
                print("[INFO] 达到速率限制")
                
    except Exception as e:
        print(f"[ERROR] 请求异常: {e}")

if __name__ == "__main__":
    test_token()