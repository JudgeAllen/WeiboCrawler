# 微博归档系统

一个将微博博主的所有微博抓取并生成静态网站的工具，方便本地查询和浏览，类似 [tombkeeper.io](https://tombkeeper.io) 的形式。

## 功能特点

- 🕷️ **自动抓取**: 抓取指定博主的所有微博内容
- 💾 **完整存储**: 保存微博文字、图片、转发等完整信息
- 🔍 **全文搜索**: 支持关键词搜索，快速定位内容
- 📱 **响应式设计**: 适配桌面和移动设备
- 🚀 **静态部署**: 生成纯静态HTML，无需后端服务
- 📊 **数据库存储**: 使用SQLite存储，方便数据管理

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
│   ├── build.py         # 构建脚本
│   └── templates/       # HTML模板
│       ├── base.html
│       ├── index.html
│       ├── user.html
│       ├── post.html
│       └── assets/      # 静态资源
│           ├── style.css
│           └── search.js
├── site/                # 生成的静态网站
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

```bash
cd crawler
python weibo_spider.py
```

爬虫会自动：
- 抓取用户信息
- 获取所有微博内容
- 下载微博图片
- 保存到SQLite数据库

### 4. 生成静态网站

```bash
cd generator
python build.py
```

生成器会：
- 读取数据库中的微博数据
- 生成静态HTML页面
- 创建搜索索引
- 复制静态资源和图片

### 5. 本地预览

使用任意HTTP服务器运行生成的网站：

#### Python方式：
```bash
cd site
python -m http.server 8000
```

#### Node.js方式：
```bash
cd site
npx http-server -p 8000
```

然后在浏览器访问: `http://localhost:8000`

## 功能说明

### 首页
- 显示所有博主列表
- 展示最新50条微博
- 支持搜索功能

### 用户页
- 显示该用户的所有微博
- 按时间倒序排列
- 显示用户信息和统计

### 微博详情页
- 显示完整的微博内容
- 显示图片（如有）
- 显示转发微博（如有）
- 显示互动统计

### 搜索功能
- 点击导航栏的"搜索"打开搜索面板
- 输入关键词实时搜索
- 支持中文搜索
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
可以使用cron或Windows任务计划程序定时运行爬虫：

```bash
# Linux/Mac crontab示例 - 每天凌晨2点更新
0 2 * * * cd /path/to/tombkeeper/crawler && python weibo_spider.py
0 3 * * * cd /path/to/tombkeeper/generator && python build.py
```

### 自定义样式
修改 `generator/templates/assets/style.css` 可以自定义网站样式。

### 部署到服务器
生成的 `site` 目录是纯静态文件，可以直接部署到：
- GitHub Pages
- Netlify
- Vercel
- 任意静态文件服务器

### 扩展搜索功能
当前使用简单的字符串匹配搜索，如需更强大的搜索功能，可以集成：
- Lunr.js
- Fuse.js
- MiniSearch

## 常见问题

### Q: 爬虫运行失败，提示Cookie无效？
A: Cookie已过期，需要重新登录微博并获取新的Cookie。

### Q: 图片无法显示？
A: 检查图片是否成功下载到 `data/images` 目录，确认 `download_images` 配置为 `true`。

### Q: 搜索功能不工作？
A: 确保运行了 `build.py` 生成搜索索引文件 `assets/search-index.json`。

### Q: 如何备份数据？
A: 备份 `data` 目录即可，包含数据库和所有图片。

### Q: 能抓取别人的私密微博吗？
A: 不能。只能抓取公开的微博内容。

### Q: 会被微博封号吗？
A: 合理使用、控制请求频率，一般不会。建议设置合适的延迟时间（2-5秒）。

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
