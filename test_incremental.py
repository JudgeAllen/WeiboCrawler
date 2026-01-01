#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试增量更新功能"""

import sys
sys.path.insert(0, 'crawler')

from weibo_spider import WeiboSpider

print("=" * 60)
print("测试增量更新功能")
print("=" * 60)

spider = WeiboSpider('crawler/config.json')

try:
    # 测试每个用户的状态
    for user in spider.config['target_users']:
        uid = user['uid']
        name = user['name']

        print(f"\n检查用户: {name} ({uid})")

        cursor = spider.db_conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM weibos WHERE uid = ?', (uid,))
        count = cursor.fetchone()[0]

        if count > 0:
            cursor.execute('''
                SELECT created_at, content
                FROM weibos
                WHERE uid = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (uid,))
            latest = cursor.fetchone()
            print(f"  已有微博: {count} 条")
            print(f"  最新微博时间: {latest[0]}")
            print(f"  内容预览: {latest[1][:50]}...")
        else:
            print(f"  数据库中无该用户微博，将首次爬取")

    print("\n" + "=" * 60)
    print("现在开始运行增量更新...")
    print("=" * 60)

    spider.run()

finally:
    spider.close()
