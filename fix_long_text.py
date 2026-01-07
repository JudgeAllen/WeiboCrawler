#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复数据库中被截断的长文本微博"""

import sys
import json
import sqlite3
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def fetch_weibo_detail(weibo_id, cookie):
    """获取单条微博的完整信息"""
    url = f'https://weibo.com/ajax/statuses/show?id={weibo_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cookie': cookie,
        'Referer': 'https://weibo.com'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('ok') == 1:
            return data
        else:
            print(f"API返回错误: {data}")
            return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def main():
    """主函数"""
    # 读取配置获取cookie
    config_path = Path(__file__).parent / 'crawler' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    cookie = config.get('cookie', '')
    if not cookie:
        print("错误: 配置文件中没有cookie")
        return 1

    # 测试微博ID: 2021-01-14 22:07的微博
    test_weibo_id = '4593391122519060'

    print("=" * 80)
    print(f"测试获取微博完整内容: {test_weibo_id}")
    print("=" * 80)

    # 获取微博详情
    print("\n1. 请求API获取微博详情...")
    weibo_data = fetch_weibo_detail(test_weibo_id, cookie)

    if not weibo_data:
        print("✗ 获取失败")
        return 1

    print("✓ 获取成功")

    # 保存完整响应
    debug_file = Path(__file__).parent / 'debug_weibo_response.json'
    with open(debug_file, 'w', encoding='utf-8') as f:
        json.dump(weibo_data, f, ensure_ascii=False, indent=2)
    print(f"\nAPI响应已保存到: {debug_file}")

    # 检查数据结构
    print("\n2. 检查数据结构...")
    print(f"   isLongText: {weibo_data.get('isLongText')}")
    print(f"   有longText字段: {bool(weibo_data.get('longText'))}")
    print(f"   有text_raw字段: {bool(weibo_data.get('text_raw'))}")
    print(f"   有text字段: {bool(weibo_data.get('text'))}")

    if weibo_data.get('longText'):
        print(f"   longText字段keys: {list(weibo_data['longText'].keys())}")

    print("\n请查看 debug_weibo_response.json 文件了解完整数据结构")

    return 0

if __name__ == '__main__':
    sys.exit(main())
