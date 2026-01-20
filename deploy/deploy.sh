#!/bin/bash
# 微博归档系统 - 一键部署脚本
# 用途：在已下载代码的基础上完成全部部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 项目目录（脚本所在目录的父目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ACTUAL_USER=${USER}

echo "=========================================="
echo "微博归档系统 - 一键部署"
echo "=========================================="
echo ""
echo "项目目录: $PROJECT_DIR"
echo "部署用户: $ACTUAL_USER"
echo ""

cd "$PROJECT_DIR"

# ========================================
# 步骤1：系统环境检查
# ========================================
echo -e "${BLUE}[1/10]${NC} ${BOLD}检查系统环境...${NC}"

# 检查操作系统
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}错误：无法识别操作系统${NC}"
    exit 1
fi

OS_NAME=$(grep "^NAME=" /etc/os-release | cut -d'"' -f2)
OS_VERSION=$(grep "^VERSION_ID=" /etc/os-release | cut -d'"' -f2)
echo "操作系统: $OS_NAME $OS_VERSION"

# 检查是否为Ubuntu
if ! grep -qi "ubuntu" /etc/os-release; then
    echo -e "${YELLOW}警告：此脚本针对Ubuntu优化，其他系统可能需要手动调整${NC}"
    read -p "是否继续？(y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 0
    fi
fi

# ========================================
# 步骤2：安装系统依赖
# ========================================
echo ""
echo -e "${BLUE}[2/10]${NC} ${BOLD}安装系统依赖...${NC}"

echo "更新软件包列表..."
sudo apt update -qq

echo "安装必需软件包..."
sudo DEBIAN_FRONTEND=noninteractive apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    sqlite3 \
    curl \
    > /dev/null 2>&1

echo -e "${GREEN}✓${NC} 系统依赖安装完成"

# ========================================
# 步骤3：创建Python虚拟环境
# ========================================
echo ""
echo -e "${BLUE}[3/10]${NC} ${BOLD}创建Python虚拟环境...${NC}"

if [ -d "venv" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} 虚拟环境创建完成"
fi

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip -q

# 安装依赖
echo "安装Python依赖包..."
pip install -r requirements.txt -q

echo -e "${GREEN}✓${NC} Python依赖安装完成"

# ========================================
# 步骤4：配置环境变量
# ========================================
echo ""
echo -e "${BLUE}[4/10]${NC} ${BOLD}配置环境变量...${NC}"

ENV_FILE="$PROJECT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}环境变量文件已存在：$ENV_FILE${NC}"
    read -p "是否重新配置？(y/n): " RECONFIG
    if [ "$RECONFIG" != "y" ]; then
        echo "跳过环境变量配置"
    else
        NEED_CONFIG=true
    fi
else
    NEED_CONFIG=true
fi

if [ "$NEED_CONFIG" = true ]; then
    echo ""
    echo "请输入微博配置信息："
    echo ""

    # 获取Cookie
    echo -e "${YELLOW}1. 微博Cookie（必填）${NC}"
    echo "   获取方法：登录weibo.com，F12打开开发者工具，Network标签中复制Cookie"
    read -p "   请粘贴Cookie: " WEIBO_COOKIE

    # 获取UID
    echo ""
    echo -e "${YELLOW}2. 目标用户UID${NC}"
    read -p "   UID（默认: 1401527553）: " WEIBO_UID
    WEIBO_UID=${WEIBO_UID:-1401527553}

    # 获取用户名
    echo ""
    echo -e "${YELLOW}3. 用户名称${NC}"
    read -p "   名称（默认: tombkeeper）: " WEIBO_NAME
    WEIBO_NAME=${WEIBO_NAME:-tombkeeper}

    # 生成.env文件
    cat > "$ENV_FILE" <<EOF
# 微博爬虫环境变量配置
# 警告：此文件包含敏感信息，不要提交到Git

# 微博Cookie
WEIBO_COOKIE="$WEIBO_COOKIE"

# 目标用户
WEIBO_UID="$WEIBO_UID"
WEIBO_NAME="$WEIBO_NAME"

# 数据库路径
DATABASE_PATH="$PROJECT_DIR/data/database.db"

# 图片路径
IMAGE_PATH="$PROJECT_DIR/data/images"

# Flask配置
FLASK_ENV="production"
FLASK_SECRET_KEY="$(openssl rand -hex 32)"
FLASK_HOST="127.0.0.1"
FLASK_PORT="5000"
EOF

    # 设置权限
    chmod 600 "$ENV_FILE"

    echo ""
    echo -e "${GREEN}✓${NC} 环境变量配置完成"
fi

# ========================================
# 步骤5：创建必要目录
# ========================================
echo ""
echo -e "${BLUE}[5/10]${NC} ${BOLD}创建必要目录...${NC}"

mkdir -p "$PROJECT_DIR/data/images"
mkdir -p "$PROJECT_DIR/logs"

echo -e "${GREEN}✓${NC} 目录创建完成"

# ========================================
# 步骤6：测试爬虫（可选）
# ========================================
echo ""
echo -e "${BLUE}[6/10]${NC} ${BOLD}测试爬虫配置...${NC}"

read -p "是否立即运行一次爬虫测试？(y/n): " TEST_CRAWLER
if [ "$TEST_CRAWLER" = "y" ]; then
    echo "正在运行爬虫..."
    source "$ENV_FILE"
    cd "$PROJECT_DIR/crawler"
    timeout 60 python weibo_spider.py || true
    cd "$PROJECT_DIR"

    # 检查数据库
    if [ -f "$PROJECT_DIR/data/database.db" ]; then
        WEIBO_COUNT=$(sqlite3 "$PROJECT_DIR/data/database.db" "SELECT COUNT(*) FROM weibos" 2>/dev/null || echo "0")
        echo -e "${GREEN}✓${NC} 爬虫测试完成，已抓取 $WEIBO_COUNT 条微博"
    else
        echo -e "${YELLOW}!${NC} 数据库未创建，可能Cookie无效或网络问题"
    fi
else
    echo "跳过爬虫测试"
fi

# ========================================
# 步骤7：配置systemd服务
# ========================================
echo ""
echo -e "${BLUE}[7/10]${NC} ${BOLD}配置systemd服务...${NC}"

# 安装调度器服务
echo "安装调度器服务..."
sudo cp "$PROJECT_DIR/deploy/weibo-scheduler.service" /etc/systemd/system/weibo-scheduler@.service

# 安装Flask服务
echo "安装Flask服务..."
sudo cp "$PROJECT_DIR/deploy/weibo-flask.service" /etc/systemd/system/weibo-flask@.service

# 重新加载systemd
sudo systemctl daemon-reload

echo -e "${GREEN}✓${NC} systemd服务配置完成"

# ========================================
# 步骤8：启动服务
# ========================================
echo ""
echo -e "${BLUE}[8/10]${NC} ${BOLD}启动服务...${NC}"

# 启动并启用调度器
echo "启动调度器服务..."
sudo systemctl enable "weibo-scheduler@$ACTUAL_USER" > /dev/null 2>&1
sudo systemctl start "weibo-scheduler@$ACTUAL_USER"

# 等待启动
sleep 2

if systemctl is-active --quiet "weibo-scheduler@$ACTUAL_USER"; then
    echo -e "${GREEN}✓${NC} 调度器服务已启动"
else
    echo -e "${YELLOW}!${NC} 调度器启动失败，请检查日志"
fi

# 启动并启用Flask
echo "启动Flask服务..."
sudo systemctl enable "weibo-flask@$ACTUAL_USER" > /dev/null 2>&1
sudo systemctl start "weibo-flask@$ACTUAL_USER"

# 等待启动
sleep 3

if systemctl is-active --quiet "weibo-flask@$ACTUAL_USER"; then
    echo -e "${GREEN}✓${NC} Flask服务已启动"
else
    echo -e "${YELLOW}!${NC} Flask启动失败，请检查日志"
fi

# ========================================
# 步骤9：配置防火墙
# ========================================
echo ""
echo -e "${BLUE}[9/10]${NC} ${BOLD}配置防火墙...${NC}"

if command -v ufw > /dev/null 2>&1; then
    # 允许SSH
    sudo ufw allow 22/tcp > /dev/null 2>&1 || true

    # 允许HTTP/HTTPS
    sudo ufw allow 80/tcp > /dev/null 2>&1 || true
    sudo ufw allow 443/tcp > /dev/null 2>&1 || true

    # 如果未启用，询问是否启用
    if ! sudo ufw status | grep -q "Status: active"; then
        read -p "是否启用UFW防火墙？(y/n): " ENABLE_UFW
        if [ "$ENABLE_UFW" = "y" ]; then
            sudo ufw --force enable
            echo -e "${GREEN}✓${NC} 防火墙已启用"
        else
            echo "防火墙未启用"
        fi
    else
        echo -e "${GREEN}✓${NC} 防火墙规则已添加"
    fi
else
    echo -e "${YELLOW}!${NC} UFW未安装，跳过防火墙配置"
fi

# ========================================
# 步骤10：配置HTTPS（可选）
# ========================================
echo ""
echo -e "${BLUE}[10/10]${NC} ${BOLD}HTTPS配置（可选）...${NC}"

read -p "是否现在配置HTTPS/SSL证书？(y/n): " SETUP_SSL
if [ "$SETUP_SSL" = "y" ]; then
    if [ -f "$PROJECT_DIR/deploy/ssl_setup.sh" ]; then
        chmod +x "$PROJECT_DIR/deploy/ssl_setup.sh"
        sudo "$PROJECT_DIR/deploy/ssl_setup.sh"
    else
        echo -e "${RED}错误：ssl_setup.sh不存在${NC}"
    fi
else
    echo "跳过HTTPS配置，可以稍后运行："
    echo "  sudo $PROJECT_DIR/deploy/ssl_setup.sh"
fi

# ========================================
# 部署完成
# ========================================
echo ""
echo "=========================================="
echo -e "${GREEN}${BOLD}✅ 部署完成！${NC}"
echo "=========================================="
echo ""

# 获取服务器IP
SERVER_IP=$(hostname -I | awk '{print $1}')

# 显示服务状态
echo -e "${BOLD}服务状态：${NC}"
if systemctl is-active --quiet "weibo-scheduler@$ACTUAL_USER"; then
    echo -e "  调度器: ${GREEN}运行中${NC}"
else
    echo -e "  调度器: ${RED}未运行${NC}"
fi

if systemctl is-active --quiet "weibo-flask@$ACTUAL_USER"; then
    echo -e "  Flask:  ${GREEN}运行中${NC}"
else
    echo -e "  Flask:  ${RED}未运行${NC}"
fi

# 检查端口
if netstat -tlnp 2>/dev/null | grep -q ":5000"; then
    echo -e "  端口:   ${GREEN}5000已监听${NC}"
else
    echo -e "  端口:   ${YELLOW}5000未监听${NC}"
fi

echo ""
echo -e "${BOLD}访问地址：${NC}"
if [ "$SETUP_SSL" = "y" ]; then
    DOMAIN=$(grep "server_name" /etc/nginx/sites-available/weibo-archive 2>/dev/null | head -1 | awk '{print $2}' | tr -d ';')
    if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "your-domain.com" ]; then
        echo -e "  ${GREEN}https://$DOMAIN${NC}"
    fi
else
    echo -e "  ${YELLOW}http://$SERVER_IP:5000${NC}"
    echo -e "  ${YELLOW}⚠️  HTTP不安全，建议配置HTTPS${NC}"
fi

echo ""
echo -e "${BOLD}常用命令：${NC}"
echo "  查看调度器状态: sudo systemctl status weibo-scheduler@$ACTUAL_USER"
echo "  查看Flask状态:  sudo systemctl status weibo-flask@$ACTUAL_USER"
echo "  查看调度器日志: tail -f $PROJECT_DIR/logs/scheduler.log"
echo "  查看Flask日志:  tail -f $PROJECT_DIR/logs/gunicorn_access.log"
echo "  停止调度器:     sudo systemctl stop weibo-scheduler@$ACTUAL_USER"
echo "  停止Flask:      sudo systemctl stop weibo-flask@$ACTUAL_USER"
echo "  重启调度器:     sudo systemctl restart weibo-scheduler@$ACTUAL_USER"
echo "  重启Flask:      sudo systemctl restart weibo-flask@$ACTUAL_USER"
echo "  配置HTTPS:      sudo $PROJECT_DIR/deploy/ssl_setup.sh"
echo "  升级系统:       $PROJECT_DIR/deploy/upgrade.sh"

echo ""
echo -e "${BOLD}重要文件位置：${NC}"
echo "  项目目录:   $PROJECT_DIR"
echo "  配置文件:   $PROJECT_DIR/.env"
echo "  数据库:     $PROJECT_DIR/data/database.db"
echo "  图片目录:   $PROJECT_DIR/data/images"
echo "  日志目录:   $PROJECT_DIR/logs"

echo ""
echo -e "${BOLD}下一步：${NC}"
if [ "$SETUP_SSL" != "y" ]; then
    echo "  1. ${YELLOW}配置HTTPS（强烈推荐）${NC}"
    echo "     sudo $PROJECT_DIR/deploy/ssl_setup.sh"
fi
echo "  2. 检查服务日志确认正常运行"
echo "  3. 访问Web界面验证"
echo "  4. 定期备份数据库"

echo ""
echo -e "${GREEN}部署成功！微博归档系统已开始运行${NC}"
echo ""
