#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证增量更新逻辑"""

import sqlite3

db_path = "data/database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("当前数据库状态")
print("=" * 60)

# 查询所有用户
cursor.execute("SELECT uid, name FROM users")
users = cursor.fetchall()

print(f"\n数据库中的用户: {len(users)} 个\n")

for uid, name in users:
    cursor.execute("SELECT COUNT(*) FROM weibos WHERE uid = ?", (uid,))
    count = cursor.fetchone()[0]
    print(f"  {name} ({uid}): {count} 条微博")

print("\n配置文件中的用户:")
import json
with open('crawler/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

for user in config['target_users']:
    uid = user['uid']
    name = user['name']

    cursor.execute("SELECT COUNT(*) FROM weibos WHERE uid = ?", (uid,))
    count = cursor.fetchone()[0]

    if count > 0:
        status = f"✓ 已有 {count} 条微博"
    else:
        status = "✗ 未爬取"

    print(f"  {name} ({uid}): {status}")

print("\n" + "=" * 60)
print("增量更新功能说明")
print("=" * 60)
print("""
新的增量更新逻辑:

1. 首次爬取用户 (数据库中无该用户)
   → 从第1页开始爬取所有微博
   → 直到没有更多微博为止

2. 增量更新 (数据库中已有该用户)
   → 从第1页开始检查新微博
   → 遇到已存在的微博则跳过
   → 连续40条都是已存在的微博时停止 (约2页)
   → 节省时间，只获取新发布的微博

3. 用户处理顺序
   → 按照 config.json 中的顺序依次处理
   → tombkeeper → t0mbkeeper

当前建议:
""")

# 检查t0mbkeeper是否需要爬取
cursor.execute("SELECT COUNT(*) FROM weibos WHERE uid = '6827625527'")
t0mb_count = cursor.fetchone()[0]

if t0mb_count == 0:
    print("  → 运行爬虫将会首次爬取 t0mbkeeper (约3598条微博)")
else:
    print(f"  → t0mbkeeper 已有 {t0mb_count} 条微博，运行爬虫将增量更新")

cursor.execute("SELECT COUNT(*) FROM weibos WHERE uid = '1401527553'")
tomb_count = cursor.fetchone()[0]
print(f"  → tombkeeper 已有 {tomb_count} 条微博，运行爬虫将增量更新")

conn.close()
