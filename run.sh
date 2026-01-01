#!/bin/bash

echo "======================================"
echo "微博归档系统"
echo "======================================"
echo ""
echo "请选择操作:"
echo "1. 运行爬虫 (抓取微博)"
echo "2. 生成网站 (构建静态页面)"
echo "3. 启动预览 (本地查看网站)"
echo "4. 完整流程 (爬虫 + 生成 + 预览)"
echo "5. 退出"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "[1/1] 运行爬虫..."
        cd crawler
        python3 weibo_spider.py
        cd ..
        echo ""
        echo "爬虫完成！"
        ;;
    2)
        echo ""
        echo "[1/1] 生成网站..."
        cd generator
        python3 build.py
        cd ..
        echo ""
        echo "网站生成完成！"
        ;;
    3)
        echo ""
        echo "[1/1] 启动预览服务器..."
        echo "浏览器访问: http://localhost:8000"
        echo "按 Ctrl+C 停止服务器"
        cd site
        python3 -m http.server 8000
        cd ..
        ;;
    4)
        echo ""
        echo "[1/3] 运行爬虫..."
        cd crawler
        python3 weibo_spider.py
        cd ..

        echo ""
        echo "[2/3] 生成网站..."
        cd generator
        python3 build.py
        cd ..

        echo ""
        echo "[3/3] 启动预览服务器..."
        echo "浏览器访问: http://localhost:8000"
        echo "按 Ctrl+C 停止服务器"
        cd site
        python3 -m http.server 8000
        cd ..
        ;;
    5)
        echo "退出程序。"
        exit 0
        ;;
    *)
        echo "无效选项！"
        exit 1
        ;;
esac
