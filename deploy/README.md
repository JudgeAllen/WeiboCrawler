# VPS部署文件说明

本目录包含在VPS（Ubuntu 24）上部署微博归档系统所需的所有文件。

## 📁 文件列表

| 文件 | 说明 | 用途 |
|------|------|------|
| `VPS_DEPLOYMENT.md` | 完整部署指南 | 详细的部署步骤和故障排查 |
| `vps_setup.sh` | 环境配置脚本 | 一键安装系统依赖和克隆代码 |
| `secure_config.sh` | 安全配置脚本 | 配置环境变量保护Cookie |
| `install_services.sh` | 服务安装脚本 | 安装并启动systemd服务 |
| `weibo-scheduler.service` | 调度器服务 | systemd服务配置文件 |
| `weibo-flask.service` | Flask服务 | systemd服务配置文件 |
| `nginx.conf` | Nginx配置 | 反向代理和SSL配置 |

## 🚀 快速开始

### 方式1：自动部署（推荐）

```bash
# 1. 连接到VPS
ssh your-user@your-vps-ip

# 2. 下载并运行部署脚本
cd ~
git clone https://github.com/JudgeAllen/WeiboCrawler.git weibo-archive
cd weibo-archive

# 3. 运行部署脚本
chmod +x deploy/*.sh
./deploy/vps_setup.sh          # 安装环境
./deploy/secure_config.sh      # 配置环境变量
./deploy/install_services.sh   # 安装服务

# 4. 验证运行
sudo systemctl status weibo-scheduler@$(whoami)
```

### 方式2：手动部署

详见 [VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md)

## 🔐 安全特性

1. **环境变量保护**：Cookie存储在 `.env` 文件中，权限设为600
2. **文件权限管理**：数据库和配置文件仅所有者可访问
3. **Nginx反向代理**：Flask不直接暴露到公网
4. **SSL支持**：支持Let's Encrypt免费证书
5. **防火墙配置**：仅开放必要端口

## 📊 服务管理

### 调度器服务

```bash
# 查看状态
sudo systemctl status weibo-scheduler@YOUR_USER

# 启动/停止/重启
sudo systemctl start/stop/restart weibo-scheduler@YOUR_USER

# 查看日志
tail -f ~/weibo-archive/logs/scheduler.log
journalctl -u weibo-scheduler@YOUR_USER -f
```

### Flask服务

```bash
# 同上，替换为 weibo-flask
sudo systemctl status weibo-flask@YOUR_USER
tail -f ~/weibo-archive/logs/flask.log
```

## 🔧 配置说明

### 环境变量 (.env)

```bash
# 必需配置
WEIBO_COOKIE="your_cookie"      # 微博Cookie
WEIBO_UID="1401527553"          # 用户UID
WEIBO_NAME="tombkeeper"         # 用户名

# 可选配置
SCHEDULER_START_HOUR="7"        # 调度开始时间
SCHEDULER_END_HOUR="24"         # 调度结束时间
SCHEDULER_NORMAL_INTERVAL="5"   # 正常间隔（分钟）
SCHEDULER_EXTENDED_INTERVAL="15" # 延长间隔（分钟）
SCHEDULER_THRESHOLD="3"         # 延长阈值（次数）

FLASK_HOST="127.0.0.1"          # Flask监听地址
FLASK_PORT="5000"               # Flask端口
```

### Nginx配置

位置：`/etc/nginx/sites-available/weibo-archive`

关键配置：
- 反向代理到 `http://127.0.0.1:5000`
- 静态文件直接服务
- SSL证书路径（如使用HTTPS）

## 📋 部署检查清单

- [ ] 系统依赖已安装（Python、Git、Nginx）
- [ ] 代码已克隆到 `~/weibo-archive`
- [ ] Python虚拟环境已创建
- [ ] 依赖包已安装 (`pip install -r requirements.txt`)
- [ ] 环境变量已配置（`.env` 文件）
- [ ] 环境变量权限正确（`chmod 600 .env`）
- [ ] 调度器服务已安装并运行
- [ ] Flask服务已安装并运行（可选）
- [ ] Nginx已配置并重启（可选）
- [ ] SSL证书已安装（可选）
- [ ] 防火墙规则已设置
- [ ] 定期备份已配置
- [ ] Web界面可访问

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细日志
journalctl -u weibo-scheduler@YOUR_USER -n 50 --no-pager

# 检查环境变量
cat ~/weibo-archive/.env

# 手动测试
cd ~/weibo-archive
source venv/bin/activate
source .env
python scheduler.py
```

### Cookie失效

```bash
# 更新Cookie
nano ~/weibo-archive/.env

# 重启服务
sudo systemctl restart weibo-scheduler@YOUR_USER
```

### 查看实时日志

```bash
# 调度器
tail -f ~/weibo-archive/logs/scheduler.log

# Flask
tail -f ~/weibo-archive/logs/flask.log

# 系统日志
journalctl -u weibo-scheduler@YOUR_USER -f
```

## 📈 监控

### 磁盘使用

```bash
# 数据目录大小
du -sh ~/weibo-archive/data/

# 数据库大小
ls -lh ~/weibo-archive/data/database.db

# 图片数量和大小
find ~/weibo-archive/data/images -type f | wc -l
du -sh ~/weibo-archive/data/images/
```

### 服务状态

```bash
# 检查所有服务
sudo systemctl status weibo-*

# 查看资源使用
top
htop
```

## 🔄 更新

```bash
# 拉取最新代码
cd ~/weibo-archive
git pull origin main

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl restart weibo-scheduler@YOUR_USER
sudo systemctl restart weibo-flask@YOUR_USER
```

## 💾 备份

建议备份：
1. 数据库文件：`~/weibo-archive/data/database.db`
2. 环境变量：`~/weibo-archive/.env`
3. 图片目录：`~/weibo-archive/data/images/`（可选）

备份脚本见 `VPS_DEPLOYMENT.md` 中的备份章节。

## 🌐 访问

- HTTP：`http://your-vps-ip:5000` 或 `http://your-domain.com`
- HTTPS：`https://your-domain.com`（需配置SSL）

## 📞 获取帮助

- 详细文档：[VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md)
- 项目主页：https://github.com/JudgeAllen/WeiboCrawler
- 问题反馈：https://github.com/JudgeAllen/WeiboCrawler/issues

---

**重要提示**：
- ⚠️ 不要将 `.env` 文件提交到Git
- ⚠️ 定期检查Cookie是否失效
- ⚠️ 定期备份数据库
- ⚠️ 监控磁盘空间使用
