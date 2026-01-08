# 快速入门指南

## 三步开始使用

### 第一步：安装依赖

```bash
pip install -r requirements.txt
```

### 第二步：配置Cookie

1. 登录微博网页版 https://weibo.com
2. 按F12打开开发者工具
3. 刷新页面，在Network标签找到任意请求
4. 复制请求头中的Cookie
5. 编辑 `crawler/config.json`：

```json
{
  "target_users": [
    {
      "uid": "1401527553",
      "name": "tombkeeper"
    }
  ],
  "cookie": "粘贴你的Cookie到这里",
  "download_images": true,
  "image_path": "../data/images",
  "database_path": "../data/database.db",
  "delay": 2,
  "max_retries": 3,
  "scheduler": {
    "active_start_hour": 7,
    "active_end_hour": 24,
    "normal_interval_minutes": 5,
    "extended_interval_minutes": 15,
    "no_update_threshold": 3
  }
}
```

**获取用户UID：** 打开用户主页，URL中的数字就是UID
- 例如：https://weibo.com/u/1401527553 → UID是 1401527553

### 第三步：运行

#### Windows用户：
双击运行 `run.bat`，选择选项4（完整流程）

#### Mac/Linux用户：
```bash
chmod +x run.sh
./run.sh
```
选择选项4（完整流程）

#### 或手动运行：

**方式1：智能调度器（推荐）**
```bash
python scheduler.py
```
自动按配置的间隔定时抓取微博，智能调整频率。

**方式2：单次运行**
```bash
# 1. 爬取微博
cd crawler
python weibo_spider.py

# 2. 动态模式（查看和管理）
cd ..
python app.py
# 访问 http://localhost:5000

# 3. 或生成静态网站
cd generator
python build.py
cd ../site
python -m http.server 8000
# 访问 http://localhost:8000
```

## 常见问题

### 提示Cookie无效？
Cookie过期了，重新登录微博获取新Cookie。

### 没有抓取到微博？
1. 检查UID是否正确
2. 检查Cookie是否有效
3. 检查网络连接

### 图片无法显示？
确保 `config.json` 中 `download_images` 为 `true`

### 搜索功能不工作？
- 动态模式：确保运行 `python app.py`
- 静态模式：确保运行了 `python build.py` 生成网站

### 如何定时自动抓取？
```bash
python scheduler.py
```
或参考 [WINDOWS_TASK_SCHEDULER.md](WINDOWS_TASK_SCHEDULER.md) 设置系统定时任务。

## 下一步

- 查看 [README.md](README.md) 了解详细功能
- 查看 [SCHEDULER_CONFIG.md](SCHEDULER_CONFIG.md) 配置智能调度器
- 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 了解如何部署到GitHub Pages
- 修改 `generator/templates/assets/style.css` 自定义样式
- 添加更多博主到 `crawler/config.json`

## 示例配置 - 多个博主

```json
{
  "target_users": [
    {
      "uid": "1401527553",
      "name": "tombkeeper"
    },
    {
      "uid": "1642088277",
      "name": "来去之间"
    },
    {
      "uid": "1197161814",
      "name": "纯银V"
    }
  ],
  "cookie": "你的Cookie",
  "download_images": true,
  "delay": 2,
  "scheduler": {
    "active_start_hour": 7,
    "active_end_hour": 24,
    "normal_interval_minutes": 5,
    "extended_interval_minutes": 15,
    "no_update_threshold": 3
  }
}
```

祝使用愉快！
