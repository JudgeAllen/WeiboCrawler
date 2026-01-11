# VPS部署完整指南

## 环境信息

- **系统**: Ubuntu 24 (或其他Linux发行版)
- **架构**: 自动化微博归档系统

---

## 部署方案概览

```
VPS部署架构：
┌─────────────────────────────────────────┐
│           Nginx (80/443)                │
│           ↓ 反向代理                     │
│      Flask App (5000)                   │
│           ↓ 读取数据                     │
│      SQLite Database                    │
│           ↑ 写入数据                     │
│   Scheduler (自动爬虫)                   │
└─────────────────────────────────────────┘
```

**特点**：
- ✅ Cookie安全（环境变量，不在代码中）
- ✅ 全自动爬取（systemd服务）
- ✅ Web界面访问（Flask + Nginx）
- ✅ 开机自启动
- ✅ 日志管理

---

## 快速部署（一键脚本）

### 步骤1：连接到VPS

```bash
ssh your-user@your-vps-ip
```

### 步骤2：运行部署脚本

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/JudgeAllen/WeiboCrawler/main/deploy/vps_setup.sh

# 添加执行权限
chmod +x vps_setup.sh

# 运行部署
./vps_setup.sh
```

### 步骤3：配置敏感信息

```bash
cd ~/weibo-archive
chmod +x deploy/secure_config.sh
./deploy/secure_config.sh
```

按提示输入：
- 微博Cookie（从浏览器复制）
- 用户UID（默认：1401527553）
- 用户名称（默认：tombkeeper）

### 步骤4：安装系统服务

```bash
chmod +x deploy/install_services.sh
./deploy/install_services.sh
```

选择启动：
- 调度器服务：自动爬取微博
- Flask服务：Web界面

### 步骤5：配置Nginx（可选）

```bash
# 安装SSL证书（推荐）
sudo apt install certbot python3-certbot-nginx

# 获取证书（替换your-domain.com）
sudo certbot --nginx -d your-domain.com

# 复制Nginx配置
sudo cp deploy/nginx.conf /etc/nginx/sites-available/weibo-archive

# 修改配置中的用户名和域名
sudo nano /etc/nginx/sites-available/weibo-archive

# 启用配置
sudo ln -s /etc/nginx/sites-available/weibo-archive /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

---

## 手动部署（详细步骤）

### 1. 基础环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3 python3-pip python3-venv git nginx

# 创建项目目录
mkdir -p ~/weibo-archive
cd ~/weibo-archive

# 克隆代码
git clone https://github.com/JudgeAllen/WeiboCrawler.git .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `~/weibo-archive/.env`：

```bash
# 微博配置
WEIBO_COOKIE="你的Cookie"
WEIBO_UID="1401527553"
WEIBO_NAME="tombkeeper"

# 路径配置
DATABASE_PATH="/home/YOUR_USER/weibo-archive/data/database.db"
IMAGE_PATH="/home/YOUR_USER/weibo-archive/data/images"

# Flask配置
FLASK_SECRET_KEY="your-random-secret-key"
FLASK_HOST="0.0.0.0"
FLASK_PORT="5000"

# 调度器配置
SCHEDULER_START_HOUR="7"
SCHEDULER_END_HOUR="24"
SCHEDULER_NORMAL_INTERVAL="5"
SCHEDULER_EXTENDED_INTERVAL="15"
SCHEDULER_THRESHOLD="3"
```

设置权限：
```bash
chmod 600 ~/weibo-archive/.env
```

### 3. 修改代码支持环境变量

需要修改 `crawler/weibo_spider.py`，使用 `config_loader.py`：

```python
# 在 weibo_spider.py 开头添加
from config_loader import load_config

# 修改 __init__ 方法
def __init__(self, config_path='config.json'):
    """初始化爬虫"""
    self.config = load_config(config_path)  # 使用新的加载器
    # ... 其余代码不变
```

同样修改 `scheduler.py`。

### 4. 测试运行

```bash
# 激活环境
source venv/bin/activate

# 加载环境变量
source .env

# 测试爬虫
cd crawler
python weibo_spider.py

# 测试Flask
cd ..
python app.py
```

访问 `http://your-vps-ip:5000` 测试。

### 5. 配置systemd服务

参考上面的步骤4。

---

## 服务管理

### 调度器服务

```bash
# 启动
sudo systemctl start weibo-scheduler@YOUR_USER

# 停止
sudo systemctl stop weibo-scheduler@YOUR_USER

# 重启
sudo systemctl restart weibo-scheduler@YOUR_USER

# 查看状态
sudo systemctl status weibo-scheduler@YOUR_USER

# 查看日志
tail -f ~/weibo-archive/logs/scheduler.log

# 实时日志
journalctl -u weibo-scheduler@YOUR_USER -f

# 开机自启
sudo systemctl enable weibo-scheduler@YOUR_USER

# 禁用自启
sudo systemctl disable weibo-scheduler@YOUR_USER
```

### Flask服务

```bash
# 同上，替换为 weibo-flask@YOUR_USER
sudo systemctl status weibo-flask@YOUR_USER
tail -f ~/weibo-archive/logs/flask.log
```

---

## 安全配置

### 1. 防火墙配置

```bash
# 安装UFW
sudo apt install ufw

# 允许SSH（重要！）
sudo ufw allow ssh
sudo ufw allow 22/tcp

# 允许HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 如果直接访问Flask（不推荐）
sudo ufw allow 5000/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. 限制Flask访问

如果使用Nginx反向代理，Flask应该只监听localhost：

修改 `app.py`：
```python
if __name__ == '__main__':
    # VPS部署：只监听localhost
    app.run(host='127.0.0.1', port=5000, debug=False)

    # 或使用环境变量
    # app.run(
    #     host=os.getenv('FLASK_HOST', '127.0.0.1'),
    #     port=int(os.getenv('FLASK_PORT', '5000')),
    #     debug=False
    # )
```

### 3. 文件权限

```bash
# .env文件（仅所有者可读）
chmod 600 ~/weibo-archive/.env

# 数据库（仅所有者可读写）
chmod 600 ~/weibo-archive/data/database.db

# 日志目录
chmod 755 ~/weibo-archive/logs
```

### 4. 定期备份

创建备份脚本 `~/weibo-archive/backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR=~/weibo-backups
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp ~/weibo-archive/data/database.db $BACKUP_DIR/database_$DATE.db

# 备份环境变量（加密）
tar -czf $BACKUP_DIR/env_$DATE.tar.gz -C ~ weibo-archive/.env

# 删除30天前的备份
find $BACKUP_DIR -type f -mtime +30 -delete

echo "备份完成: $BACKUP_DIR"
```

设置cron定时备份：
```bash
crontab -e

# 每天凌晨3点备份
0 3 * * * /home/YOUR_USER/weibo-archive/backup.sh
```

---

## 监控和维护

### 1. 日志查看

```bash
# 调度器日志
tail -f ~/weibo-archive/logs/scheduler.log

# Flask日志
tail -f ~/weibo-archive/logs/flask.log

# Nginx访问日志
sudo tail -f /var/log/nginx/weibo-archive-access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/weibo-archive-error.log

# 系统日志
journalctl -u weibo-scheduler@YOUR_USER -n 100
journalctl -u weibo-flask@YOUR_USER -n 100
```

### 2. 性能监控

```bash
# 查看进程
ps aux | grep python

# 查看资源使用
top
htop

# 查看磁盘使用
df -h
du -sh ~/weibo-archive/data/

# 查看数据库大小
ls -lh ~/weibo-archive/data/database.db
```

### 3. 更新代码

```bash
cd ~/weibo-archive

# 拉取最新代码
git pull origin main

# 重启服务
sudo systemctl restart weibo-scheduler@YOUR_USER
sudo systemctl restart weibo-flask@YOUR_USER
```

---

## 故障排查

### 问题1：服务无法启动

```bash
# 查看详细错误
sudo systemctl status weibo-scheduler@YOUR_USER -l
journalctl -u weibo-scheduler@YOUR_USER -n 50

# 检查环境变量
cat ~/weibo-archive/.env

# 手动运行测试
cd ~/weibo-archive
source venv/bin/activate
source .env
python scheduler.py
```

### 问题2：Cookie失效

```bash
# 重新配置Cookie
nano ~/weibo-archive/.env
# 修改WEIBO_COOKIE值

# 重启服务
sudo systemctl restart weibo-scheduler@YOUR_USER
```

### 问题3：磁盘空间不足

```bash
# 清理旧日志
find ~/weibo-archive/logs -type f -mtime +7 -delete

# 压缩图片（可选）
# 使用ImageMagick批量压缩
sudo apt install imagemagick
find ~/weibo-archive/data/images -name "*.jpg" -exec mogrify -quality 85 {} \;
```

### 问题4：数据库锁定

```bash
# 检查是否有多个进程访问数据库
ps aux | grep python

# 停止所有相关服务
sudo systemctl stop weibo-scheduler@YOUR_USER
sudo systemctl stop weibo-flask@YOUR_USER

# 等待几秒后重启
sleep 5
sudo systemctl start weibo-scheduler@YOUR_USER
sudo systemctl start weibo-flask@YOUR_USER
```

---

## 常见问题

### Q: 如何访问Web界面？

A:
- 直接访问：`http://your-vps-ip:5000`
- 通过Nginx：`http://your-domain.com`
- 通过HTTPS：`https://your-domain.com`（需配置SSL）

### Q: 如何更改调度间隔？

A: 修改 `.env` 文件中的调度器配置，然后重启服务：
```bash
nano ~/weibo-archive/.env
sudo systemctl restart weibo-scheduler@YOUR_USER
```

### Q: 如何添加多个博主？

A: 环境变量方式目前只支持单个博主。如需多个博主，建议使用配置文件方式或修改代码支持多个环境变量。

### Q: 数据库会占用多少空间？

A: 取决于微博数量和图片：
- 文字数据：约 1KB/条微博
- 图片：约 100-500KB/张
- 示例：3万条微博 + 图片 ≈ 5-10GB

---

## 优化建议

### 1. 数据库优化

```sql
-- 定期执行VACUUM释放空间
sqlite3 ~/weibo-archive/data/database.db "VACUUM;"

-- 分析查询性能
sqlite3 ~/weibo-archive/data/database.db "ANALYZE;"
```

### 2. Nginx缓存

在nginx.conf中添加：
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=weibo_cache:10m max_size=1g;

location / {
    proxy_cache weibo_cache;
    proxy_cache_valid 200 5m;
    # ...
}
```

### 3. 使用CDN

将静态资源（图片、CSS、JS）托管到CDN可以大幅提升访问速度。

---

## 下一步

1. ✅ 完成基础部署
2. ⬜ 配置SSL证书（Let's Encrypt）
3. ⬜ 设置监控告警（可选）
4. ⬜ 配置CDN加速（可选）
5. ⬜ 定期备份测试

---

祝部署顺利！如有问题，请查看日志或提交Issue。
