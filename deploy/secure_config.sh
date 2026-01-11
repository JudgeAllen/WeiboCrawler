#!/bin/bash
# 安全配置脚本 - 使用环境变量保护敏感信息

set -e

echo "=========================================="
echo "配置安全的环境变量"
echo "=========================================="
echo ""

# 创建环境变量配置文件
ENV_FILE=~/weibo-archive/.env

echo "请输入配置信息："
echo ""

# 获取微博Cookie
echo "1. 微博Cookie（从浏览器复制完整Cookie）："
read -s WEIBO_COOKIE
echo ""

# 获取用户UID
echo "2. 微博用户UID（默认: 1401527553）："
read WEIBO_UID
WEIBO_UID=${WEIBO_UID:-1401527553}

# 获取用户名称
echo "3. 用户名称（默认: tombkeeper）："
read WEIBO_NAME
WEIBO_NAME=${WEIBO_NAME:-tombkeeper}

# 生成.env文件
cat > $ENV_FILE <<EOF
# 微博爬虫环境变量配置
# 警告：此文件包含敏感信息，不要提交到Git

# 微博Cookie
WEIBO_COOKIE="$WEIBO_COOKIE"

# 目标用户
WEIBO_UID="$WEIBO_UID"
WEIBO_NAME="$WEIBO_NAME"

# 数据库路径
DATABASE_PATH="/home/\$USER/weibo-archive/data/database.db"

# 图片路径
IMAGE_PATH="/home/\$USER/weibo-archive/data/images"

# Flask配置
FLASK_ENV="production"
FLASK_SECRET_KEY="$(openssl rand -hex 32)"
FLASK_HOST="127.0.0.1"
FLASK_PORT="5000"
EOF

# 设置文件权限（仅所有者可读）
chmod 600 $ENV_FILE

echo ""
echo "✅ 环境变量配置文件已创建: $ENV_FILE"
echo "⚠️  文件权限已设为仅所有者可读（600）"
echo ""

# 添加到.bashrc自动加载
if ! grep -q "weibo-archive/.env" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# 加载微博归档环境变量" >> ~/.bashrc
    echo "if [ -f ~/weibo-archive/.env ]; then" >> ~/.bashrc
    echo "    export \$(cat ~/weibo-archive/.env | grep -v '^#' | xargs)" >> ~/.bashrc
    echo "fi" >> ~/.bashrc
    echo "✅ 环境变量已添加到 ~/.bashrc"
fi

echo ""
echo "下一步："
echo "1. 重新加载环境变量: source ~/.bashrc"
echo "2. 修改爬虫代码使用环境变量（见文档）"
echo ""
