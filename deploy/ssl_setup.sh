#!/bin/bash
# SSL/HTTPS 一键配置脚本
# 用途：自动配置Let's Encrypt免费SSL证书

set -e

echo "=========================================="
echo "微博归档系统 - HTTPS自动配置"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误：请使用sudo运行此脚本${NC}"
    echo "用法: sudo ./ssl_setup.sh"
    exit 1
fi

# 获取实际用户（即使使用sudo）
ACTUAL_USER=${SUDO_USER:-$(whoami)}
PROJECT_DIR="/home/$ACTUAL_USER/weibo-archive"

echo "当前用户: $ACTUAL_USER"
echo "项目目录: $PROJECT_DIR"
echo ""

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误：项目目录不存在: $PROJECT_DIR${NC}"
    echo "请先运行 vps_setup.sh 安装基础环境"
    exit 1
fi

# 获取域名
echo -e "${YELLOW}请输入配置信息：${NC}"
echo ""
read -p "域名（例如：weibo.example.com）: " DOMAIN

# 验证域名格式
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}错误：域名不能为空${NC}"
    exit 1
fi

# 获取邮箱
read -p "邮箱（用于证书到期通知）: " EMAIL

# 验证邮箱格式
if [ -z "$EMAIL" ]; then
    echo -e "${RED}错误：邮箱不能为空${NC}"
    exit 1
fi

# 是否配置www子域名
read -p "是否同时配置 www.$DOMAIN？(y/n): " USE_WWW
if [ "$USE_WWW" = "y" ] || [ "$USE_WWW" = "Y" ]; then
    WWW_DOMAIN="www.$DOMAIN"
    DOMAIN_LIST="-d $DOMAIN -d $WWW_DOMAIN"
    NGINX_SERVER_NAME="$DOMAIN $WWW_DOMAIN"
else
    DOMAIN_LIST="-d $DOMAIN"
    NGINX_SERVER_NAME="$DOMAIN"
fi

echo ""
echo -e "${GREEN}配置信息：${NC}"
echo "- 域名: $NGINX_SERVER_NAME"
echo "- 邮箱: $EMAIL"
echo "- 用户: $ACTUAL_USER"
echo "- 项目路径: $PROJECT_DIR"
echo ""

read -p "确认继续？(y/n): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "=========================================="
echo "开始配置HTTPS..."
echo "=========================================="
echo ""

# 1. 检查DNS解析
echo -e "${YELLOW}[1/7]${NC} 检查DNS解析..."
if ! host $DOMAIN > /dev/null 2>&1; then
    echo -e "${RED}警告：域名 $DOMAIN 无法解析${NC}"
    echo "请确保域名已正确解析到此服务器IP"
    read -p "是否继续？(y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} DNS解析正常"
fi

# 2. 安装Certbot
echo -e "${YELLOW}[2/7]${NC} 安装Certbot..."
apt update -qq
apt install -y certbot python3-certbot-nginx > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Certbot安装完成"

# 3. 配置Nginx
echo -e "${YELLOW}[3/7]${NC} 配置Nginx..."

# 创建Nginx配置文件
cat > /etc/nginx/sites-available/weibo-archive <<EOF
# HTTP服务器 - 用于Let's Encrypt验证和重定向
server {
    listen 80;
    listen [::]:80;
    server_name $NGINX_SERVER_NAME;

    # Let's Encrypt验证路径
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # 临时允许访问（获取证书后会自动改为HTTPS重定向）
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
ln -sf /etc/nginx/sites-available/weibo-archive /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试配置
if nginx -t > /dev/null 2>&1; then
    systemctl restart nginx
    echo -e "${GREEN}✓${NC} Nginx配置完成"
else
    echo -e "${RED}错误：Nginx配置测试失败${NC}"
    nginx -t
    exit 1
fi

# 4. 配置防火墙
echo -e "${YELLOW}[4/7]${NC} 配置防火墙..."
if command -v ufw > /dev/null 2>&1; then
    ufw allow 80/tcp > /dev/null 2>&1 || true
    ufw allow 443/tcp > /dev/null 2>&1 || true
    echo -e "${GREEN}✓${NC} UFW防火墙规则已添加"
else
    echo -e "${YELLOW}!${NC} UFW未安装，跳过防火墙配置"
fi

# 5. 获取SSL证书
echo -e "${YELLOW}[5/7]${NC} 获取SSL证书（可能需要1-2分钟）..."
echo "正在向Let's Encrypt申请证书..."

if certbot --nginx $DOMAIN_LIST \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    --redirect \
    --hsts \
    --staple-ocsp \
    --must-staple; then
    echo -e "${GREEN}✓${NC} SSL证书获取成功"
else
    echo -e "${RED}错误：SSL证书获取失败${NC}"
    echo ""
    echo "可能的原因："
    echo "1. 域名未正确解析到此服务器"
    echo "2. 80端口被占用或防火墙未开放"
    echo "3. 域名提供商限制"
    echo ""
    echo "请检查后重试"
    exit 1
fi

# 6. 优化SSL配置
echo -e "${YELLOW}[6/7]${NC} 优化SSL配置..."

# 添加安全头和性能优化
cat > /etc/nginx/conf.d/ssl-params.conf <<EOF
# SSL性能优化
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# SSL安全配置
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers off;

# 安全头
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
EOF

# 更新Nginx配置，添加静态文件服务
cat > /etc/nginx/sites-available/weibo-archive <<EOF
# HTTP服务器 - 重定向到HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $NGINX_SERVER_NAME;

    # Let's Encrypt验证路径
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # 重定向到HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS服务器
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $NGINX_SERVER_NAME;

    # SSL证书（由Certbot自动管理）
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # 日志
    access_log /var/log/nginx/weibo-archive-access.log;
    error_log /var/log/nginx/weibo-archive-error.log;

    # 反向代理到Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件直接服务（性能优化）
    location /static/ {
        alias $PROJECT_DIR/generator/templates/assets/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    location /images/ {
        alias $PROJECT_DIR/data/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 重启Nginx
nginx -t && systemctl restart nginx
echo -e "${GREEN}✓${NC} SSL配置优化完成"

# 7. 测试自动续期
echo -e "${YELLOW}[7/7]${NC} 测试证书自动续期..."
if certbot renew --dry-run > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} 自动续期测试通过"
else
    echo -e "${YELLOW}!${NC} 自动续期测试失败，但证书已成功安装"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ HTTPS配置完成！${NC}"
echo "=========================================="
echo ""
echo "访问地址："
echo -e "  ${GREEN}https://$DOMAIN${NC}"
if [ "$USE_WWW" = "y" ] || [ "$USE_WWW" = "Y" ]; then
    echo -e "  ${GREEN}https://$WWW_DOMAIN${NC}"
fi
echo ""
echo "证书信息："
echo "  位置: /etc/letsencrypt/live/$DOMAIN/"
echo "  邮箱: $EMAIL"
echo "  有效期: 90天（自动续期）"
echo ""
echo "证书管理命令："
echo "  查看证书: sudo certbot certificates"
echo "  手动续期: sudo certbot renew"
echo "  撤销证书: sudo certbot revoke --cert-path /etc/letsencrypt/live/$DOMAIN/cert.pem"
echo ""
echo "建议："
echo "1. 访问 https://www.ssllabs.com/ssltest/ 测试SSL评级"
echo "2. 定期检查证书是否自动续期成功"
echo "3. 备份证书目录: /etc/letsencrypt/"
echo ""
