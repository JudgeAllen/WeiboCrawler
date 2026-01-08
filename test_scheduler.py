#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试智能调度器的逻辑"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scheduler import SmartScheduler


def test_scheduler_logic():
    """测试调度器逻辑"""
    scheduler = SmartScheduler()

    print("="*60)
    print("智能调度器逻辑测试")
    print("="*60)
    print(f"活跃时段: {scheduler.active_start_hour}:00 - {scheduler.active_end_hour}:00")
    print(f"正常间隔: {scheduler.normal_interval}分钟")
    print(f"延长间隔: {scheduler.extended_interval}分钟")
    print(f"延长阈值: 连续{scheduler.no_update_threshold}次无更新")
    print()

    # 模拟场景
    scenarios = [
        (False, "第1次检查：无新内容"),
        (False, "第2次检查：无新内容"),
        (False, "第3次检查：无新内容（达到阈值，应该延长）"),
        (False, "第4次检查：无新内容（保持延长状态）"),
        (False, "第5次检查：无新内容（保持延长状态）"),
        (True,  "第6次检查：发现新内容（应该恢复正常）"),
        (False, "第7次检查：无新内容（重新开始计数）"),
        (False, "第8次检查：无新内容"),
        (True,  "第9次检查：发现新内容（未达到阈值，保持正常）"),
    ]

    print("模拟运行场景：")
    print("-" * 60)

    for i, (has_new_content, description) in enumerate(scenarios, 1):
        print(f"\n{description}")
        print(f"  检查结果: {'✓ 有新内容' if has_new_content else '- 无新内容'}")

        # 更新间隔
        scheduler.update_interval(has_new_content)

        print(f"  无更新次数: {scheduler.no_update_count}")
        print(f"  当前间隔: {scheduler.current_interval}分钟")
        print(f"  是否延长: {'是' if scheduler.is_extended else '否'}")

        # 验证预期结果
        if i == 3:  # 第3次后应该延长
            assert scheduler.is_extended, "第3次无更新后应该延长间隔"
            assert scheduler.current_interval == scheduler.extended_interval
            print("  ✅ 验证通过：成功延长间隔")

        if i == 6:  # 发现新内容后应该恢复
            assert not scheduler.is_extended, "发现新内容后应该恢复正常间隔"
            assert scheduler.current_interval == scheduler.normal_interval
            assert scheduler.no_update_count == 0
            print("  ✅ 验证通过：成功恢复正常间隔")

        if i == 9:  # 未达到阈值，应该保持正常
            assert not scheduler.is_extended, "未达到阈值应该保持正常间隔"
            assert scheduler.current_interval == scheduler.normal_interval
            print("  ✅ 验证通过：保持正常间隔")

    print("\n" + "="*60)
    print("✅ 所有测试通过！")
    print("="*60)


def test_active_time():
    """测试活跃时间判断"""
    scheduler = SmartScheduler()

    print("\n" + "="*60)
    print("活跃时间测试")
    print("="*60)

    from datetime import datetime
    current_hour = datetime.now().hour
    is_active = scheduler.is_active_time()

    print(f"当前时间: {current_hour}:00")
    print(f"活跃时段: {scheduler.active_start_hour}:00 - {scheduler.active_end_hour}:00")
    print(f"是否在活跃时段: {is_active}")

    # 模拟不同时间
    print("\n模拟不同时间点：")
    for hour in [0, 6, 7, 12, 18, 23, 24]:
        # 临时修改当前时间（仅用于测试）
        original_func = datetime.now

        class FakeDateTime:
            def __init__(self, h):
                self.hour = h

        # 这里只是展示逻辑，实际判断基于当前时间
        if scheduler.active_start_hour < scheduler.active_end_hour:
            is_active = scheduler.active_start_hour <= hour < scheduler.active_end_hour
        else:
            is_active = hour >= scheduler.active_start_hour or hour < scheduler.active_end_hour

        status = "✓ 活跃" if is_active else "- 休眠"
        print(f"  {hour:02d}:00 → {status}")

    print("="*60)


if __name__ == '__main__':
    try:
        test_scheduler_logic()
        test_active_time()
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
