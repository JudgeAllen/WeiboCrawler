#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库中的数据"""

import sqlite3
import json
from pathlib import Path

db_path = Path("data/database.db")

if not db_path.exists():
    print("数据库文件不存在！")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 查询用户信息
print("=" * 60)
print("用户信息:")
print("=" * 60)
cursor.execute("SELECT uid, name, description, followers_count FROM users")
users = cursor.fetchall()

if not users:
    print("没有用户数据！")
else:
    for user in users:
        uid, name, desc, followers = user
        print(f"\nUID: {uid}")
        print(f"用户名: {name}")
        print(f"粉丝数: {followers}")
        print(f"简介: {desc[:100] if desc else '无'}...")

# 查询每个用户的微博数量
print("\n" + "=" * 60)
print("微博统计:")
print("=" * 60)
cursor.execute("""
    SELECT u.name, u.uid, COUNT(w.id) as weibo_count
    FROM users u
    LEFT JOIN weibos w ON u.uid = w.uid
    GROUP BY u.uid
""")
stats = cursor.fetchall()

for stat in stats:
    name, uid, count = stat
    print(f"{name} ({uid}): {count} 条微博")

# 查询总微博数
cursor.execute("SELECT COUNT(*) FROM weibos")
total = cursor.fetchone()[0]
print(f"\n总计: {total} 条微博")

# 查询图片数量
cursor.execute("SELECT COUNT(*) FROM images WHERE downloaded = 1")
image_count = cursor.fetchone()[0]
print(f"已下载图片: {image_count} 张")

# 显示最新的几条微博
print("\n" + "=" * 60)
print("最新微博 (前5条):")
print("=" * 60)
cursor.execute("""
    SELECT w.id, u.name, w.content, w.created_at
    FROM weibos w
    LEFT JOIN users u ON w.uid = u.uid
    ORDER BY w.created_at DESC
    LIMIT 5
""")
recent = cursor.fetchall()

for i, weibo in enumerate(recent, 1):
    weibo_id, user_name, content, created_at = weibo
    print(f"\n{i}. {user_name} - {created_at}")
    print(f"   内容: {content[:80]}...")
    print(f"   ID: {weibo_id}")

conn.close()
