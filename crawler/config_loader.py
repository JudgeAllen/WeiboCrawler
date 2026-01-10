#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置加载器 - 支持环境变量和配置文件"""

import os
import json
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """
    加载配置，优先使用环境变量

    优先级：
    1. 环境变量（VPS部署推荐）
    2. 配置文件（本地开发）
    """

    # 方式1：从环境变量加载（VPS部署）
    if os.getenv('WEIBO_COOKIE'):
        print("🔐 使用环境变量配置")

        config = {
            'cookie': os.getenv('WEIBO_COOKIE'),
            'target_users': [
                {
                    'uid': os.getenv('WEIBO_UID', '1401527553'),
                    'name': os.getenv('WEIBO_NAME', 'tombkeeper')
                }
            ],
            'download_images': os.getenv('DOWNLOAD_IMAGES', 'true').lower() == 'true',
            'image_path': os.getenv('IMAGE_PATH', '../data/images'),
            'database_path': os.getenv('DATABASE_PATH', '../data/database.db'),
            'delay': int(os.getenv('CRAWL_DELAY', '2')),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'force_update': os.getenv('FORCE_UPDATE', 'false').lower() == 'true',
            'scheduler': {
                'active_start_hour': int(os.getenv('SCHEDULER_START_HOUR', '7')),
                'active_end_hour': int(os.getenv('SCHEDULER_END_HOUR', '24')),
                'normal_interval_minutes': int(os.getenv('SCHEDULER_NORMAL_INTERVAL', '5')),
                'extended_interval_minutes': int(os.getenv('SCHEDULER_EXTENDED_INTERVAL', '15')),
                'no_update_threshold': int(os.getenv('SCHEDULER_THRESHOLD', '3'))
            }
        }

        return config

    # 方式2：从配置文件加载（本地开发）
    else:
        print("📄 使用配置文件")

        # 如果配置文件路径不是绝对路径，尝试在脚本所在目录查找
        if not os.path.isabs(config_path) and not os.path.exists(config_path):
            script_dir = Path(__file__).parent
            config_path = script_dir / config_path

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)


def save_config_template(output_path: str = 'config.json.example'):
    """生成配置文件模板"""
    template = {
        "target_users": [
            {
                "uid": "1401527553",
                "name": "tombkeeper"
            }
        ],
        "cookie": "YOUR_WEIBO_COOKIE_HERE",
        "download_images": True,
        "image_path": "../data/images",
        "database_path": "../data/database.db",
        "delay": 2,
        "max_retries": 3,
        "force_update": False,
        "scheduler": {
            "active_start_hour": 7,
            "active_end_hour": 24,
            "normal_interval_minutes": 5,
            "extended_interval_minutes": 15,
            "no_update_threshold": 3
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"✅ 配置模板已生成: {output_path}")


if __name__ == '__main__':
    # 测试配置加载
    config = load_config()
    print("\n当前配置:")
    print(f"- 用户: {config['target_users'][0]['name']}")
    print(f"- UID: {config['target_users'][0]['uid']}")
    print(f"- Cookie已设置: {'是' if config.get('cookie') else '否'}")
    print(f"- 数据库路径: {config['database_path']}")
