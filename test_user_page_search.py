#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试用户页面搜索功能"""

import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://localhost:5000'

def test_user_page_search():
    """测试用户页面搜索功能"""
    print("=== 测试用户页面搜索功能 ===\n")

    # 1. 获取用户UID
    print("1. 获取用户列表...")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    user_links = soup.find_all('a', class_='user-card')

    if not user_links:
        print("✗ 未找到用户")
        return False

    for user_link in user_links[:2]:  # 测试前2个用户
        uid = user_link['href'].split('/')[-1]
        user_name = user_link.find('div', class_='user-name').text

        print(f"\n2. 测试用户: {user_name} (UID: {uid})")

        # 2. 访问用户页面
        response = requests.get(f'{BASE_URL}/user/{uid}')
        if response.status_code != 200:
            print(f"✗ 用户页面访问失败")
            return False

        print(f"✓ 用户页面加载成功")

        # 3. 检查搜索元素
        soup = BeautifulSoup(response.text, 'html.parser')

        # 检查搜索面板
        search_panel = soup.find('div', id='search-panel')
        if not search_panel:
            print("✗ 搜索面板未找到")
            return False
        print("✓ 搜索面板存在")

        # 检查搜索输入框
        search_input = soup.find('input', id='search-input')
        if not search_input:
            print("✗ 搜索输入框未找到")
            return False
        print("✓ 搜索输入框存在")

        # 检查搜索按钮
        search_toggle = soup.find('a', id='search-toggle')
        if not search_toggle:
            print("✗ 搜索按钮未找到")
            return False
        print("✓ 搜索按钮存在")

        # 检查搜索脚本
        scripts = soup.find_all('script', src=True)
        search_script_found = False
        for script in scripts:
            if 'search_dynamic.js' in script.get('src', ''):
                search_script_found = True
                break

        if not search_script_found:
            print("✗ 搜索脚本未加载")
            return False
        print("✓ 搜索脚本已加载 (search_dynamic.js)")

        # 检查base模板
        footer = soup.find('footer', class_='site-footer')
        if footer and '动态模式' in footer.text:
            print("✓ 使用正确的base_dynamic.html模板")
        else:
            print("✗ 模板继承错误，应使用base_dynamic.html")
            return False

    # 4. 测试搜索API
    print("\n3. 测试搜索API...")
    test_queries = ['微博', '安全', '手机']

    for query in test_queries:
        response = requests.get(f'{BASE_URL}/api/search', params={'q': query})
        if response.status_code != 200:
            print(f"✗ 搜索API失败: {query}")
            return False

        data = response.json()
        print(f"✓ 搜索 '{query}': {len(data)} 条结果")

    print("\n" + "=" * 60)
    print("✓ 所有用户页面搜索功能测试通过！")
    print("=" * 60)
    return True

if __name__ == '__main__':
    try:
        success = test_user_page_search()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到服务器，请先运行: python app.py")
        exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
