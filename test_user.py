#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试用户UID是否有效"""

import json
import requests

# 读取配置
with open('crawler/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Cookie': config.get('cookie', ''),
    'Referer': 'https://weibo.com'
})

print("=" * 60)
print("测试用户UID有效性")
print("=" * 60)

for user in config['target_users']:
    uid = user['uid']
    name = user['name']

    print(f"\n测试用户: {name} (UID: {uid})")
    print("-" * 60)

    # 测试用户信息接口
    url = f'https://weibo.com/ajax/profile/info?uid={uid}'
    try:
        response = session.get(url, timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('ok') == 1:
                user_info = data['data']['user']
                print(f"✓ 用户名: {user_info.get('screen_name', 'N/A')}")
                print(f"✓ 粉丝数: {user_info.get('followers_count', 0)}")
                print(f"✓ 微博数: {user_info.get('statuses_count', 0)}")
                print(f"✓ 简介: {user_info.get('description', 'N/A')[:50]}...")
            else:
                print(f"✗ API返回错误: {data}")
        else:
            print(f"✗ HTTP错误: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
    except Exception as e:
        print(f"✗ 请求失败: {str(e)}")

    # 测试微博列表接口
    url2 = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1&feature=0'
    try:
        response2 = session.get(url2, timeout=10)
        if response2.status_code == 200:
            data2 = response2.json()
            if data2.get('ok') == 1:
                weibo_list = data2['data'].get('list', [])
                print(f"✓ 可获取微博列表，第一页有 {len(weibo_list)} 条")
            else:
                print(f"✗ 微博列表API错误: {data2}")
        else:
            print(f"✗ 微博列表HTTP错误: {response2.status_code}")
    except Exception as e:
        print(f"✗ 微博列表请求失败: {str(e)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
