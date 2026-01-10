# HTTPS/SSL配置指南

## 概述

本指南将帮助你为微博归档系统配置免费的HTTPS证书（Let's Encrypt），确保数据传输安全。

---

## 前置条件

1. ✅ 已有域名（或使用VPS提供商的二级域名）
2. ✅ 域名已解析到VPS的IP地址
3. ✅ VPS已安装Nginx
4. ✅ 防火墙已开放80和443端口

---

## 方案1：使用Let's Encrypt（推荐）

### 步骤1：安装Certbot

```bash
# 更新软件包
sudo apt update

# 安装Certbot和Nginx插件
sudo apt install certbot python3-certbot-nginx -y

# 验证安装
certbot --version
```

### 步骤2：配置域名

**选项A：如果已有域名**

1. 登录域名提供商（阿里云、腾讯云、Cloudflare等）
2. 添加A记录：
   - 主机记录：`@` 或 `weibo`
   - 记录类型：`A`
   - 记录值：`你的VPS IP地址`
   - TTL：`600`（或默认）

3. 验证DNS解析：
```bash
# 替换为你的域名
ping your-domain.com
nslookup your-domain.com
dig your-domain.com
```

**选项B：如果没有域名**

可以使用免费域名服务：
- Freenom: https://www.freenom.com
- DuckDNS: https://www.duckdns.org
- No-IP: https://www.noip.com

或者使用VPS提供商的子域名（如果提供）。

### 步骤3：配置Nginx基础站点

创建Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/weibo-archive
```

粘贴以下内容（**替换 `your-domain.com` 和 `YOUR_USER`**）：

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # 替换为你的域名

    # 临时根目录（用于Let's Encrypt验证）
    root /var/www/html;

    # Let's Encrypt验证路径
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # 其他请求转发到Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/weibo-archive /etc/nginx/sites-enabled/

# 删除默认站点（可选）
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 步骤4：获取SSL证书

**方式A：自动配置（最简单，推荐）**

```bash
# 一键获取证书并自动配置Nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 按提示操作：
# 1. 输入邮箱（用于证书到期提醒）
# 2. 同意服务条款：Y
# 3. 是否分享邮箱：N（可选）
# 4. 选择是否强制HTTPS重定向：2（推荐选择2，强制HTTPS）
```

**方式B：仅获取证书，手动配置**

```bash
# 仅获取证书
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# 证书位置：
# - 证书：/etc/letsencrypt/live/your-domain.com/fullchain.pem
# - 私钥：/etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 步骤5：验证HTTPS

访问你的域名，应该会自动跳转到HTTPS：

```
https://your-domain.com
```

检查证书：

```bash
# 测试SSL配置
curl -I https://your-domain.com

# 查看证书信息
sudo certbot certificates

# 测试证书有效性
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

### 步骤6：配置自动续期

Let's Encrypt证书有效期90天，需要定期续期。

```bash
# 测试自动续期
sudo certbot renew --dry-run

# 查看定时任务（Certbot已自动添加）
sudo systemctl list-timers | grep certbot

# 手动续期（通常不需要）
sudo certbot renew
```

Certbot会自动创建systemd定时器，每天检查两次证书是否需要续期。

---

## 方案2：手动配置HTTPS（高级）

如果Certbot自动配置不符合需求，可以手动配置。

### 完整的Nginx HTTPS配置

创建配置文件：

```bash
sudo nano /etc/nginx/sites-available/weibo-archive
```

完整配置：

```nginx
# HTTP服务器 - 自动跳转到HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;

    # Let's Encrypt验证
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # 强制跳转HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS服务器
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    # HSTS（可选，30天）
    add_header Strict-Transport-Security "max-age=2592000" always;

    # 其他安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 日志
    access_log /var/log/nginx/weibo-archive-access.log;
    error_log /var/log/nginx/weibo-archive-error.log;

    # 反向代理到Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持（如需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件直接服务（性能优化）
    location /static/ {
        alias /home/YOUR_USER/weibo-archive/generator/templates/assets/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    location /images/ {
        alias /home/YOUR_USER/weibo-archive/data/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

替换配置中的：
- `your-domain.com` → 你的域名
- `YOUR_USER` → 你的Linux用户名

重启Nginx：

```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## 方案3：使用Cloudflare（备选）

如果域名托管在Cloudflare，可以使用Cloudflare的免费SSL。

### 步骤1：添加站点到Cloudflare

1. 访问 https://dash.cloudflare.com/
2. 添加你的域名
3. 按提示修改域名服务器（NS记录）

### 步骤2：配置SSL/TLS

1. 进入 SSL/TLS 设置
2. 加密模式选择：**Full (strict)** 或 **Full**
3. 边缘证书 → 始终使用HTTPS：开启
4. 自动HTTPS重写：开启

### 步骤3：配置源证书（可选）

Cloudflare → SSL/TLS → 源服务器 → 创建证书

然后在Nginx中使用Cloudflare的源证书。

### 优点

- ✅ 无需在VPS上安装证书
- ✅ 自动续期
- ✅ 免费CDN加速
- ✅ DDoS防护

### 缺点

- ⚠️ 需要域名托管在Cloudflare
- ⚠️ 流量经过Cloudflare

---

## 防火墙配置

确保VPS防火墙开放HTTPS端口：

```bash
# 使用UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status

# 或使用iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables-save
```

---

## 修改Flask配置（重要）

### 让Flask知道使用了HTTPS

编辑 `app.py`，添加HTTPS支持：

```python
from flask import Flask, request

app = Flask(__name__)

# 信任代理服务器的X-Forwarded-Proto头
class ReverseProxied:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # 从Nginx获取真实的协议（http/https）
        scheme = environ.get('HTTP_X_FORWARDED_PROTO', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app.wsgi_app = ReverseProxied(app.wsgi_app)

# ... 其余代码不变
```

或者更简单的方式，使用Flask扩展：

```bash
pip install Flask-SSLify
```

在 `app.py` 中：

```python
from flask import Flask
from flask_sslify import SSLify

app = Flask(__name__)

# 强制HTTPS（仅在生产环境）
if os.getenv('FLASK_ENV') == 'production':
    sslify = SSLify(app)

# ... 其余代码
```

重启Flask服务：

```bash
sudo systemctl restart weibo-flask@YOUR_USER
```

---

## 测试HTTPS配置

### 1. 浏览器测试

访问 `https://your-domain.com`，检查：
- ✅ 地址栏显示锁图标
- ✅ 证书有效
- ✅ HTTP自动跳转到HTTPS

### 2. 在线工具测试

- **SSL Labs**: https://www.ssllabs.com/ssltest/
  - 输入你的域名，获得A+评级最佳

- **SSL Checker**: https://www.sslchecker.com/sslchecker

### 3. 命令行测试

```bash
# 测试HTTPS连接
curl -I https://your-domain.com

# 测试HTTP重定向
curl -I http://your-domain.com

# 测试证书
openssl s_client -connect your-domain.com:443 -servername your-domain.com < /dev/null

# 测试证书到期时间
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

## 常见问题

### Q1: Certbot获取证书失败

**错误信息**：`Challenge failed for domain your-domain.com`

**解决方法**：
```bash
# 1. 检查域名解析
dig your-domain.com
ping your-domain.com

# 2. 检查80端口是否开放
sudo netstat -tlnp | grep :80

# 3. 检查防火墙
sudo ufw status
sudo ufw allow 80/tcp

# 4. 检查Nginx配置
sudo nginx -t

# 5. 重试
sudo certbot --nginx -d your-domain.com
```

### Q2: 证书已过期

Let's Encrypt证书90天有效，但应该自动续期。

**检查自动续期**：
```bash
# 查看续期定时器
sudo systemctl list-timers | grep certbot

# 手动续期
sudo certbot renew

# 强制续期（即使未到期）
sudo certbot renew --force-renewal
```

### Q3: 混合内容警告

浏览器显示"混合内容"警告（HTTPS页面加载HTTP资源）。

**解决方法**：
检查模板中的资源链接，确保使用HTTPS或相对路径：

```html
<!-- 错误 -->
<img src="http://example.com/image.jpg">

<!-- 正确 -->
<img src="https://example.com/image.jpg">
<!-- 或使用相对路径 -->
<img src="/images/image.jpg">
```

### Q4: Nginx 502 Bad Gateway

**原因**：Flask服务未运行或端口错误。

**解决方法**：
```bash
# 检查Flask服务
sudo systemctl status weibo-flask@YOUR_USER

# 检查Flask监听端口
sudo netstat -tlnp | grep :5000

# 重启Flask
sudo systemctl restart weibo-flask@YOUR_USER

# 查看Flask日志
tail -f ~/weibo-archive/logs/flask.log
```

### Q5: VPS提供商的防火墙

有些VPS提供商有额外的安全组/防火墙设置。

**检查**：
- 登录VPS管理面板
- 检查安全组规则
- 确保开放80和443端口

---

## 安全加固

### 1. 隐藏Nginx版本

编辑 `/etc/nginx/nginx.conf`：

```nginx
http {
    server_tokens off;
    # ...
}
```

### 2. 限制请求速率

在Nginx配置中添加：

```nginx
# 在http块中
limit_req_zone $binary_remote_addr zone=weibo:10m rate=10r/s;

# 在server块中
location / {
    limit_req zone=weibo burst=20;
    # ...
}
```

### 3. 启用OCSP Stapling

在HTTPS server块中添加：

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/your-domain.com/chain.pem;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

### 4. 配置更严格的HSTS

```nginx
# 1年HSTS，包含子域名
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

---

## 完整部署脚本

创建一键HTTPS部署脚本：

```bash
#!/bin/bash
# ssl_setup.sh - 自动配置HTTPS

set -e

echo "=========================================="
echo "HTTPS/SSL 自动配置脚本"
echo "=========================================="
echo ""

# 获取域名
read -p "请输入你的域名（例如：example.com）: " DOMAIN
read -p "请输入你的邮箱（用于证书通知）: " EMAIL

# 获取用户名
CURRENT_USER=$(whoami)

echo ""
echo "配置信息："
echo "- 域名: $DOMAIN"
echo "- 邮箱: $EMAIL"
echo "- 用户: $CURRENT_USER"
echo ""

read -p "确认继续？(y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "已取消"
    exit 0
fi

# 1. 安装Certbot
echo "1/5 安装Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. 创建Nginx配置
echo "2/5 配置Nginx..."
sudo tee /etc/nginx/sites-available/weibo-archive > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    root /var/www/html;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用配置
sudo ln -sf /etc/nginx/sites-available/weibo-archive /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 3. 开放端口
echo "3/5 配置防火墙..."
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 4. 获取证书
echo "4/5 获取SSL证书..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect

# 5. 测试自动续期
echo "5/5 测试证书自动续期..."
sudo certbot renew --dry-run

echo ""
echo "=========================================="
echo "✅ HTTPS配置完成！"
echo "=========================================="
echo ""
echo "现在可以访问："
echo "https://$DOMAIN"
echo ""
echo "证书位置："
echo "/etc/letsencrypt/live/$DOMAIN/"
echo ""
echo "证书将在到期前自动续期"
echo ""
```

保存为 `deploy/ssl_setup.sh` 并运行：

```bash
chmod +x deploy/ssl_setup.sh
./deploy/ssl_setup.sh
```

---

## 总结

**推荐步骤**：

1. ✅ 准备域名并解析到VPS
2. ✅ 安装Certbot：`sudo apt install certbot python3-certbot-nginx`
3. ✅ 配置基础Nginx
4. ✅ 获取证书：`sudo certbot --nginx -d your-domain.com`
5. ✅ 测试访问：`https://your-domain.com`
6. ✅ 验证自动续期：`sudo certbot renew --dry-run`

**安全检查**：
- ✅ HTTPS工作正常
- ✅ HTTP自动跳转HTTPS
- ✅ SSL评级A或A+
- ✅ 自动续期已配置
- ✅ 防火墙规则正确

完成后，你的微博归档系统就可以通过安全的HTTPS访问了！
