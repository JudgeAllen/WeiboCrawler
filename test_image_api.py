#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试微博API返回的图片数据"""

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

# 测试获取微博列表
uid = config['target_users'][0]['uid']
url = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1&feature=0'

print("=" * 60)
print("测试微博API返回数据")
print("=" * 60)

try:
    response = session.get(url, timeout=10)
    data = response.json()

    if data.get('ok') == 1:
        weibos = data['data'].get('list', [])
        print(f"\n获取到 {len(weibos)} 条微博\n")

        # 查找第一条有图片的微博
        for i, weibo in enumerate(weibos):
            print(f"\n微博 {i+1}:")
            print(f"ID: {weibo.get('id', '')}")
            print(f"内容: {weibo.get('text_raw', '')[:50]}...")

            # 检查各种可能的图片字段
            print(f"\n图片相关字段:")
            print(f"  pics: {weibo.get('pics', 'N/A')}")
            print(f"  pic_ids: {weibo.get('pic_ids', 'N/A')}")
            print(f"  pic_num: {weibo.get('pic_num', 'N/A')}")

            # 显示完整的键列表
            if i == 0:
                print(f"\n所有字段: {list(weibo.keys())}")

            # 如果有图片就显示详细信息
            if weibo.get('pics') or weibo.get('pic_ids'):
                print(f"\n找到有图片的微博！")
                print(f"完整数据:")
                print(json.dumps(weibo.get('pics', []), indent=2, ensure_ascii=False))
                break
    else:
        print(f"API返回错误: {data}")

except Exception as e:
    print(f"请求失败: {str(e)}")
