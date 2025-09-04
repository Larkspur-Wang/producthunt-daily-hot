#!/usr/bin/env python3
"""
最终版本的Product Hunt脚本 - 基于测试结果优化
"""
import os
import sys
import requests
import json
import time
import random
from datetime import datetime, timedelta, timezone

def get_product_hunt_data_direct():
    """直接使用Product Hunt API获取数据"""
    print("[DEBUG] 开始获取Product Hunt数据...")
    
    # 使用有效的token
    token = "0pZ43ySQCn3vifDG7-ZVukFKs5Oa_-bPcXrRmrdVa3c"
    
    # API端点
    url = "https://api.producthunt.com/v2/api/graphql"
    
    # 计算昨天的日期
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    print(f"[DEBUG] 获取日期: {date_str}")
    
    # 使用更真实的浏览器headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://producthunt.com",
        "Referer": "https://producthunt.com/",
        "Connection": "keep-alive"
    }
    
    # 简化的查询 - 直接获取前24个
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
    
    try:
        print("[DEBUG] 发送API请求...")
        response = requests.post(url, headers=headers, json={"query": query}, timeout=30)
        
        print(f"[DEBUG] 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print(f"[ERROR] API错误: {data['errors']}")
                return []
            
            posts = data.get('data', {}).get('posts', {}).get('nodes', [])
            print(f"[DEBUG] 成功获取 {len(posts)} 个帖子")
            
            # 按票数排序
            posts.sort(key=lambda x: x['votesCount'], reverse=True)
            
            return posts[:24]  # 确保最多24个
            
        else:
            print(f"[ERROR] 请求失败: {response.status_code}")
            print(f"[ERROR] 响应: {response.text[:500]}")
            return []
            
    except Exception as e:
        print(f"[ERROR] 请求异常: {e}")
        return []

def main():
    """主函数"""
    print("=== Product Hunt 数据获取测试 ===")
    
    # 获取数据
    products = get_product_hunt_data_direct()
    
    if products:
        print(f"\n成功获取 {len(products)} 个产品:")
        for i, product in enumerate(products[:5]):  # 显示前5个
            print(f"{i+1}. {product['name']} - {product['votesCount']} 票")
            print(f"   {product['tagline']}")
            print()
        
        print("数据获取成功！")
    else:
        print("未能获取数据")

if __name__ == "__main__":
    main()