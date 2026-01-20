#!/bin/bash

# 启动所有服务
echo "Starting Automation Framework..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# 创建必要的目录
mkdir -p storage/screenshots storage/logs storage/videos storage/exports
mkdir -p logs
mkdir -p nginx/ssl

# 启动服务
docker-compose up -d

echo "Services started successfully!"
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "Admin: http://localhost:8000/admin"

# 显示服务状态
docker-compose ps
