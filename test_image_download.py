#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试图片下载功能"""

import sys
sys.path.insert(0, 'crawler')

from weibo_spider import WeiboSpider

print("=" * 60)
print("测试图片下载功能")
print("=" * 60)

spider = WeiboSpider('crawler/config.json')

try:
    # 测试下载一张图片
    test_url = "https://wx1.sinaimg.cn/large/53899d01ly1i8t3434f35j20mf0cf106.jpg"
    test_weibo_id = "5249636208215413"

    print(f"\n测试下载图片:")
    print(f"URL: {test_url}")
    print(f"微博ID: {test_weibo_id}")

    result = spider.download_image(test_url, test_weibo_id)

    if result:
        print(f"\n✓ 下载成功!")
        print(f"保存路径: {result}")
    else:
        print(f"\n✗ 下载失败")

finally:
    spider.close()
