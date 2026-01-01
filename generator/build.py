#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态网站生成器 - 将数据库中的微博生成静态HTML页面
"""

import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from jinja2 import Environment, FileSystemLoader


class SiteGenerator:
    """静态网站生成器"""

    def __init__(self, db_path: str = "../data/database.db", output_dir: str = "../site"):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.db_conn = sqlite3.connect(db_path)
        self.db_conn.row_factory = sqlite3.Row

        # 设置Jinja2模板环境
        template_dir = Path(__file__).parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.env.filters['datetimeformat'] = self.datetimeformat

    def datetimeformat(self, value: str, format: str = '%Y-%m-%d %H:%M') -> str:
        """日期时间格式化过滤器"""
        if not value:
            return ''
        try:
            # 微博时间格式示例: "Tue Dec 31 12:00:00 +0800 2024"
            dt = datetime.strptime(value, '%a %b %d %H:%M:%S %z %Y')
            return dt.strftime(format)
        except:
            return value

    def get_users(self) -> List[Dict]:
        """获取所有用户"""
        cursor = self.db_conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY name')
        return [dict(row) for row in cursor.fetchall()]

    def get_weibos(self, uid: str = None, limit: int = None, offset: int = 0) -> List[Dict]:
        """获取微博列表"""
        cursor = self.db_conn.cursor()

        if uid:
            query = '''
                SELECT w.*, u.name as user_name
                FROM weibos w
                LEFT JOIN users u ON w.uid = u.uid
                WHERE w.uid = ?
                ORDER BY CAST(w.id AS INTEGER) DESC
            '''
            params = [uid]
        else:
            query = '''
                SELECT w.*, u.name as user_name
                FROM weibos w
                LEFT JOIN users u ON w.uid = u.uid
                ORDER BY CAST(w.id AS INTEGER) DESC
            '''
            params = []

        if limit:
            query += f' LIMIT {limit} OFFSET {offset}'

        cursor.execute(query, params)
        weibos = []

        for row in cursor.fetchall():
            weibo = dict(row)
            # 解析图片JSON
            if weibo['pics']:
                weibo['pics'] = json.loads(weibo['pics'])
            else:
                weibo['pics'] = []

            # 解析转发微博
            if weibo['retweeted_status']:
                try:
                    weibo['retweeted_status'] = json.loads(weibo['retweeted_status'])
                except:
                    weibo['retweeted_status'] = None

            weibos.append(weibo)

        return weibos

    def get_weibo_by_id(self, weibo_id: str) -> Dict:
        """获取单条微博"""
        weibos = self.get_weibos()
        for weibo in weibos:
            if weibo['id'] == weibo_id:
                return weibo
        return None

    def prepare_search_index(self) -> List[Dict]:
        """准备搜索索引数据"""
        weibos = self.get_weibos()
        index_data = []

        for weibo in weibos:
            index_data.append({
                'id': weibo['id'],
                'content': weibo['content'],
                'created_at': weibo['created_at'],
                'user_name': weibo['user_name']
            })

        return index_data

    def generate_index_page(self, total_count: int, users: List[Dict]):
        """生成首页（带分页）"""
        template = self.env.get_template('index.html')
        per_page = 50  # 每页显示50条
        total_pages = (total_count + per_page - 1) // per_page

        # 生成首页
        weibos = self.get_weibos(limit=per_page, offset=0)
        html = template.render(
            weibos=weibos,
            users=users,
            total_count=total_count,
            current_page=1,
            total_pages=total_pages,
            page_title='微博归档'
        )
        output_file = self.output_dir / 'index.html'
        output_file.write_text(html, encoding='utf-8')

        # 生成其他页面
        for page in range(2, total_pages + 1):
            offset = (page - 1) * per_page
            weibos = self.get_weibos(limit=per_page, offset=offset)
            html = template.render(
                weibos=weibos,
                users=users,
                total_count=total_count,
                current_page=page,
                total_pages=total_pages,
                page_title=f'微博归档 - 第{page}页'
            )
            output_file = self.output_dir / f'page-{page}.html'
            output_file.write_text(html, encoding='utf-8')

        print(f"生成首页: {total_pages} 页")

    def generate_user_pages(self, users: List[Dict]):
        """生成用户页面（带分页）"""
        user_dir = self.output_dir / 'users'
        user_dir.mkdir(parents=True, exist_ok=True)

        template = self.env.get_template('user.html')
        per_page = 50

        for user in users:
            # 获取该用户的微博总数
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM weibos WHERE uid = ?', (user['uid'],))
            total_count = cursor.fetchone()[0]

            if total_count == 0:
                continue

            total_pages = (total_count + per_page - 1) // per_page

            # 生成第一页
            weibos = self.get_weibos(uid=user['uid'], limit=per_page, offset=0)
            html = template.render(
                user=user,
                weibos=weibos,
                total_count=total_count,
                current_page=1,
                total_pages=total_pages,
                page_title=f"{user['name']}的微博"
            )
            output_file = user_dir / f"{user['uid']}.html"
            output_file.write_text(html, encoding='utf-8')

            # 生成其他页面
            for page in range(2, total_pages + 1):
                offset = (page - 1) * per_page
                weibos = self.get_weibos(uid=user['uid'], limit=per_page, offset=offset)
                html = template.render(
                    user=user,
                    weibos=weibos,
                    total_count=total_count,
                    current_page=page,
                    total_pages=total_pages,
                    page_title=f"{user['name']}的微博 - 第{page}页"
                )
                output_file = user_dir / f"{user['uid']}-page-{page}.html"
                output_file.write_text(html, encoding='utf-8')

            print(f"生成用户页: {user['name']} ({total_count} 条微博, {total_pages} 页)")

    def generate_post_pages(self, weibos: List[Dict]):
        """生成单个微博详情页"""
        post_dir = self.output_dir / 'posts'
        post_dir.mkdir(parents=True, exist_ok=True)

        template = self.env.get_template('post.html')

        for weibo in weibos:
            html = template.render(
                weibo=weibo,
                page_title=f"{weibo['user_name']}的微博"
            )

            output_file = post_dir / f"{weibo['id']}.html"
            output_file.write_text(html, encoding='utf-8')

        print(f"生成微博详情页: {len(weibos)} 个")

    def copy_assets(self):
        """复制静态资源"""
        # 复制CSS和JS
        assets_src = Path(__file__).parent / 'templates' / 'assets'
        assets_dst = self.output_dir / 'assets'

        if assets_src.exists():
            if assets_dst.exists():
                shutil.rmtree(assets_dst)
            shutil.copytree(assets_src, assets_dst)
            print("复制静态资源完成")

        # 复制图片
        images_src = Path(__file__).parent.parent / 'data' / 'images'
        images_dst = self.output_dir / 'images'

        if images_src.exists():
            if images_dst.exists():
                shutil.rmtree(images_dst)
            shutil.copytree(images_src, images_dst)
            print("复制图片完成")

    def generate_search_index(self, weibos: List[Dict]):
        """生成搜索索引JSON"""
        index_data = self.prepare_search_index()

        search_index_file = self.output_dir / 'assets' / 'search-index.json'
        search_index_file.parent.mkdir(parents=True, exist_ok=True)

        with open(search_index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        print(f"生成搜索索引: {len(index_data)} 条记录")

    def build(self):
        """构建静态网站"""
        print("=" * 50)
        print("开始生成静态网站")
        print("=" * 50)

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 获取数据统计
        users = self.get_users()
        cursor = self.db_conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM weibos')
        total_weibos = cursor.fetchone()[0]

        print(f"\n数据统计:")
        print(f"  用户数: {len(users)}")
        print(f"  微博数: {total_weibos}")

        # 生成页面
        print("\n生成页面:")
        self.generate_index_page(total_weibos, users)
        self.generate_user_pages(users)

        # 复制静态资源（必须先执行，避免覆盖搜索索引）
        self.copy_assets()

        # 生成微博详情页（获取所有微博）
        print("生成微博详情页...")
        all_weibos = self.get_weibos()
        self.generate_post_pages(all_weibos)

        # 生成搜索索引（必须在copy_assets之后）
        self.generate_search_index(all_weibos)

        print("\n" + "=" * 50)
        print(f"网站生成完成！输出目录: {self.output_dir.absolute()}")
        print("=" * 50)

    def close(self):
        """关闭数据库连接"""
        if self.db_conn:
            self.db_conn.close()


if __name__ == '__main__':
    generator = SiteGenerator()
    try:
        generator.build()
    finally:
        generator.close()
