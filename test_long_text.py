#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试长文本微博抓取和显示"""

import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_long_text_extraction():
    """测试长文本提取逻辑"""
    print("=" * 60)
    print("测试长文本提取逻辑")
    print("=" * 60)

    # 模拟短文本微博
    short_weibo = {
        'text_raw': '这是一条短文本微博',
        'isLongText': False
    }

    # 模拟长文本微博（被截断）
    long_weibo_truncated = {
        'text_raw': '这是一条很长的微博，内容被截断了...',
        'isLongText': True,
        'longText': {
            'longTextContent': '这是一条很长的微博，这是完整的内容，包含了所有的文字，没有任何截断。'
        }
    }

    # 模拟长文本微博（没有longText字段，降级处理）
    long_weibo_no_long_text = {
        'text_raw': '这是一条很长的微博，但是没有longText字段',
        'isLongText': True
    }

    # 测试短文本
    print("\n测试1：短文本微博")
    if short_weibo.get('isLongText') and short_weibo.get('longText'):
        content = short_weibo['longText'].get('longTextContent', '')
    else:
        content = short_weibo.get('text_raw', short_weibo.get('text', ''))

    expected = '这是一条短文本微博'
    assert content == expected, f"短文本测试失败: {content} != {expected}"
    print(f"✓ 短文本内容: {content}")

    # 测试长文本
    print("\n测试2：长文本微博（有longText字段）")
    if long_weibo_truncated.get('isLongText') and long_weibo_truncated.get('longText'):
        content = long_weibo_truncated['longText'].get('longTextContent', '')
    else:
        content = long_weibo_truncated.get('text_raw', long_weibo_truncated.get('text', ''))

    expected = '这是一条很长的微博，这是完整的内容，包含了所有的文字，没有任何截断。'
    assert content == expected, f"长文本测试失败: {content} != {expected}"
    print(f"✓ 长文本内容: {content}")

    # 测试降级处理
    print("\n测试3：长文本微博（无longText字段，降级处理）")
    if long_weibo_no_long_text.get('isLongText') and long_weibo_no_long_text.get('longText'):
        content = long_weibo_no_long_text['longText'].get('longTextContent', '')
    else:
        content = long_weibo_no_long_text.get('text_raw', long_weibo_no_long_text.get('text', ''))

    expected = '这是一条很长的微博，但是没有longText字段'
    assert content == expected, f"降级处理测试失败: {content} != {expected}"
    print(f"✓ 降级处理内容: {content}")

    print("\n" + "=" * 60)
    print("✓ 所有长文本提取逻辑测试通过")
    print("=" * 60)
    return True


def test_database_long_text():
    """测试数据库中的长文本微博"""
    print("\n" + "=" * 60)
    print("检查数据库中的长文本微博")
    print("=" * 60)

    db_path = Path(__file__).parent / 'data' / 'database.db'
    if not db_path.exists():
        print("✗ 数据库文件不存在")
        return False

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # 查询2021-01-14 22:07的微博
    cursor.execute('''
        SELECT id, created_at, content, LENGTH(content) as content_length
        FROM weibos
        WHERE created_at LIKE '%Jan 14 22:07%2021%'
    ''')

    row = cursor.fetchone()
    if not row:
        print("✗ 未找到2021-01-14 22:07的微博")
        conn.close()
        return False

    weibo_id, created_at, content, content_length = row

    print(f"\n微博ID: {weibo_id}")
    print(f"发布时间: {created_at}")
    print(f"内容长度: {content_length} 字符")
    print(f"内容预览: {content[:100]}...")

    # 检查内容是否被截断（通常以"​​​"结尾表示被截断）
    is_truncated = content.endswith('​​​')

    if is_truncated:
        print("\n⚠ 警告：此微博内容可能被截断")
        print("  建议：重新运行爬虫以获取完整内容")
        print("  命令：cd crawler && python weibo_spider.py")
    else:
        print("\n✓ 微博内容完整")

    # 统计长文本微博数量
    cursor.execute('''
        SELECT COUNT(*) FROM weibos
        WHERE LENGTH(content) > 140
    ''')
    long_text_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM weibos')
    total_count = cursor.fetchone()[0]

    print(f"\n数据库统计:")
    print(f"  总微博数: {total_count:,}")
    print(f"  长文本微博: {long_text_count:,} ({long_text_count*100/total_count:.1f}%)")

    conn.close()

    return not is_truncated


def test_spider_import():
    """测试爬虫代码能否正常导入"""
    print("\n" + "=" * 60)
    print("测试爬虫代码导入")
    print("=" * 60)

    try:
        from crawler.weibo_spider import WeiboSpider
        print("✓ WeiboSpider 导入成功")

        # 测试初始化
        spider = WeiboSpider()
        print("✓ WeiboSpider 实例化成功")
        spider.close()

        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("长文本微博测试套件")
    print("=" * 60)

    results = []

    # 测试1: 长文本提取逻辑
    try:
        result = test_long_text_extraction()
        results.append(("长文本提取逻辑", result))
    except Exception as e:
        print(f"\n✗ 长文本提取逻辑测试失败: {e}")
        results.append(("长文本提取逻辑", False))

    # 测试2: 爬虫代码导入
    try:
        result = test_spider_import()
        results.append(("爬虫代码导入", result))
    except Exception as e:
        print(f"\n✗ 爬虫代码导入测试失败: {e}")
        results.append(("爬虫代码导入", False))

    # 测试3: 数据库长文本
    try:
        result = test_database_long_text()
        results.append(("数据库长文本检查", result))
    except Exception as e:
        print(f"\n✗ 数据库长文本检查失败: {e}")
        results.append(("数据库长文本检查", False))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过")
        print("\n建议：重新运行爬虫以更新数据库中的长文本微博")
        print("命令：cd crawler && python weibo_spider.py")
    else:
        print("✗ 部分测试失败")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
