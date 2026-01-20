#!/bin/bash

# Linux/macOS数据库初始化脚本

echo "============================================"
echo "数据库初始化脚本"
echo "============================================"
echo

# 设置变量
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-3306}
DB_USER=${DB_USER:-root}
DB_NAME=${DB_NAME:-automation_framework}

# 提示输入密码
read -sp "请输入MySQL root密码: " DB_PASSWORD
echo
echo

echo "正在连接MySQL..."
echo

# 检查MySQL是否可用
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ 错误: 无法连接到MySQL服务器"
    echo "请检查:"
    echo "1. MySQL服务是否已启动"
    echo "2. 用户名和密码是否正确"
    echo "3. 主机和端口是否正确"
    exit 1
fi

echo "✅ MySQL连接成功"
echo

# 选择SQL脚本
echo "请选择要执行的SQL脚本:"
echo "1. 完整版 (schema.sql) - 包含所有表和视图"
echo "2. 最小版 (schema_minimal.sql) - 仅核心表"
echo
read -p "请输入选择 (1 或 2): " CHOICE

if [ "$CHOICE" = "1" ]; then
    SQL_FILE="schema.sql"
    echo
    echo "将执行完整版SQL脚本..."
elif [ "$CHOICE" = "2" ]; then
    SQL_FILE="schema_minimal.sql"
    echo
    echo "将执行最小版SQL脚本..."
else
    echo "❌ 无效的选择"
    exit 1
fi

echo
echo "正在执行SQL脚本: $SQL_FILE"
echo

# 执行SQL脚本
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" < "$SQL_FILE"

if [ $? -ne 0 ]; then
    echo
    echo "❌ SQL脚本执行失败"
    exit 1
fi

echo
echo "============================================"
echo "✅ 数据库初始化完成！"
echo "============================================"
echo
echo "数据库名称: $DB_NAME"
echo

# 显示创建的表
echo "已创建的表:"
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "USE $DB_NAME; SHOW TABLES;"

echo
echo "下一步:"
echo "1. 配置 .env 文件中的数据库连接信息"
echo "2. 运行 bash scripts/start.sh 启动服务"
echo
