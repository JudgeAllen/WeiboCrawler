#!/bin/bash
# 安装systemd服务脚本

set -e

echo "=========================================="
echo "安装微博归档系统服务"
echo "=========================================="
echo ""

# 获取当前用户名
CURRENT_USER=$(whoami)
PROJECT_DIR=~/WeiboCrawler

echo "当前用户: $CURRENT_USER"
echo "项目目录: $PROJECT_DIR"
echo ""



# 创建日志目录
echo "创建日志目录..."
mkdir -p $PROJECT_DIR/logs

# 安装调度器服务
echo "1/3 安装调度器服务..."
sudo cp $PROJECT_DIR/deploy/weibo-scheduler@.service /etc/systemd/system/weibo-scheduler@.service
sudo systemctl daemon-reload

# 安装Flask服务（可选）
echo "2/3 安装Flask服务..."
sudo cp $PROJECT_DIR/deploy/weibo-flask@.service /etc/systemd/system/weibo-flask@.service
sudo systemctl daemon-reload

# 询问是否启动服务
echo ""
echo "3/3 配置服务..."
echo ""

read -p "是否启动调度器服务？(y/n): " START_SCHEDULER
if [ "$START_SCHEDULER" = "y" ]; then
    sudo systemctl enable weibo-scheduler@$CURRENT_USER
    sudo systemctl start weibo-scheduler@$CURRENT_USER
    echo "✅ 调度器服务已启动"
fi

echo ""
read -p "是否启动Flask Web服务？(y/n): " START_FLASK
if [ "$START_FLASK" = "y" ]; then
    sudo systemctl enable weibo-flask@$CURRENT_USER
    sudo systemctl start weibo-flask@$CURRENT_USER
    echo "✅ Flask服务已启动"
fi

echo ""
echo "=========================================="
echo "✅ 服务安装完成！"
echo "=========================================="
echo ""
echo "常用命令："
echo ""
echo "# 查看调度器状态"
echo "sudo systemctl status weibo-scheduler@$CURRENT_USER"
echo ""
echo "# 查看调度器日志"
echo "tail -f ~/weibo-archive/logs/scheduler.log"
echo ""
echo "# 停止/启动/重启调度器"
echo "sudo systemctl stop/start/restart weibo-scheduler@$CURRENT_USER"
echo ""
echo "# 查看Flask状态"
echo "sudo systemctl status weibo-flask@$CURRENT_USER"
echo ""
echo "# 查看Flask日志"
echo "tail -f ~/weibo-archive/logs/flask.log"
echo ""
