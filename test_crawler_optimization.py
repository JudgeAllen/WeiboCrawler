#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试爬虫优化功能"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from crawler.weibo_spider import WeiboSpider

def test_quick_check():
    """测试快速检查功能"""
    print("=" * 60)
    print("测试爬虫优化 - 快速检查功能")
    print("=" * 60)

    spider = WeiboSpider()

    try:
        # 读取配置的第一个用户
        target_users = spider.config.get('target_users', [])
        if not target_users:
            print("错误: 请在 config.json 中配置 target_users")
            return False

        user = target_users[0]
        uid = user.get('uid', '')
        name = user.get('name', '')

        if not uid:
            print("错误: 用户UID为空")
            return False

        # 检查数据库中是否已有微博
        cursor = spider.db_conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM weibos WHERE uid = ?', (uid,))
        existing_count = cursor.fetchone()[0]

        if existing_count == 0:
            print("提示: 该用户没有历史微博，请先运行一次完整爬取")
            print("      python run.py")
            return False

        print(f"\n测试用户: {name} ({uid})")
        print(f"数据库已有: {existing_count} 条微博\n")

        # 测试1: 快速检查功能
        print("【测试1】快速ID检查（仅检查前5条）")
        print("-" * 40)
        start_time = time.time()

        has_new = spider.quick_check_new_weibos(uid, max_check=5)

        elapsed = time.time() - start_time
        print(f"检查结果: {'发现新微博' if has_new else '无新微博'}")
        print(f"耗时: {elapsed:.2f}秒")
        print(f"{'✓' if elapsed < 3 else '✗'} 性能目标: < 3秒")

        # 测试2: 完整爬取一次（验证三层优化）
        print(f"\n【测试2】完整爬取流程（验证三层优化）")
        print("-" * 40)
        start_time = time.time()

        # 记录初始微博数
        cursor.execute('SELECT COUNT(*) FROM weibos WHERE uid = ?', (uid,))
        before_count = cursor.fetchone()[0]

        # 运行爬取
        spider.crawl_user(uid, name)

        # 检查结果
        cursor.execute('SELECT COUNT(*) FROM weibos WHERE uid = ?', (uid,))
        after_count = cursor.fetchone()[0]

        elapsed = time.time() - start_time
        new_count = after_count - before_count

        print(f"\n结果统计:")
        print(f"  新增微博: {new_count} 条")
        print(f"  总耗时: {elapsed:.2f}秒")

        if new_count == 0:
            print(f"  {'✓' if elapsed < 5 else '✗'} 无新微博性能目标: < 5秒")
        elif new_count <= 5:
            print(f"  {'✓' if elapsed < 10 else '✗'} 少量更新性能目标: < 10秒")
        else:
            print(f"  ℹ 大量新微博 ({new_count}条)，完整爬取正常")

        # 测试3: 再次运行（应触发超快模式）
        print(f"\n【测试3】再次运行（应触发超快模式）")
        print("-" * 40)
        start_time = time.time()

        spider.crawl_user(uid, name)

        elapsed = time.time() - start_time
        print(f"总耗时: {elapsed:.2f}秒")
        print(f"{'✓' if elapsed < 3 else '✗'} 超快模式目标: < 3秒")

        print("\n" + "=" * 60)
        print("✓ 优化功能测试完成")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        spider.close()

def test_performance_comparison():
    """性能对比测试（需要多次运行统计）"""
    print("\n" + "=" * 60)
    print("性能对比测试 - 10次运行统计")
    print("=" * 60)

    times = []
    spider = WeiboSpider()

    try:
        target_users = spider.config.get('target_users', [])
        if not target_users:
            print("错误: 请在 config.json 中配置 target_users")
            return

        user = target_users[0]
        uid = user.get('uid', '')
        name = user.get('name', '')

        print(f"测试用户: {name} ({uid})")
        print("连续运行10次，统计平均耗时...\n")

        for i in range(10):
            start_time = time.time()
            spider.crawl_user(uid, name)
            elapsed = time.time() - start_time
            times.append(elapsed)
            print(f"第 {i+1:2d} 次: {elapsed:.2f}秒")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\n统计结果:")
        print(f"  平均耗时: {avg_time:.2f}秒")
        print(f"  最快耗时: {min_time:.2f}秒")
        print(f"  最慢耗时: {max_time:.2f}秒")
        print(f"  {'✓' if avg_time < 3 else '✗'} 平均性能目标: < 3秒")

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
    finally:
        spider.close()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='测试爬虫优化功能')
    parser.add_argument('--perf', action='store_true', help='运行性能对比测试（10次）')
    args = parser.parse_args()

    if args.perf:
        test_performance_comparison()
    else:
        success = test_quick_check()
        sys.exit(0 if success else 1)
