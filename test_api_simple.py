#!/usr/bin/env python3
"""
测试Product Hunt API访问
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import cloudscraper
    print("[OK] cloudscraper 可用")
except ImportError:
    print("[ERROR] cloudscraper 不可用")

from scripts.product_hunt_list_to_md_by_google import get_producthunt_token, get_session_headers, create_session_with_retry

def test_product_hunt_api():
    """测试Product Hunt API访问"""
    print("\n=== 测试Product Hunt API访问 ===")
    
    # 获取token
    try:
        token = get_producthunt_token()
        print("[OK] Token获取成功")
    except Exception as e:
        print(f"[ERROR] Token获取失败: {e}")
        return
    
    # 创建session
    try:
        session = create_session_with_retry()
        print("[OK] Session创建成功")
    except Exception as e:
        print(f"[ERROR] Session创建失败: {e}")
        return
    
    # 测试API
    url = "https://api.producthunt.com/v2/api/graphql"
    headers = get_session_headers()
    
    # 简单测试查询
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
    
    try:
        print("\n发送测试请求...")
        response = session.post(url, headers=headers, json={"query": test_query}, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("[OK] API响应成功")
                print(f"返回数据: {data}")
            except Exception as e:
                print(f"[ERROR] JSON解析失败: {e}")
                print(f"响应内容: {response.text[:200]}")
        else:
            print(f"[ERROR] API请求失败: {response.text[:200]}")
            
    except Exception as e:
        print(f"[ERROR] 请求异常: {e}")

if __name__ == "__main__":
    test_product_hunt_api()