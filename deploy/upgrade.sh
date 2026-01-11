#!/bin/bash
# 微博归档系统 - 一键升级脚本
# 用途：更新已部署的系统到最新版本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取实际用户
ACTUAL_USER=${USER}
PROJECT_DIR="${HOME}/weibo-archive"

echo "=========================================="
echo "微博归档系统 - 一键升级"
echo "=========================================="
echo ""
echo "用户: $ACTUAL_USER"
echo "项目目录: $PROJECT_DIR"
echo ""

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误：项目目录不存在: $PROJECT_DIR${NC}"
    echo "请先运行部署脚本安装系统"
    exit 1
fi

cd "$PROJECT_DIR"

# 检查是否是git仓库
if [ ! -d ".git" ]; then
    echo -e "${RED}错误：不是Git仓库${NC}"
    echo "无法自动升级，请手动下载最新代码"
    exit 1
fi

echo -e "${BLUE}[1/8]${NC} 检查当前状态..."

# 检查是否有未提交的更改
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${YELLOW}警告：检测到本地未提交的更改${NC}"
    echo ""
    git status --short
    echo ""
    read -p "是否继续升级？未提交的更改可能会丢失 (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo "升级已取消"
        exit 0
    fi
fi

# 显示当前版本
CURRENT_COMMIT=$(git rev-parse --short HEAD)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "当前版本: $CURRENT_BRANCH @ $CURRENT_COMMIT"

echo ""
echo -e "${BLUE}[2/8]${NC} 获取最新代码..."

# 备份当前版本（如果有本地更改）
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    BACKUP_BRANCH="backup-$(date +%Y%m%d-%H%M%S)"
    git branch "$BACKUP_BRANCH"
    echo -e "${GREEN}✓${NC} 已创建备份分支: $BACKUP_BRANCH"
fi

# 拉取最新代码
if git pull origin main; then
    NEW_COMMIT=$(git rev-parse --short HEAD)
    if [ "$CURRENT_COMMIT" = "$NEW_COMMIT" ]; then
        echo -e "${GREEN}✓${NC} 已是最新版本，无需更新"
        SKIP_RESTART=true
    else
        echo -e "${GREEN}✓${NC} 代码已更新: $CURRENT_COMMIT -> $NEW_COMMIT"
        SKIP_RESTART=false
    fi
else
    echo -e "${RED}错误：拉取代码失败${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}[3/8]${NC} 更新Python依赖..."

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate

    # 更新pip
    pip install --upgrade pip -q

    # 安装/更新依赖
    if pip install -r requirements.txt -q; then
        echo -e "${GREEN}✓${NC} Python依赖已更新"
    else
        echo -e "${YELLOW}!${NC} 依赖更新失败，但继续执行"
    fi
else
    echo -e "${YELLOW}!${NC} 虚拟环境不存在，跳过依赖更新"
fi

echo ""
echo -e "${BLUE}[4/8]${NC} 检查数据库..."

# 检查数据库是否存在
if [ -f "data/database.db" ]; then
    DB_SIZE=$(du -h data/database.db | cut -f1)
    WEIBO_COUNT=$(sqlite3 data/database.db "SELECT COUNT(*) FROM weibos" 2>/dev/null || echo "未知")
    echo -e "${GREEN}✓${NC} 数据库正常 (大小: $DB_SIZE, 微博数: $WEIBO_COUNT)"
else
    echo -e "${YELLOW}!${NC} 数据库不存在，升级后首次运行将创建"
fi

echo ""
echo -e "${BLUE}[5/8]${NC} 更新systemd服务..."

# 检查是否有systemd服务
if systemctl list-unit-files | grep -q "weibo-scheduler@.service"; then
    # 复制新的服务文件
    if [ -f "deploy/weibo-scheduler.service" ]; then
        sudo cp deploy/weibo-scheduler.service /etc/systemd/system/weibo-scheduler@.service
        echo -e "${GREEN}✓${NC} 调度器服务配置已更新"
    fi

    if [ -f "deploy/weibo-flask.service" ]; then
        sudo cp deploy/weibo-flask.service /etc/systemd/system/weibo-flask@.service
        echo -e "${GREEN}✓${NC} Flask服务配置已更新"
    fi

    # 重新加载systemd
    sudo systemctl daemon-reload
    echo -e "${GREEN}✓${NC} systemd已重新加载"
else
    echo -e "${YELLOW}!${NC} 未检测到systemd服务，跳过"
fi

echo ""
echo -e "${BLUE}[6/8]${NC} 检查Nginx配置..."

# 检查Nginx是否安装
if command -v nginx >/dev/null 2>&1; then
    if [ -f "/etc/nginx/sites-available/weibo-archive" ]; then
        echo -e "${YELLOW}提示：${NC}Nginx配置文件已存在"
        echo "如需更新Nginx配置，请手动执行："
        echo "  sudo cp deploy/nginx.conf /etc/nginx/sites-available/weibo-archive"
        echo "  sudo nginx -t && sudo systemctl reload nginx"
    else
        echo -e "${YELLOW}!${NC} Nginx未配置，如需配置请参考文档"
    fi
else
    echo -e "${YELLOW}!${NC} Nginx未安装，跳过"
fi

echo ""
echo -e "${BLUE}[7/8]${NC} 重启服务..."

if [ "$SKIP_RESTART" = true ]; then
    echo -e "${YELLOW}!${NC} 版本未变化，跳过重启"
else
    # 重启调度器
    if systemctl is-active --quiet "weibo-scheduler@$ACTUAL_USER"; then
        echo "正在重启调度器服务..."
        if sudo systemctl restart "weibo-scheduler@$ACTUAL_USER"; then
            echo -e "${GREEN}✓${NC} 调度器服务已重启"
        else
            echo -e "${RED}!${NC} 调度器重启失败"
        fi
    else
        echo -e "${YELLOW}!${NC} 调度器服务未运行，跳过重启"
    fi

    # 重启Flask
    if systemctl is-active --quiet "weibo-flask@$ACTUAL_USER"; then
        echo "正在重启Flask服务..."
        if sudo systemctl restart "weibo-flask@$ACTUAL_USER"; then
            echo -e "${GREEN}✓${NC} Flask服务已重启"
        else
            echo -e "${RED}!${NC} Flask重启失败"
        fi
    else
        echo -e "${YELLOW}!${NC} Flask服务未运行，跳过重启"
    fi
fi

echo ""
echo -e "${BLUE}[8/8]${NC} 验证服务状态..."

# 等待服务启动
sleep 2

# 检查服务状态
echo ""
echo "服务状态："

if systemctl is-active --quiet "weibo-scheduler@$ACTUAL_USER"; then
    echo -e "  调度器: ${GREEN}运行中${NC}"
else
    echo -e "  调度器: ${RED}未运行${NC}"
fi

if systemctl is-active --quiet "weibo-flask@$ACTUAL_USER"; then
    echo -e "  Flask:  ${GREEN}运行中${NC}"
else
    echo -e "  Flask:  ${YELLOW}未运行${NC}"
fi

# 检查端口
if netstat -tlnp 2>/dev/null | grep -q ":5000"; then
    echo -e "  端口:   ${GREEN}5000已监听${NC}"
else
    echo -e "  端口:   ${YELLOW}5000未监听${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 升级完成！${NC}"
echo "=========================================="
echo ""

# 显示更新日志
if [ "$SKIP_RESTART" = false ]; then
    echo "更新内容："
    git log --oneline --pretty=format:"  %h - %s" "$CURRENT_COMMIT"..HEAD
    echo ""
    echo ""
fi

echo "当前版本: $(git rev-parse --short HEAD)"
echo ""
echo "常用命令："
echo "  查看调度器状态: sudo systemctl status weibo-scheduler@$ACTUAL_USER"
echo "  查看Flask状态:  sudo systemctl status weibo-flask@$ACTUAL_USER"
echo "  查看调度器日志: tail -f ~/weibo-archive/logs/scheduler.log"
echo "  查看Flask日志:  tail -f ~/weibo-archive/logs/gunicorn_access.log"
echo ""
echo "访问地址："
if [ -f "/etc/nginx/sites-enabled/weibo-archive" ]; then
    DOMAIN=$(grep "server_name" /etc/nginx/sites-available/weibo-archive 2>/dev/null | head -1 | awk '{print $2}' | tr -d ';')
    if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "your-domain.com" ]; then
        echo "  https://$DOMAIN"
    else
        echo "  http://$(hostname -I | awk '{print $1}'):5000"
    fi
else
    echo "  http://$(hostname -I | awk '{print $1}'):5000"
fi
echo ""

# 检查是否需要手动操作
if [ -f ".upgrade_notes" ]; then
    echo -e "${YELLOW}⚠️  重要提示：${NC}"
    cat .upgrade_notes
    echo ""
fi
