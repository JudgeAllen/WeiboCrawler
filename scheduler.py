#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能调度器 - 支持自适应轮询间隔"""

import time
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from crawler.weibo_spider import WeiboSpider


class SmartScheduler:
    """智能调度器"""

    def __init__(self, config_path='crawler/config.json'):
        """初始化调度器"""
        self.config = self._load_config(config_path)
        self.scheduler_config = self.config.get('scheduler', {})

        # 调度参数
        self.active_start_hour = self.scheduler_config.get('active_start_hour', 7)
        self.active_end_hour = self.scheduler_config.get('active_end_hour', 24)
        self.normal_interval = self.scheduler_config.get('normal_interval_minutes', 5)
        self.extended_interval = self.scheduler_config.get('extended_interval_minutes', 15)
        self.no_update_threshold = self.scheduler_config.get('no_update_threshold', 3)

        # 状态变量
        self.no_update_count = 0  # 连续无更新次数
        self.current_interval = self.normal_interval  # 当前间隔（分钟）
        self.is_extended = False  # 是否已经延长

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        # 如果配置文件路径不是绝对路径，相对于脚本所在目录
        if not Path(config_path).is_absolute():
            config_path = Path(__file__).parent / config_path

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def is_active_time(self) -> bool:
        """检查当前是否在活跃时间段"""
        current_hour = datetime.now().hour

        # 处理跨0点的情况
        if self.active_start_hour < self.active_end_hour:
            # 例如: 7-24 (早上7点到晚上12点)
            return self.active_start_hour <= current_hour < self.active_end_hour
        else:
            # 例如: 22-6 (晚上10点到早上6点)
            return current_hour >= self.active_start_hour or current_hour < self.active_end_hour

    def run_crawler(self) -> bool:
        """运行一次爬虫任务，返回是否有新内容"""
        print(f"\n{'='*60}")
        print(f"定时任务触发: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"当前间隔: {self.current_interval}分钟 | 无更新次数: {self.no_update_count}")
        print(f"{'='*60}")

        spider = WeiboSpider(config_path='crawler/config.json')
        has_new_content = False

        try:
            start_time = time.time()

            # 获取爬取前的微博总数
            import sqlite3
            db_path = Path(__file__).parent / self.config.get('database_path', 'data/database.db').lstrip('../')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM weibos')
            count_before = cursor.fetchone()[0]
            conn.close()

            # 运行爬虫
            spider.run()

            # 获取爬取后的微博总数
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM weibos')
            count_after = cursor.fetchone()[0]
            conn.close()

            # 判断是否有新内容
            new_count = count_after - count_before
            has_new_content = new_count > 0

            elapsed = time.time() - start_time

            if has_new_content:
                print(f"\n✓ 发现 {new_count} 条新微博")
            else:
                print(f"\n- 没有新微博")

            print(f"本轮爬取耗时: {elapsed:.1f}秒")

        except Exception as e:
            print(f"爬虫运行出错: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            spider.close()

        return has_new_content

    def update_interval(self, has_new_content: bool):
        """根据爬取结果更新间隔"""
        if has_new_content:
            # 有新内容，重置计数器，恢复到正常间隔
            self.no_update_count = 0
            if self.is_extended:
                print(f"\n>>> 发现新内容，间隔恢复为 {self.normal_interval} 分钟")
                self.current_interval = self.normal_interval
                self.is_extended = False
        else:
            # 无新内容，增加计数
            self.no_update_count += 1

            # 如果连续N次无更新且未延长过，则延长间隔
            if self.no_update_count >= self.no_update_threshold and not self.is_extended:
                print(f"\n>>> 连续 {self.no_update_count} 次无更新，间隔延长为 {self.extended_interval} 分钟")
                self.current_interval = self.extended_interval
                self.is_extended = True

    def run(self):
        """主循环"""
        print("="*60)
        print("微博智能调度器")
        print("="*60)
        print(f"活跃时间: {self.active_start_hour}:00 - {self.active_end_hour}:00")
        print(f"正常间隔: {self.normal_interval} 分钟")
        print(f"延长间隔: {self.extended_interval} 分钟")
        print(f"延长阈值: 连续 {self.no_update_threshold} 次无更新")
        print(f"启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("按 Ctrl+C 停止运行")
        print("="*60)

        while True:
            # 检查是否在活跃时间段
            if not self.is_active_time():
                current_hour = datetime.now().hour
                # 计算到活跃时间开始还有多久
                if current_hour < self.active_start_hour:
                    hours_to_wait = self.active_start_hour - current_hour
                else:
                    hours_to_wait = 24 - current_hour + self.active_start_hour

                next_active = time.time() + hours_to_wait * 3600
                next_active_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_active))

                print(f"\n当前时间 {datetime.now().hour}:00 不在活跃时段")
                print(f"下次活跃时间: {next_active_str}")
                print(f"等待 {hours_to_wait} 小时...")

                # 等待到活跃时间（每小时检查一次）
                time.sleep(3600)
                continue

            # 运行爬虫
            has_new_content = self.run_crawler()

            # 更新间隔
            self.update_interval(has_new_content)

            # 显示下次运行时间
            next_run = time.time() + self.current_interval * 60
            next_run_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_run))
            print(f"\n下次运行时间: {next_run_str}")
            print(f"等待 {self.current_interval} 分钟...")

            # 等待指定时间
            time.sleep(self.current_interval * 60)


def main():
    """主函数"""
    scheduler = SmartScheduler()
    scheduler.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n调度器已停止")
        sys.exit(0)
