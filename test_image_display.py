#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试图片显示功能"""

import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://localhost:5000'

def test_image_display():
    """测试图片显示功能"""
    print("=== 测试图片显示功能 ===\n")

    # 1. 检查首页图片路径
    print("1. 检查首页图片路径...")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    images = soup.find_all('img', src=True)
    print(f"   找到 {len(images)} 张图片")

    if images:
        for i, img in enumerate(images[:5], 1):
            src = img.get('src')
            print(f"   {i}. {src}")

            # 检查路径格式
            if src.startswith('/images/'):
                print(f"      ✓ 路径格式正确")
            elif src.startswith('/https://') or src.startswith('https://'):
                print(f"      ✗ 错误：仍在使用外部URL")
                return False
            else:
                print(f"      ? 未知路径格式")

    # 2. 测试图片可访问性
    print("\n2. 测试图片文件可访问性...")
    test_images = []
    for img in images[:3]:
        src = img.get('src')
        if src.startswith('/images/'):
            test_images.append(src)

    for img_path in test_images:
        response = requests.head(f'{BASE_URL}{img_path}')
        if response.status_code == 200:
            size = response.headers.get('Content-Length', 'unknown')
            print(f"   ✓ {img_path} - {response.status_code} ({size} bytes)")
        else:
            print(f"   ✗ {img_path} - {response.status_code}")
            return False

    # 3. 检查用户页面图片
    print("\n3. 检查用户页面图片...")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    user_link = soup.find('a', class_='user-card')

    if user_link:
        uid = user_link['href'].split('/')[-1]
        response = requests.get(f'{BASE_URL}/user/{uid}')
        soup = BeautifulSoup(response.text, 'html.parser')

        user_images = soup.find_all('img', src=True)
        print(f"   用户页面找到 {len(user_images)} 张图片")

        for img in user_images[:3]:
            src = img.get('src')
            if src.startswith('/images/'):
                print(f"   ✓ {src}")
            else:
                print(f"   ✗ 错误路径: {src}")
                return False

    # 4. 检查详情页图片
    print("\n4. 检查详情页图片...")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    detail_link = soup.find('a', class_='detail-link')

    if detail_link:
        href = detail_link['href']
        response = requests.get(f'{BASE_URL}{href}')
        soup = BeautifulSoup(response.text, 'html.parser')

        detail_images = soup.find_all('img', src=True)
        print(f"   详情页找到 {len(detail_images)} 张图片")

        for img in detail_images[:3]:
            src = img.get('src')
            if src.startswith('/images/'):
                print(f"   ✓ {src}")
            else:
                print(f"   ✗ 错误路径: {src}")
                return False

    print("\n" + "=" * 60)
    print("✓ 所有图片显示功能测试通过！")
    print("=" * 60)
    return True

if __name__ == '__main__':
    try:
        success = test_image_display()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到服务器，请先运行: python app.py")
        exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
