#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博爬虫 - 抓取指定用户的所有微博
"""

import json
import os
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class WeiboSpider:
    """微博爬虫类"""

    def __init__(self, config_path: str = "config.json"):
        """初始化爬虫"""
        self.config = self._load_config(config_path)
        self.session = self._create_session()
        self.db_conn = self._init_database()

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        # 如果配置文件路径不是绝对路径，尝试在 crawler 目录查找
        if not os.path.isabs(config_path) and not os.path.exists(config_path):
            # 获取当前脚本所在目录
            script_dir = Path(__file__).parent
            config_path = script_dir / config_path

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _create_session(self) -> requests.Session:
        """创建带重试机制的会话"""
        session = requests.Session()
        retry = Retry(
            total=self.config.get('max_retries', 3),
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # 设置请求头
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': self.config.get('cookie', ''),
            'Referer': 'https://weibo.com'
        })
        return session

    def _init_database(self) -> sqlite3.Connection:
        """初始化数据库"""
        db_path_str = self.config.get('database_path', '../data/database.db')
        db_path = Path(db_path_str)

        # 如果是相对路径，相对于项目根目录（crawler的上级目录）
        if not db_path.is_absolute():
            # 获取项目根目录（crawler的父目录）
            project_root = Path(__file__).parent.parent
            db_path = project_root / db_path_str.lstrip('../')

        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                uid TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                followers_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建微博表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weibos (
                id TEXT PRIMARY KEY,
                uid TEXT,
                content TEXT,
                created_at TEXT,
                reposts_count INTEGER,
                comments_count INTEGER,
                attitudes_count INTEGER,
                source TEXT,
                pics TEXT,
                retweeted_status TEXT,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uid) REFERENCES users(uid)
            )
        ''')

        # 创建图片表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weibo_id TEXT,
                url TEXT,
                local_path TEXT,
                downloaded INTEGER DEFAULT 0,
                FOREIGN KEY (weibo_id) REFERENCES weibos(id)
            )
        ''')

        # 创建全文搜索索引
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS weibos_fts
            USING fts5(id, content, tokenize='porter unicode61')
        ''')

        conn.commit()
        return conn

    def fetch_user_info(self, uid: str) -> Optional[Dict]:
        """获取用户信息"""
        url = f'https://weibo.com/ajax/profile/info?uid={uid}'
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('ok') == 1:
                user_info = data['data']['user']
                return {
                    'uid': uid,
                    'name': user_info.get('screen_name', ''),
                    'description': user_info.get('description', ''),
                    'followers_count': user_info.get('followers_count', 0)
                }
        except Exception as e:
            print(f"获取用户信息失败 {uid}: {str(e)}")
        return None

    def fetch_weibo_list(self, uid: str, page: int = 1) -> List[Dict]:
        """获取用户微博列表"""
        url = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page={page}&feature=0'
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('ok') == 1:
                return data['data'].get('list', [])
        except Exception as e:
            print(f"获取微博列表失败 {uid} 第{page}页: {str(e)}")
        return []

    def download_image(self, url: str, weibo_id: str) -> Optional[str]:
        """下载图片"""
        if not self.config.get('download_images', True):
            return None

        try:
            # 创建图片保存目录
            image_path_str = self.config.get('image_path', '../data/images')
            image_dir = Path(image_path_str)

            # 如果是相对路径，相对于项目根目录
            if not image_dir.is_absolute():
                project_root = Path(__file__).parent.parent
                image_dir = project_root / image_path_str.lstrip('../')

            # 确保weibo_id是字符串
            weibo_id_str = str(weibo_id)
            weibo_dir = image_dir / weibo_id_str
            weibo_dir.mkdir(parents=True, exist_ok=True)

            # 获取文件名
            filename = url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]

            local_path = weibo_dir / filename

            # 如果文件已存在，跳过下载
            if local_path.exists():
                # 返回相对路径（从images目录开始）
                return f"images/{weibo_id_str}/{filename}"

            # 下载图片
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)

            # 返回相对路径（从images目录开始）
            return f"images/{weibo_id_str}/{filename}"

        except Exception as e:
            print(f"下载图片失败 {url}: {str(e)}")
        return None

    def weibo_exists(self, weibo_id: str) -> bool:
        """检查微博是否已存在"""
        cursor = self.db_conn.cursor()
        cursor.execute('SELECT 1 FROM weibos WHERE id = ? LIMIT 1', (weibo_id,))
        return cursor.fetchone() is not None

    def get_latest_weibo_id(self, uid: str) -> Optional[str]:
        """获取用户最新的微博ID"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT id FROM weibos
            WHERE uid = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (uid,))
        result = cursor.fetchone()
        return result[0] if result else None

    def quick_check_new_weibos(self, uid: str, max_check: int = 5) -> bool:
        """快速检查是否有新微博（仅检查前几条ID，不下载完整内容）"""
        try:
            weibos = self.fetch_weibo_list(uid, page=1)
            if not weibos:
                return False

            # 只检查前几条
            for weibo in weibos[:max_check]:
                weibo_id = weibo.get('id', '')
                if weibo_id and not self.weibo_exists(weibo_id):
                    return True

            return False
        except Exception as e:
            print(f"快速检查失败: {str(e)}")
            # 如果检查失败，保守起见返回True继续完整爬取
            return True

    def save_weibo(self, weibo: Dict, uid: str) -> bool:
        """保存微博到数据库，返回是否是新微博"""
        cursor = self.db_conn.cursor()

        # 提取微博信息
        weibo_id = weibo.get('id', '')

        # 检查是否已存在
        if self.weibo_exists(weibo_id):
            return False

        content = weibo.get('text_raw', weibo.get('text', ''))
        created_at = weibo.get('created_at', '')

        # 统计信息
        reposts_count = weibo.get('reposts_count', 0)
        comments_count = weibo.get('comments_count', 0)
        attitudes_count = weibo.get('attitudes_count', 0)
        source = weibo.get('source', '')

        # 图片信息 - 优先使用pic_ids构造URL，其次使用pics数组
        pic_urls = []
        pic_ids = weibo.get('pic_ids', [])
        if pic_ids:
            # 通过pic_id构造图片URL
            for pic_id in pic_ids:
                # 新浪图片URL格式: https://wx1.sinaimg.cn/large/{pic_id}.jpg
                pic_url = f'https://wx1.sinaimg.cn/large/{pic_id}.jpg'
                pic_urls.append(pic_url)
        else:
            # 降级方案：尝试从pics字段获取
            pics = weibo.get('pics', [])
            pic_urls = [pic.get('large', {}).get('url', '') for pic in pics]

        # 转发微博
        retweeted_status = weibo.get('retweeted_status')
        retweeted_text = ''
        if retweeted_status:
            retweeted_text = json.dumps(retweeted_status, ensure_ascii=False)

        # 插入微博
        cursor.execute('''
            INSERT INTO weibos
            (id, uid, content, created_at, reposts_count, comments_count,
             attitudes_count, source, pics, retweeted_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (weibo_id, uid, content, created_at, reposts_count,
              comments_count, attitudes_count, source,
              json.dumps(pic_urls, ensure_ascii=False), retweeted_text))

        # 插入全文搜索表
        cursor.execute('''
            INSERT INTO weibos_fts (id, content)
            VALUES (?, ?)
        ''', (weibo_id, content))

        # 下载并保存图片
        for pic_url in pic_urls:
            local_path = self.download_image(pic_url, weibo_id)
            cursor.execute('''
                INSERT INTO images (weibo_id, url, local_path, downloaded)
                VALUES (?, ?, ?, ?)
            ''', (weibo_id, pic_url, local_path, 1 if local_path else 0))

        self.db_conn.commit()
        return True

    def crawl_user(self, uid: str, name: str = ''):
        """爬取指定用户的所有微博（增量更新）"""
        print(f"\n开始爬取用户: {name} ({uid})")

        # 获取并保存用户信息
        user_info = self.fetch_user_info(uid)
        if user_info:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (uid, name, description, followers_count)
                VALUES (?, ?, ?, ?)
            ''', (user_info['uid'], user_info['name'],
                  user_info['description'], user_info['followers_count']))
            self.db_conn.commit()
            print(f"用户信息: {user_info['name']}, 粉丝数: {user_info['followers_count']}")

        # 检查数据库中是否已有该用户的微博
        cursor = self.db_conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM weibos WHERE uid = ?', (uid,))
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            print(f"数据库中已有 {existing_count} 条微博，开始增量更新...")
            mode = "incremental"

            # 快速检查：如果前5条都已存在，直接跳过（适合频繁更新场景）
            print(f"执行快速检查（检查前5条ID）...")
            has_new = self.quick_check_new_weibos(uid, max_check=5)
            if not has_new:
                print(f"快速检查：前5条都已存在，无新微博，跳过爬取")
                print(f"\n用户 {name} 爬取完成:")
                print(f"  新增微博: 0 条")
                print(f"  跳过已存在: 0 条")
                print(f"  数据库总计: {existing_count} 条")
                print(f"  [超快模式] 快速检查发现无更新")
                return
            else:
                print(f"快速检查：发现新微博，开始完整爬取...")
        else:
            print(f"首次爬取该用户，将获取所有微博...")
            mode = "full"

        # 爬取微博
        page = 1
        new_weibos = 0
        skipped_weibos = 0
        consecutive_existing = 0  # 连续遇到已存在微博的计数
        first_page_all_exist = False  # 第一页是否全部已存在

        while True:
            print(f"正在爬取第 {page} 页...")
            weibos = self.fetch_weibo_list(uid, page)

            if not weibos:
                print("没有更多微博了")
                break

            page_new_count = 0
            for weibo in weibos:
                is_new = self.save_weibo(weibo, uid)
                if is_new:
                    new_weibos += 1
                    page_new_count += 1
                    consecutive_existing = 0  # 重置计数
                else:
                    skipped_weibos += 1
                    consecutive_existing += 1

            print(f"第 {page} 页完成，新增 {page_new_count} 条，跳过 {len(weibos) - page_new_count} 条")

            # 优化：第一页如果全部已存在，立即退出（适合频繁更新场景）
            if page == 1 and page_new_count == 0 and len(weibos) > 0 and mode == "incremental":
                print(f"第一页全部已存在，无新微博，快速退出")
                first_page_all_exist = True
                break

            # 增量更新模式：如果连续2页都是已存在的微博，说明已经更新完毕
            if mode == "incremental" and consecutive_existing >= 40:  # 2页约40条
                print(f"连续遇到已存在的微博，增量更新完成")
                break

            # 延迟，避免请求过快
            time.sleep(self.config.get('delay', 2))
            page += 1

        print(f"\n用户 {name} 爬取完成:")
        print(f"  新增微博: {new_weibos} 条")
        print(f"  跳过已存在: {skipped_weibos} 条")
        print(f"  数据库总计: {existing_count + new_weibos} 条")
        if first_page_all_exist:
            print(f"  [快速模式] 第一页无更新，跳过后续检查")

    def run(self):
        """运行爬虫"""
        print("=" * 50)
        print("微博爬虫启动")
        print("=" * 50)

        target_users = self.config.get('target_users', [])

        if not target_users:
            print("错误: 请在 config.json 中配置 target_users")
            return

        for user in target_users:
            uid = user.get('uid', '')
            name = user.get('name', '')

            if uid:
                try:
                    self.crawl_user(uid, name)
                except Exception as e:
                    print(f"爬取用户 {name} 时出错: {str(e)}")
                    continue

        print("\n" + "=" * 50)
        print("所有用户爬取完成")
        print("=" * 50)

    def close(self):
        """关闭数据库连接"""
        if self.db_conn:
            self.db_conn.close()


if __name__ == '__main__':
    spider = WeiboSpider()
    try:
        spider.run()
    finally:
        spider.close()
