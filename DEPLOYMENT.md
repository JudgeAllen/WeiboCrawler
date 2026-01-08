# 部署指南

本文档介绍如何将微博归档系统部署到GitHub Pages或Cloudflare Pages。

## 重要说明

⚠️ **静态部署限制**

GitHub Pages和Cloudflare Pages只支持**静态网站**，不支持Python后端。这意味着：

- ✅ 可以部署：静态HTML网站（使用 `generator/build.py` 生成）
- ❌ 不可部署：Flask动态服务器（`app.py`）
- ❌ 不可运行：定时爬虫任务

**推荐工作流程**：
1. 本地运行爬虫抓取最新微博
2. 本地使用Flask动态模式查看和管理
3. 定期生成静态网站并部署到GitHub Pages/Cloudflare Pages供公开访问

---

## 方案一：部署到GitHub Pages

### 优点
- 完全免费
- GitHub集成，自动部署
- 免费HTTPS和自定义域名
- 全球CDN

### 步骤

#### 1. 准备数据库

确保您的数据库文件在 `data/database.db`，并且已经抓取了微博数据。

#### 2. 生成静态网站

```bash
cd generator
python build.py
```

这会在 `site/` 目录生成静态HTML文件。

#### 3. 提交并推送到GitHub

```bash
git add site/
git commit -m "chore: 更新静态网站"
git push origin main
```

#### 4. 配置GitHub Pages

1. 访问您的GitHub仓库
2. 点击 **Settings** → **Pages**
3. 在 **Source** 下选择：
   - **Deploy from a branch**
   - Branch: `main`
   - Folder: `/site` ⚠️ **重要：选择site文件夹**
4. 点击 **Save**

#### 5. 等待部署

GitHub会自动部署，通常需要1-3分钟。部署完成后会显示网站URL：
```
https://your-username.github.io/your-repo-name/
```

#### 6. 自定义域名（可选）

如果您有自己的域名：
1. 在DNS提供商添加CNAME记录指向 `your-username.github.io`
2. 在GitHub Pages设置中填写自定义域名
3. 等待DNS生效（通常几分钟到几小时）

---

## 方案二：使用GitHub Actions自动部署

上面的`.github/workflows/deploy.yml`文件已经为您准备好了。

### 启用方式

#### 1. 在GitHub仓库中启用GitHub Pages

1. 访问 Settings → Pages
2. Source 选择 **GitHub Actions**

#### 2. 手动触发部署

1. 访问仓库的 **Actions** 标签
2. 选择 **Deploy to GitHub Pages** 工作流
3. 点击 **Run workflow** → **Run workflow**

#### 3. 查看部署状态

在Actions页面可以看到部署进度。部署完成后访问：
```
https://your-username.github.io/your-repo-name/
```

### 自动部署（可选）

如果希望每次推送都自动部署，编辑 `.github/workflows/deploy.yml`：

```yaml
on:
  push:
    branches:
      - main
  workflow_dispatch:
```

这样每次推送到main分支时都会自动重新生成和部署。

⚠️ **注意**：这会在每次推送时重新生成整个站点，如果数据库很大可能比较慢。

---

## 方案三：部署到Cloudflare Pages

### 优点
- 完全免费
- 全球CDN，速度更快（比GitHub Pages）
- 无限带宽
- 更好的中国访问速度

### 步骤

#### 1. 生成静态网站

```bash
cd generator
python build.py
```

#### 2. 注册Cloudflare账号

访问 https://pages.cloudflare.com/ 并注册账号（免费）

#### 3. 连接GitHub仓库

1. 点击 **Create a project**
2. 选择 **Connect to Git**
3. 授权Cloudflare访问您的GitHub仓库
4. 选择 `TombkeeperWeibo` 仓库

#### 4. 配置构建设置

- **Framework preset**: None
- **Build command**: `cd generator && python build.py`
- **Build output directory**: `site`
- **Root directory**: `/`

或者，如果已经在本地生成了站点：
- **Build command**: 留空
- **Build output directory**: `site`

#### 5. 部署

点击 **Save and Deploy**，Cloudflare会自动部署。

部署完成后会得到一个URL，例如：
```
https://tombkeeperweibo.pages.dev
```

#### 6. 自定义域名（可选）

1. 在Cloudflare Pages项目中点击 **Custom domains**
2. 添加您的域名
3. 按提示配置DNS（如果域名在Cloudflare会自动配置）

---

## 更新部署的网站

### 本地更新流程

1. **运行爬虫获取最新微博**
   ```bash
   cd crawler
   python weibo_spider.py
   ```

2. **重新生成静态网站**
   ```bash
   cd ../generator
   python build.py
   ```

3. **提交并推送**
   ```bash
   git add site/
   git commit -m "update: 更新至$(date +%Y-%m-%d)"
   git push
   ```

### GitHub Pages
推送后会自动更新（如果配置了自动部署），或者手动触发GitHub Actions。

### Cloudflare Pages
推送后会自动触发重新部署。

---

## 方案四：部署动态网站（Flask）

如果您需要动态功能（实时搜索、定时更新等），需要使用支持Python的托管服务。

### 推荐服务

#### 1. Railway (推荐)
- 免费额度：$5/月
- 支持：Python、定时任务
- 网址：https://railway.app/

**部署步骤**：
1. 注册Railway账号
2. 连接GitHub仓库
3. 配置启动命令：`python app.py`
4. 自动部署

#### 2. Render
- 免费额度：有限
- 支持：Python
- 网址：https://render.com/

**部署步骤**：
1. 注册Render账号
2. New Web Service → 连接GitHub
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python app.py`

#### 3. PythonAnywhere
- 免费额度：有限
- 专门为Python设计
- 网址：https://www.pythonanywhere.com/

**部署步骤**：
1. 注册账号（免费）
2. 上传代码或从GitHub克隆
3. 配置WSGI文件
4. 设置定时任务（需要付费账户）

⚠️ **动态部署限制**：
- 免费额度通常有限
- 定时任务可能需要付费
- 需要保持数据库文件同步

---

## 推荐方案总结

### 如果只是想分享归档内容
✅ **GitHub Pages** 或 **Cloudflare Pages**（静态部署）
- 完全免费
- 性能好
- 操作简单

### 如果需要动态功能
✅ **Railway** 或 **Render**（动态部署）
- 支持Python后端
- 可以运行定时任务
- 有免费额度（有限）

### 混合方案（推荐）
✅ **本地动态 + 远程静态**
- 本地使用Flask动态模式管理和查看
- 定期生成静态网站部署到GitHub Pages
- 兼顾便利性和成本

---

## 常见问题

### Q: 为什么不能在GitHub Pages运行爬虫？
A: GitHub Pages只支持静态HTML/CSS/JS，不能运行Python代码。爬虫需要在本地运行。

### Q: 多久需要更新一次部署的网站？
A: 根据您的需求，可以每天、每周或每月更新一次。只需重新生成静态站点并推送即可。

### Q: 可以在GitHub Pages使用搜索功能吗？
A: 可以！静态模式使用预生成的JSON索引，搜索在浏览器中执行，不需要服务器。

### Q: 数据库文件会被公开吗？
A: 不会。只有生成的HTML文件会被部署，数据库文件保留在本地。

### Q: 图片会占用GitHub仓库空间吗？
A: 会。如果图片很多，可以考虑：
  1. 使用图床服务（如Cloudinary、腾讯云COS）
  2. 不提交图片到GitHub，仅部署文字内容
  3. 使用Git LFS管理大文件

### Q: 如何绑定自定义域名？
A: GitHub Pages和Cloudflare Pages都支持免费绑定自定义域名，在各自的设置页面配置即可。

---

## 安全建议

⚠️ **不要提交敏感信息**

在提交代码到公开仓库前，确保：
- ✅ `crawler/config.json` 已添加到 `.gitignore`
- ✅ 微博Cookie不在代码中
- ✅ 数据库文件不被提交（如果包含私密微博）

检查 `.gitignore` 文件包含：
```
crawler/config.json
data/database.db
*.pyc
__pycache__/
.venv/
```

---

## 示例工作流

### 日常使用（本地）
```bash
# 1. 运行爬虫
python scheduler.py  # 或设置定时任务

# 2. 查看微博
python app.py
# 访问 http://localhost:5000
```

### 更新公开网站（每周一次）
```bash
# 1. 生成静态站点
cd generator
python build.py

# 2. 提交并推送
cd ..
git add site/
git commit -m "update: $(date +%Y-%m-%d) 更新"
git push

# 3. 等待自动部署（1-3分钟）
```

---

祝部署顺利！如有问题，请提交Issue到GitHub仓库。
