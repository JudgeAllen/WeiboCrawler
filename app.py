#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博归档系统 - 动态Flask服务器
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, template_folder='generator/templates')
app.config['JSON_AS_ASCII'] = False

# 数据库路径
DB_PATH = 'data/database.db'
IMAGES_PATH = 'data/images'


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    """日期时间格式化"""
    if not value:
        return ''
    try:
        dt = datetime.strptime(value, '%a %b %d %H:%M:%S %z %Y')
        return dt.strftime(format)
    except:
        return value


def convert_pics_to_local(weibo_id, pic_urls, cursor):
    """将图片URL列表转换为本地路径"""
    if not pic_urls:
        return []

    local_pics = []
    for pic_url in pic_urls:
        # 从images表查询本地路径
        cursor.execute(
            'SELECT local_path FROM images WHERE weibo_id = ? AND url = ? AND downloaded = 1',
            (weibo_id, pic_url)
        )
        result = cursor.fetchone()
        if result and result['local_path']:
            local_pics.append(result['local_path'])
        else:
            # 如果没有本地文件，使用原URL
            local_pics.append(pic_url)
    return local_pics


# 注册过滤器
app.jinja_env.filters['datetimeformat'] = datetimeformat


@app.route('/')
def index():
    """首页"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取用户列表
    cursor.execute('SELECT * FROM users ORDER BY name')
    users = [dict(row) for row in cursor.fetchall()]

    # 获取微博总数
    cursor.execute('SELECT COUNT(*) FROM weibos')
    total_count = cursor.fetchone()[0]

    # 计算总页数
    total_pages = (total_count + per_page - 1) // per_page

    # 获取当前页微博
    cursor.execute('''
        SELECT w.*, u.name as user_name
        FROM weibos w
        LEFT JOIN users u ON w.uid = u.uid
        ORDER BY CAST(w.id AS INTEGER) DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset))

    weibos = []
    for row in cursor.fetchall():
        weibo = dict(row)
        # 解析图片JSON
        if weibo['pics']:
            pic_urls = json.loads(weibo['pics'])
            weibo['pics'] = convert_pics_to_local(weibo['id'], pic_urls, cursor)
        else:
            weibo['pics'] = []

        # 解析转发微博
        if weibo['retweeted_status']:
            try:
                weibo['retweeted_status'] = json.loads(weibo['retweeted_status'])
            except:
                weibo['retweeted_status'] = None

        weibos.append(weibo)

    conn.close()

    return render_template('index_dynamic.html',
                          weibos=weibos,
                          users=users,
                          total_count=total_count,
                          current_page=page,
                          total_pages=total_pages,
                          page_title='微博归档')


@app.route('/user/<uid>')
def user_page(uid):
    """用户页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取用户信息
    cursor.execute('SELECT * FROM users WHERE uid = ?', (uid,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "用户不存在", 404

    user = dict(user)

    # 获取该用户的微博总数
    cursor.execute('SELECT COUNT(*) FROM weibos WHERE uid = ?', (uid,))
    total_count = cursor.fetchone()[0]

    # 计算总页数
    total_pages = (total_count + per_page - 1) // per_page

    # 获取当前页微博
    cursor.execute('''
        SELECT w.*, u.name as user_name
        FROM weibos w
        LEFT JOIN users u ON w.uid = u.uid
        WHERE w.uid = ?
        ORDER BY CAST(w.id AS INTEGER) DESC
        LIMIT ? OFFSET ?
    ''', (uid, per_page, offset))

    weibos = []
    for row in cursor.fetchall():
        weibo = dict(row)
        # 解析图片JSON
        if weibo['pics']:
            pic_urls = json.loads(weibo['pics'])
            weibo['pics'] = convert_pics_to_local(weibo['id'], pic_urls, cursor)
        else:
            weibo['pics'] = []

        # 解析转发微博
        if weibo['retweeted_status']:
            try:
                weibo['retweeted_status'] = json.loads(weibo['retweeted_status'])
            except:
                weibo['retweeted_status'] = None

        weibos.append(weibo)

    conn.close()

    return render_template('user_dynamic.html',
                          user=user,
                          weibos=weibos,
                          total_count=total_count,
                          current_page=page,
                          total_pages=total_pages,
                          page_title=f"{user['name']}的微博")


@app.route('/post/<weibo_id>')
def post_page(weibo_id):
    """微博详情页"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT w.*, u.name as user_name
        FROM weibos w
        LEFT JOIN users u ON w.uid = u.uid
        WHERE w.id = ?
    ''', (weibo_id,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return "微博不存在", 404

    weibo = dict(row)

    # 解析图片JSON
    if weibo['pics']:
        pic_urls = json.loads(weibo['pics'])
        weibo['pics'] = convert_pics_to_local(weibo['id'], pic_urls, cursor)
    else:
        weibo['pics'] = []

    # 解析转发微博
    if weibo['retweeted_status']:
        try:
            weibo['retweeted_status'] = json.loads(weibo['retweeted_status'])
        except:
            weibo['retweeted_status'] = None

    conn.close()

    return render_template('post_dynamic.html',
                          weibo=weibo,
                          page_title=f"{weibo['user_name']}的微博")


@app.route('/api/search')
def search_api():
    """搜索API"""
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor()

    # 清理查询字符串，移除FTS特殊字符
    # FTS5特殊字符: " ( ) * + - < > @ ^ | ~
    import re
    clean_query = re.sub(r'["\(\)\*\+\-<>@\^|~!/:\[\]{}]', ' ', query)
    clean_query = ' '.join(clean_query.split())  # 移除多余空格

    if not clean_query:
        return jsonify([])

    # 使用FTS全文搜索
    try:
        cursor.execute('''
            SELECT w.id, w.content, w.created_at, u.name as user_name
            FROM weibos_fts f
            JOIN weibos w ON CAST(f.id AS TEXT) = CAST(w.id AS TEXT)
            LEFT JOIN users u ON w.uid = u.uid
            WHERE f.content MATCH ?
            ORDER BY CAST(w.id AS INTEGER) DESC
            LIMIT 20
        ''', (clean_query,))
    except Exception as e:
        # 如果FTS查询失败，回退到LIKE查询
        cursor.execute('''
            SELECT w.id, w.content, w.created_at, u.name as user_name
            FROM weibos w
            LEFT JOIN users u ON w.uid = u.uid
            WHERE w.content LIKE ?
            ORDER BY CAST(w.id AS INTEGER) DESC
            LIMIT 20
        ''', (f'%{query}%',))

    results = []
    for row in cursor.fetchall():
        results.append({
            'id': row['id'],
            'content': row['content'],
            'created_at': row['created_at'],
            'user_name': row['user_name']
        })

    conn.close()

    return jsonify(results)


@app.route('/date-range')
def date_range():
    """按日期范围筛选微博"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取日期参数
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # 如果没有提供日期，显示日期选择页面
    if not start_date or not end_date:
        # 获取最早和最晚的微博日期（按ID排序，ID越小越早）
        cursor.execute('SELECT created_at FROM weibos ORDER BY CAST(id AS INTEGER) ASC LIMIT 1')
        min_row = cursor.fetchone()

        cursor.execute('SELECT created_at FROM weibos ORDER BY CAST(id AS INTEGER) DESC LIMIT 1')
        max_row = cursor.fetchone()

        min_date = None
        max_date = None
        if min_row and max_row:
            try:
                min_dt = datetime.strptime(min_row[0], '%a %b %d %H:%M:%S %z %Y')
                max_dt = datetime.strptime(max_row[0], '%a %b %d %H:%M:%S %z %Y')
                min_date = min_dt.strftime('%Y-%m-%d')
                max_date = max_dt.strftime('%Y-%m-%d')
            except:
                pass

        conn.close()
        return render_template('date_range.html',
                             page_title='按日期筛选',
                             min_date=min_date,
                             max_date=max_date)

    # 转换日期格式用于查询
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        # 结束日期包含当天23:59:59
        end_dt = end_dt.replace(hour=23, minute=59, second=59)
    except:
        conn.close()
        return "日期格式错误", 400

    # 查询该日期范围内的微博总数
    cursor.execute('''
        SELECT COUNT(*) FROM weibos w
        WHERE datetime(substr(w.created_at, -4) || '-' ||
              CASE substr(w.created_at, 5, 3)
                  WHEN 'Jan' THEN '01'
                  WHEN 'Feb' THEN '02'
                  WHEN 'Mar' THEN '03'
                  WHEN 'Apr' THEN '04'
                  WHEN 'May' THEN '05'
                  WHEN 'Jun' THEN '06'
                  WHEN 'Jul' THEN '07'
                  WHEN 'Aug' THEN '08'
                  WHEN 'Sep' THEN '09'
                  WHEN 'Oct' THEN '10'
                  WHEN 'Nov' THEN '11'
                  WHEN 'Dec' THEN '12'
              END || '-' ||
              substr('0' || substr(w.created_at, 9, 2), -2) || ' ' ||
              substr(w.created_at, 12, 8))
        BETWEEN ? AND ?
    ''', (start_dt.strftime('%Y-%m-%d %H:%M:%S'), end_dt.strftime('%Y-%m-%d %H:%M:%S')))

    total = cursor.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page

    # 查询该日期范围内的微博
    cursor.execute('''
        SELECT w.*, u.name as user_name
        FROM weibos w
        LEFT JOIN users u ON w.uid = u.uid
        WHERE datetime(substr(w.created_at, -4) || '-' ||
              CASE substr(w.created_at, 5, 3)
                  WHEN 'Jan' THEN '01'
                  WHEN 'Feb' THEN '02'
                  WHEN 'Mar' THEN '03'
                  WHEN 'Apr' THEN '04'
                  WHEN 'May' THEN '05'
                  WHEN 'Jun' THEN '06'
                  WHEN 'Jul' THEN '07'
                  WHEN 'Aug' THEN '08'
                  WHEN 'Sep' THEN '09'
                  WHEN 'Oct' THEN '10'
                  WHEN 'Nov' THEN '11'
                  WHEN 'Dec' THEN '12'
              END || '-' ||
              substr('0' || substr(w.created_at, 9, 2), -2) || ' ' ||
              substr(w.created_at, 12, 8))
        BETWEEN ? AND ?
        ORDER BY CAST(w.id AS INTEGER) DESC
        LIMIT ? OFFSET ?
    ''', (start_dt.strftime('%Y-%m-%d %H:%M:%S'), end_dt.strftime('%Y-%m-%d %H:%M:%S'),
          per_page, offset))

    weibos = []
    for row in cursor.fetchall():
        weibo = dict(row)
        # 转换图片路径
        if weibo['pics']:
            pic_urls = json.loads(weibo['pics'])
            weibo['pics'] = convert_pics_to_local(weibo['id'], pic_urls, cursor)
        else:
            weibo['pics'] = []

        # 解析转发微博
        if weibo.get('retweeted_status'):
            try:
                weibo['retweeted_status'] = json.loads(weibo['retweeted_status'])
            except:
                weibo['retweeted_status'] = None

        weibos.append(weibo)

    conn.close()

    return render_template('date_range_results.html',
                         page_title=f'{start_date} 至 {end_date} 的微博',
                         weibos=weibos,
                         total=total,
                         page=page,
                         total_pages=total_pages,
                         start_date=start_date,
                         end_date=end_date,
                         datetimeformat=datetimeformat)


@app.route('/images/<path:filename>')
def serve_image(filename):
    """提供图片文件"""
    return send_from_directory(IMAGES_PATH, filename)


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """提供静态资源"""
    return send_from_directory('generator/templates/assets', filename)


if __name__ == '__main__':
    print("=" * 60)
    print("微博归档系统 - 动态模式")
    print("=" * 60)
    print("\n访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务器\n")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
