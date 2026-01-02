# 微博归档系统

一个将微博博主的所有微博抓取并生成静态网站的工具，方便本地查询和浏览，类似 [tombkeeper.io](https://tombkeeper.io) 的形式。

## 功能特点

- 🕷️ **自动抓取**: 抓取指定博主的所有微博内容
- 💾 **完整存储**: 保存微博文字、图片、转发等完整信息
- 🔍 **全文搜索**: 支持关键词搜索，快速定位内容
- 📱 **响应式设计**: 适配桌面和移动设备
- 🚀 **双模式运行**: 支持静态站点生成和动态Flask服务器两种模式
- 📊 **数据库存储**: 使用SQLite存储，方便数据管理
- 🔄 **增量更新**: 智能识别已抓取内容，仅获取新微博

## 项目结构

```
tombkeeper/
├── crawler/              # 爬虫模块
│   ├── config.json      # 配置文件
│   └── weibo_spider.py  # 微博爬虫
├── data/                # 数据存储
│   ├── database.db      # SQLite数据库
│   └── images/          # 图片文件
├── generator/           # 网站生成器
│   ├── build.py         # 静态站点构建脚本
│   └── templates/       # HTML模板
│       ├── base.html            # 静态模板基础
│       ├── base_dynamic.html   # 动态模板基础
│       ├── index.html           # 静态首页
│       ├── index_dynamic.html  # 动态首页
│       ├── user.html            # 静态用户页
│       ├── user_dynamic.html   # 动态用户页
│       ├── post.html            # 静态详情页
│       ├── post_dynamic.html   # 动态详情页
│       └── assets/      # 静态资源
│           ├── style.css
│           ├── search.js         # 静态模式搜索
│           └── search_dynamic.js # 动态模式搜索
├── site/                # 生成的静态网站
├── app.py               # Flask动态服务器
└── requirements.txt     # Python依赖
```

## 安装使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置爬虫

编辑 `crawler/config.json`，填入要抓取的博主信息和你的微博Cookie：

```json
{
  "target_users": [
    {
      "uid": "1401527553",
      "name": "tombkeeper"
    }
  ],
  "cookie": "YOUR_WEIBO_COOKIE_HERE",
  "download_images": true,
  "image_path": "../data/images",
  "database_path": "../data/database.db",
  "delay": 2,
  "max_retries": 3
}
```

#### 如何获取微博Cookie：

1. 登录微博网页版 (weibo.com)
2. 打开浏览器开发者工具 (F12)
3. 切换到 Network 标签
4. 刷新页面，找到任意请求
5. 在请求头中找到 `Cookie` 字段，复制完整内容
6. 粘贴到 config.json 的 `cookie` 字段

#### 如何获取用户UID：

1. 打开用户主页，查看URL
2. URL格式: `https://weibo.com/u/1401527553` 或 `https://weibo.com/1401527553`
3. 数字部分就是UID

### 3. 运行爬虫

#### 单次运行

```bash
python run.py
```

爬虫会自动：
- 抓取用户信息
- 获取所有微博内容（增量更新，自动跳过已存在微博）
- 下载微博图片
- 保存到SQLite数据库

#### 定时自动更新（推荐）

本系统专门针对 **5-10分钟频繁更新** 场景进行了优化，在无新内容时可在2秒内完成检查。

**方式1：使用Python调度器（跨平台）**

```bash
python scheduler.py
```

默认每10分钟自动运行一次爬虫。

**方式2：使用系统定时任务**

Windows - 任务计划程序（详细步骤见 [Windows计划任务指南](WINDOWS_TASK_SCHEDULER.md)）:
1. 打开"任务计划程序"（`Win+R` → 输入 `taskschd.msc`）
2. 创建基本任务 → 触发器设为"每10分钟"
3. 操作 → 启动程序 → 选择 `run_crawler_scheduled.bat`
4. 高级设置 → 配置重复间隔和运行条件

快速命令（管理员CMD）：
```cmd
schtasks /create /tn "微博爬虫定时更新" /tr "f:\Git\tombkeeper\run_crawler_scheduled.bat" /sc minute /mo 10 /st 00:00 /du 9999:00 /f
```

Linux/Mac - crontab:
```bash
# 每10分钟执行一次
*/10 * * * * cd /path/to/tombkeeper && cd crawler && python weibo_spider.py >> ../logs/crawler.log 2>&1
```

**性能优势**：
- 无新微博时：~2秒完成（快速ID检查）
- 少量新微博：~5秒完成（仅爬取第一页）
- 大量新微博：~12秒完成（智能增量更新）

详见 [爬虫优化文档](CRAWLER_OPTIMIZATION.md)

### 4. 选择运行模式

#### 方式一：动态模式（推荐本地使用）

直接运行Flask服务器，实时从数据库读取数据：

```bash
python app.py
```

然后在浏览器访问: `http://localhost:5000`

**优点**：
- 无需生成静态文件，直接查看最新数据
- 适合频繁更新的场景
- 搜索使用SQLite FTS全文搜索，性能更好

**缺点**：
- 需要Python环境运行
- 不适合部署到静态托管服务

#### 方式二：静态模式（推荐部署使用）

生成静态HTML网站：

```bash
cd generator
python build.py
```

生成器会：
- 读取数据库中的微博数据
- 生成静态HTML页面（支持分页）
- 创建搜索索引
- 复制静态资源和图片

然后使用任意HTTP服务器运行：

```bash
# Python方式
cd site
python -m http.server 8000

# 或 Node.js方式
cd site
npx http-server -p 8000
```

浏览器访问: `http://localhost:8000`

**优点**：
- 纯静态文件，可部署到任何静态托管服务
- 无需后端，访问速度快
- 可离线浏览

**缺点**：
- 每次更新数据后需要重新生成
- 生成时间较长（数据量大时）

## 功能说明

### 首页
- 显示所有博主列表
- 展示最新微博（每页50条，支持翻页）
- 支持搜索功能

### 用户页
- 显示该用户的所有微博
- 按微博ID倒序排列（最新的在前）
- 显示用户信息和统计
- 支持分页浏览

### 微博详情页
- 显示完整的微博内容
- 显示图片（如有）
- 显示转发微博（如有）
- 显示互动统计

### 搜索功能

**动态模式**：
- 使用SQLite FTS5全文搜索
- 实时查询数据库
- 支持中文分词
- 最多返回20条结果

**静态模式**：
- 使用预生成的JSON索引
- 客户端JavaScript搜索
- 高亮显示匹配内容
- 按相关度排序

## 数据库结构

### users 表
- uid: 用户ID
- name: 用户名
- description: 个人简介
- followers_count: 粉丝数

### weibos 表
- id: 微博ID
- uid: 用户ID
- content: 微博内容
- created_at: 发布时间
- reposts_count: 转发数
- comments_count: 评论数
- attitudes_count: 点赞数
- source: 来源
- pics: 图片URL列表 (JSON)
- retweeted_status: 转发微博 (JSON)

### images 表
- weibo_id: 微博ID
- url: 原始URL
- local_path: 本地路径
- downloaded: 是否已下载

## 注意事项

### 爬虫使用
1. **Cookie过期**: 微博Cookie会定期过期，需要重新获取
2. **请求频率**: 默认每次请求间隔2秒，避免被封IP
3. **数据量**: 如果博主微博很多，第一次爬取会比较慢
4. **增量更新**: 重复运行会自动更新新微博，不会重复下载

### 法律和道德
1. **仅供个人使用**: 本工具仅用于个人备份和学习
2. **尊重版权**: 请勿用于商业用途或侵犯他人权益
3. **遵守协议**: 使用时请遵守微博的服务条款
4. **合理使用**: 不要过度频繁请求，避免给服务器造成压力

### 技术限制
1. **评论内容**: 当前版本不抓取评论内容
2. **视频内容**: 不支持视频下载
3. **私密微博**: 只能抓取公开微博
4. **已删除微博**: 无法抓取已删除的内容

## 进阶使用

### 定时更新

**动态模式**：
只需定时运行爬虫即可，Flask会自动读取最新数据：

```bash
# Linux/Mac crontab示例 - 每天凌晨2点更新
0 2 * * * cd /path/to/tombkeeper/crawler && python weibo_spider.py
```

**静态模式**：
需要同时运行爬虫和生成器：

```bash
# Linux/Mac crontab示例 - 每天凌晨2点更新
0 2 * * * cd /path/to/tombkeeper/crawler && python weibo_spider.py
0 3 * * * cd /path/to/tombkeeper/generator && python build.py
```

### 自定义样式
修改 `generator/templates/assets/style.css` 可以自定义网站样式。

### 部署到服务器

**静态模式部署**：
生成的 `site` 目录是纯静态文件，可以直接部署到：
- GitHub Pages
- Netlify
- Vercel
- 任意静态文件服务器

**动态模式部署**：
需要支持Python的托管服务：
- Railway
- Render
- PythonAnywhere
- 自己的VPS（使用gunicorn + nginx）

部署示例（使用gunicorn）：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 常见问题

### Q: 爬虫运行失败，提示Cookie无效？
A: Cookie已过期，需要重新登录微博并获取新的Cookie。

### Q: 图片无法显示？
A: 检查图片是否成功下载到 `data/images` 目录，确认 `download_images` 配置为 `true`。

### Q: 搜索功能不工作？
A:
- **静态模式**：确保运行了 `build.py` 生成搜索索引文件 `assets/search-index.json`。
- **动态模式**：检查数据库中是否有 `weibos_fts` 表，爬虫会自动创建。

### Q: 如何备份数据？
A: 备份 `data` 目录即可，包含数据库和所有图片。

### Q: 能抓取别人的私密微博吗？
A: 不能。只能抓取公开的微博内容。

### Q: 会被微博封号吗？
A: 合理使用、控制请求频率，一般不会。建议设置合适的延迟时间（2-5秒）。

### Q: 静态模式和动态模式如何选择？
A:
- **本地频繁查看**：推荐动态模式，无需每次生成，实时看到最新数据
- **部署到静态托管**：必须使用静态模式（如GitHub Pages）
- **部署到VPS**：可选择动态模式，更方便维护
- **数据量特别大**：静态模式生成时间长，推荐动态模式

## 开发计划

- [ ] 支持评论抓取
- [ ] 支持视频下载
- [ ] 增加图片查看器
- [ ] 支持标签分类
- [ ] 导出为PDF/Markdown
- [ ] 数据可视化统计

## License

MIT License - 仅供学习和个人使用

## 致谢

灵感来源于 [tombkeeper.io](https://tombkeeper.io)
