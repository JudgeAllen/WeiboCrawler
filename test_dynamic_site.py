#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试动态网站功能"""

import requests
from bs4 import BeautifulSoup
import time

BASE_URL = 'http://localhost:5000'

def test_homepage():
    """测试首页"""
    print("\n=== 测试首页 ===")
    response = requests.get(BASE_URL)
    assert response.status_code == 200, "首页访问失败"

    soup = BeautifulSoup(response.text, 'html.parser')
    weibos = soup.find_all('article', class_='weibo-item')

    print(f"✓ 首页加载成功")
    print(f"✓ 显示 {len(weibos)} 条微博")

    # 验证排序（最新到最旧）
    if len(weibos) >= 2:
        first_id = int(weibos[0].get('data-id'))
        second_id = int(weibos[1].get('data-id'))
        assert first_id > second_id, "微博排序错误"
        print(f"✓ 微博按时间倒序排列 (最新ID: {first_id:,})")

def test_pagination():
    """测试分页功能"""
    print("\n=== 测试分页 ===")

    # 测试第1页
    response = requests.get(f'{BASE_URL}/?page=1')
    assert response.status_code == 200
    print("✓ 第1页加载成功")

    # 测试跳转到第100页
    response = requests.get(f'{BASE_URL}/?page=100')
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, 'html.parser')
    page_info = soup.find('span', class_='page-info')
    assert '100' in page_info.text, "页码显示错误"
    print("✓ 页面跳转功能正常 (第100页)")

    # 测试最后一页
    response = requests.get(f'{BASE_URL}/?page=636')
    assert response.status_code == 200
    print("✓ 最后一页加载成功")

def test_user_page():
    """测试用户页面"""
    print("\n=== 测试用户页面 ===")

    # 获取用户UID
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    user_link = soup.find('a', class_='user-card')

    if user_link:
        uid = user_link['href'].split('/')[-1]
        user_name = user_link.find('div', class_='user-name').text

        # 访问用户页面
        response = requests.get(f'{BASE_URL}/user/{uid}')
        assert response.status_code == 200
        print(f"✓ 用户页面加载成功: {user_name}")

        # 验证排序
        soup = BeautifulSoup(response.text, 'html.parser')
        weibos = soup.find_all('article', class_='weibo-item')

        if len(weibos) >= 2:
            first_id = int(weibos[0].get('data-id'))
            second_id = int(weibos[1].get('data-id'))
            assert first_id > second_id, "用户页微博排序错误"
            print(f"✓ 用户页微博按时间倒序排列")

def test_post_detail():
    """测试微博详情页"""
    print("\n=== 测试微博详情页 ===")

    # 从首页获取第一条微博ID
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    first_weibo = soup.find('article', class_='weibo-item')

    if first_weibo:
        weibo_id = first_weibo.get('data-id')

        # 访问详情页
        response = requests.get(f'{BASE_URL}/post/{weibo_id}')
        assert response.status_code == 200
        print(f"✓ 微博详情页加载成功 (ID: {weibo_id})")

def test_search():
    """测试搜索功能"""
    print("\n=== 测试搜索功能 ===")

    # 测试常用词搜索
    test_queries = ['安全', '微博', '手机', '雷军']

    for query in test_queries:
        response = requests.get(f'{BASE_URL}/api/search', params={'q': query})
        assert response.status_code == 200, f"搜索 '{query}' 失败"

        data = response.json()
        print(f"✓ 搜索 '{query}': {len(data)} 条结果")

        # 验证搜索结果排序
        if len(data) >= 2:
            first_id = int(data[0]['id'])
            last_id = int(data[-1]['id'])
            assert first_id >= last_id, f"搜索结果排序错误: {first_id} < {last_id}"

    print(f"✓ 搜索结果按时间倒序排列")

def test_ordering():
    """详细测试排序是否正确"""
    print("\n=== 详细测试排序 ===")

    # 获取第1页和最后一页的ID
    response = requests.get(f'{BASE_URL}/')
    soup = BeautifulSoup(response.text, 'html.parser')
    first_page_weibos = soup.find_all('article', class_='weibo-item')
    first_id = int(first_page_weibos[0].get('data-id'))

    response = requests.get(f'{BASE_URL}/?page=636')
    soup = BeautifulSoup(response.text, 'html.parser')
    last_page_weibos = soup.find_all('article', class_='weibo-item')
    last_id = int(last_page_weibos[-1].get('data-id'))

    print(f"  第1页第1条ID:  {first_id:,}")
    print(f"  第636页最后ID: {last_id:,}")

    assert first_id > last_id, f"排序错误: 第1页ID ({first_id}) 应该大于最后一页ID ({last_id})"
    print(f"✓ 全局排序正确 (最新到最旧)")

def main():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试动态网站功能")
    print("=" * 60)

    try:
        test_homepage()
        test_pagination()
        test_user_page()
        test_post_detail()
        test_search()
        test_ordering()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到服务器，请先运行: python app.py")
        return 1
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
