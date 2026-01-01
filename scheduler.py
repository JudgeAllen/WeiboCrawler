#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定时爬虫调度器 - 支持5-10分钟频繁更新"""

import time
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from crawler.weibo_spider import WeiboSpider

def run_crawler():
    """运行一次爬虫任务"""
    print(f"\n{'='*60}")
    print(f"定时任务触发: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    spider = WeiboSpider()
    try:
        start_time = time.time()
        spider.run()
        elapsed = time.time() - start_time
        print(f"\n本轮爬取耗时: {elapsed:.1f}秒")
    except Exception as e:
        print(f"爬虫运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        spider.close()

def main():
    """主函数 - 使用简单的循环定时"""
    try:
        # 尝试导入 schedule 库（可选）
        import schedule
        use_schedule = True
    except ImportError:
        print("提示: 安装 schedule 库可获得更好的定时功能")
        print("      pip install schedule")
        use_schedule = False

    # 从配置文件读取更新间隔（默认10分钟）
    interval_minutes = 10

    print("="*60)
    print("微博定时爬虫调度器")
    print("="*60)
    print(f"更新间隔: {interval_minutes} 分钟")
    print(f"启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("按 Ctrl+C 停止运行")
    print("="*60)

    if use_schedule:
        # 使用 schedule 库
        schedule.every(interval_minutes).minutes.do(run_crawler)

        # 立即运行一次
        run_crawler()

        # 持续运行
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        # 使用简单循环
        while True:
            run_crawler()

            # 显示下次运行时间
            next_run = time.time() + interval_minutes * 60
            next_run_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_run))
            print(f"\n下次运行时间: {next_run_str}")
            print(f"等待 {interval_minutes} 分钟...")

            # 等待指定时间
            time.sleep(interval_minutes * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n调度器已停止")
        sys.exit(0)
