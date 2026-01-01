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
  "download_images": true
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
```bash
# 1. 爬取微博
cd crawler
python weibo_spider.py

# 2. 生成网站
cd ../generator
python build.py

# 3. 预览
cd ../site
python -m http.server 8000
```

浏览器访问：http://localhost:8000

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
确保运行了第2步生成网站。

## 下一步

- 查看 [README.md](README.md) 了解详细功能
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
  "delay": 2
}
```

祝使用愉快！
