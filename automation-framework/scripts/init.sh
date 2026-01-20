#!/bin/bash

# 初始化数据库和配置
echo "Initializing Automation Framework..."

# 等待MySQL启动
echo "Waiting for MySQL to be ready..."
sleep 10

# 运行数据库迁移
docker-compose exec app aerich init -t src.models.database.TORTOISE_ORM
docker-compose exec app aerich init-db

# 创建默认管理员用户
echo "Creating default admin user..."
# TODO: 添加创建管理员用户的命令

echo "Initialization complete!"
