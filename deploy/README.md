# VPS部署文件说明

本目录包含在VPS（Ubuntu 24）上部署微博归档系统所需的所有文件。

## 📁 文件列表

| 文件 | 说明 | 用途 |
|------|------|------|
| `VPS_DEPLOYMENT.md` | 完整部署指南 | 详细的部署步骤和故障排查 |
| `SSL_SETUP.md` | HTTPS配置指南 | SSL/TLS证书配置详解 |
| `vps_setup.sh` | 环境配置脚本 | 一键安装系统依赖和克隆代码 |
| `secure_config.sh` | 安全配置脚本 | 配置环境变量保护Cookie |
| `install_services.sh` | 服务安装脚本 | 安装并启动systemd服务 |
| `ssl_setup.sh` | HTTPS配置脚本 | 一键配置Let's Encrypt证书 |
| `upgrade.sh` | 升级脚本（Linux） | 一键更新到最新版本 |
| `upgrade.bat` | 升级脚本（Windows） | Windows一键更新 |
| `weibo-scheduler.service` | 调度器服务 | systemd服务配置文件 |
| `weibo-flask.service` | Flask服务 | systemd服务配置文件 |
| `nginx.conf` | Nginx配置模板 | 反向代理和SSL配置模板 |

## 🚀 快速开始

### 完整部署流程

```bash
# 1. 连接到VPS
ssh your-user@your-vps-ip

# 2. 下载代码
cd ~
git clone https://github.com/JudgeAllen/WeiboCrawler.git weibo-archive
cd weibo-archive

# 3. 运行部署脚本（按顺序执行）
chmod +x deploy/*.sh

# 3.1 安装基础环境
./deploy/vps_setup.sh

# 3.2 配置环境变量（输入Cookie）
./deploy/secure_config.sh

# 3.3 安装并启动服务
./deploy/install_services.sh

# 3.4 配置HTTPS（可选但强烈推荐）
sudo ./deploy/ssl_setup.sh

# 4. 验证运行
sudo systemctl status weibo-scheduler@$(whoami)
sudo systemctl status weibo-flask@$(whoami)
```

### HTTP访问（不推荐）

如果暂时不配置HTTPS，可以通过以下方式访问：
```
http://your-vps-ip:5000
```

⚠️ **安全警告**：HTTP模式下Cookie和数据明文传输，强烈建议配置HTTPS。

### HTTPS访问（推荐）

配置SSL证书后，可以通过域名安全访问：
```
https://your-domain.com
```

详见 [SSL_SETUP.md](SSL_SETUP.md)

---

## 📖 详细文档

### 主要文档

1. **[VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md)** - VPS部署完整指南
   - 基础环境配置
   - 服务管理
   - 安全配置
   - 监控维护
   - 故障排查

2. **[SSL_SETUP.md](SSL_SETUP.md)** - HTTPS配置指南
   - Let's Encrypt证书申请
   - Nginx SSL配置
   - 自动续期设置
   - 安全优化
   - 常见问题

### 快速参考

## 🔐 安全特性

### 基础安全

1. **环境变量保护**：Cookie存储在 `.env` 文件中，权限设为600
2. **文件权限管理**：数据库和配置文件仅所有者可访问
3. **Nginx反向代理**：Flask不直接暴露到公网
4. **防火墙配置**：仅开放必要端口（22, 80, 443）

### HTTPS/SSL安全（强烈推荐）

5. **免费SSL证书**：Let's Encrypt自动续期
6. **数据加密传输**：TLS 1.2/1.3加密所有通信
7. **Cookie安全传输**：防止中间人攻击窃取Cookie
8. **强制HTTPS**：自动将HTTP重定向到HTTPS
9. **安全头配置**：
   - HSTS（强制HTTPS）
   - X-Frame-Options（防点击劫持）
   - X-Content-Type-Options（防MIME嗅探）
   - X-XSS-Protection（XSS防护）
   - OCSP Stapling（证书状态检查）

### 为什么需要HTTPS？

| 安全威胁 | HTTP | HTTPS |
|---------|------|-------|
| Cookie窃取 | ⚠️ 易被窃取 | ✅ 加密保护 |
| 数据监听 | ⚠️ 明文可见 | ✅ 完全加密 |
| 中间人攻击 | ⚠️ 无防护 | ✅ 有效防护 |
| 浏览器信任 | ❌ "不安全"警告 | ✅ 锁图标 |

**配置HTTPS只需一条命令**：
```bash
sudo ./deploy/ssl_setup.sh
```

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

### 基础部署

- [ ] 系统依赖已安装（Python、Git、Nginx）
- [ ] 代码已克隆到 `~/weibo-archive`
- [ ] Python虚拟环境已创建
- [ ] 依赖包已安装 (`pip install -r requirements.txt`)
- [ ] 环境变量已配置（`.env` 文件）
- [ ] 环境变量权限正确（`chmod 600 .env`）
- [ ] 调度器服务已安装并运行
- [ ] Flask服务已安装并运行
- [ ] 防火墙规则已设置（22, 80, 443端口）

### HTTPS配置（强烈推荐）

- [ ] 域名已准备并解析到VPS IP
- [ ] Certbot已安装
- [ ] SSL证书已获取
- [ ] Nginx HTTPS配置已完成
- [ ] HTTP自动跳转HTTPS
- [ ] 证书自动续期已配置
- [ ] SSL Labs测试评级A或A+
- [ ] Web界面可通过HTTPS访问

### 可选优化

- [ ] 定期备份已配置
- [ ] 日志轮转已配置
- [ ] 监控告警已配置
- [ ] CDN加速已配置

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

## 🔄 升级系统

### 方式1：一键升级（推荐）

**Linux/VPS:**
```bash
cd ~/weibo-archive
chmod +x deploy/upgrade.sh
./deploy/upgrade.sh
```

**Windows:**
```cmd
cd f:\Git\tombkeeper
deploy\upgrade.bat
```

升级脚本会自动：
1. ✅ 拉取最新代码
2. ✅ 更新Python依赖
3. ✅ 检查数据库状态
4. ✅ 更新systemd服务配置
5. ✅ 重启服务
6. ✅ 验证运行状态
7. ✅ 显示更新日志

### 方式2：手动升级

```bash
# 1. 拉取最新代码
cd ~/weibo-archive
git pull origin main

# 2. 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 3. 更新systemd服务（如有更新）
sudo cp deploy/weibo-scheduler.service /etc/systemd/system/weibo-scheduler@.service
sudo cp deploy/weibo-flask.service /etc/systemd/system/weibo-flask@.service
sudo systemctl daemon-reload

# 4. 重启服务
sudo systemctl restart weibo-scheduler@YOUR_USER
sudo systemctl restart weibo-flask@YOUR_USER

# 5. 验证
sudo systemctl status weibo-scheduler@YOUR_USER
sudo systemctl status weibo-flask@YOUR_USER
```

### 升级注意事项

- ⚠️ 升级前会检查未提交的更改
- ⚠️ 如有本地修改，建议先备份或提交
- ⚠️ 升级会自动重启服务，可能中断几秒钟
- ✅ 数据库和配置文件不会被覆盖
- ✅ 升级失败会保留当前版本

## 💾 备份

建议备份：
1. 数据库文件：`~/weibo-archive/data/database.db`
2. 环境变量：`~/weibo-archive/.env`
3. 图片目录：`~/weibo-archive/data/images/`（可选）

备份脚本见 `VPS_DEPLOYMENT.md` 中的备份章节。

## 🌐 访问方式

### HTTP访问（临时）

```
http://your-vps-ip:5000
```

⚠️ **不推荐**：Cookie和数据明文传输，仅用于测试

### HTTPS访问（推荐）

```
https://your-domain.com
```

✅ **推荐**：数据加密传输，安全可靠

配置方法：
```bash
sudo ./deploy/ssl_setup.sh
```

## 📞 获取帮助

### 文档

- **VPS部署**：[VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md)
- **HTTPS配置**：[SSL_SETUP.md](SSL_SETUP.md)
- **主文档**：[../README.md](../README.md)

### 支持

- 项目主页：https://github.com/JudgeAllen/WeiboCrawler
- 问题反馈：https://github.com/JudgeAllen/WeiboCrawler/issues

### 常见问题快速链接

- [如何配置HTTPS？](SSL_SETUP.md)
- [如何查看服务日志？](VPS_DEPLOYMENT.md#监控和维护)
- [Cookie失效怎么办？](VPS_DEPLOYMENT.md#问题2cookie失效)
- [如何更新代码？](VPS_DEPLOYMENT.md#更新代码)

---

## ⚠️ 重要提示

### 安全

- ❌ **不要**将 `.env` 文件提交到Git
- ✅ **务必**配置HTTPS保护Cookie传输
- ✅ **建议**使用强密码和SSH密钥登录VPS
- ✅ **定期**更新系统和软件包

### 维护

- 🔄 定期检查Cookie是否失效
- 💾 定期备份数据库（`~/weibo-archive/data/database.db`）
- 📊 监控磁盘空间使用
- 📜 定期查看日志文件
- 🔒 检查SSL证书是否正常续期

### 成本

- VPS费用：根据服务商和配置（通常$5-20/月）
- SSL证书：免费（Let's Encrypt）
- 域名：约$10-15/年（可选，或使用免费域名）

---

## 🎯 推荐配置

**最佳实践**：

```bash
# 完整部署流程
./deploy/vps_setup.sh          # 基础环境
./deploy/secure_config.sh      # 环境变量
./deploy/install_services.sh   # 系统服务
sudo ./deploy/ssl_setup.sh     # HTTPS（强烈推荐）

# 验证
sudo systemctl status weibo-scheduler@$(whoami)
sudo systemctl status weibo-flask@$(whoami)
curl -I https://your-domain.com
```

**访问**：`https://your-domain.com`
