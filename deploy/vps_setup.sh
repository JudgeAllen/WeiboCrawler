#!/bin/bash
# VPS部署脚本 - Ubuntu 24
# 用途：一键配置微博归档系统运行环境

set -e  # 遇到错误立即退出

echo "=========================================="
echo "微博归档系统 VPS 部署脚本"
echo "=========================================="
echo ""

# 1. 更新系统
echo "1/8 更新系统软件包..."
sudo apt update
sudo apt upgrade -y

# 2. 安装Python 3.11+
echo "2/8 安装Python和pip..."
sudo apt install -y python3 python3-pip python3-venv

# 3. 安装Git
echo "3/8 安装Git..."
sudo apt install -y git

# 4. 安装Nginx（可选，用于反向代理）
echo "4/8 安装Nginx..."
sudo apt install -y nginx

# 5. 创建项目目录
echo "5/8 创建项目目录..."
mkdir -p ~/weibo-archive
cd ~/weibo-archive

# 6. 克隆仓库
echo "6/8 克隆代码仓库..."
read -p "请输入你的GitHub仓库URL (https://github.com/JudgeAllen/WeiboCrawler.git): " REPO_URL
REPO_URL=${REPO_URL:-https://github.com/JudgeAllen/WeiboCrawler.git}
git clone $REPO_URL .

# 7. 创建Python虚拟环境
echo "7/8 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 8. 安装依赖
echo "8/8 安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ 基础环境配置完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 配置微博Cookie: nano crawler/config.json"
echo "2. 测试运行爬虫: source venv/bin/activate && python run.py"
echo "3. 配置systemd服务实现自动启动"
echo ""
