"""
初始化RuoYi数据库
"""
import asyncio
import os
import sys
import aiomysql
from dotenv import load_dotenv

# 加载环境变量
env_file = "ruoyi-fastapi-backend/.env.dev"
if len(sys.argv) > 1 and sys.argv[1] == "prod":
    env_file = "ruoyi-fastapi-backend/.env.prod"

load_dotenv(env_file)

# 从环境变量读取数据库配置
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USERNAME", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_DATABASE", "ruoyi-fastapi")

# 验证必需的环境变量
if not DB_PASSWORD:
    print("❌ 错误: 未设置数据库密码 (DB_PASSWORD)")
    print(f"请在 {env_file} 文件中配置 DB_PASSWORD")
    sys.exit(1)


async def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("RuoYi数据库初始化")
    print("=" * 60)
    print(f"主机: {DB_HOST}:{DB_PORT}")
    print(f"数据库: {DB_NAME}")
    print()
    
    try:
        # 连接MySQL
        print("正在连接MySQL...")
        conn = await aiomysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        print("✅ 连接成功")
        
        async with conn.cursor() as cursor:
            # 创建数据库
            print(f"\n正在创建数据库 {DB_NAME}...")
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ 数据库创建成功")
            
            # 使用数据库
            await cursor.execute(f"USE `{DB_NAME}`")
            
            # 读取SQL文件
            print("\n正在读取SQL文件...")
            sql_file = "ruoyi-fastapi-backend/sql/ruoyi-fastapi.sql"
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()
            print("✅ SQL文件读取成功")
            
            # 分割并执行SQL语句
            print("\n正在执行SQL语句...")
            statements = [s.strip() for s in sql_content.split(";") if s.strip()]
            total = len(statements)
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        await cursor.execute(statement)
                        if i % 10 == 0 or i == total:
                            print(f"  进度: {i}/{total}")
                    except Exception as e:
                        # 忽略一些常见的警告
                        if "already exists" not in str(e).lower():
                            print(f"  警告 [{i}]: {str(e)[:100]}")
            
            await conn.commit()
            print("✅ SQL执行完成")
            
            # 显示创建的表
            print("\n已创建的表:")
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            for table in tables[:10]:  # 只显示前10个
                print(f"  - {table[0]}")
            if len(tables) > 10:
                print(f"  ... 还有 {len(tables) - 10} 个表")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)
        print("\n默认管理员账号:")
        print("  用户名: admin")
        print("  密码: admin123")
        print()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(init_database())
    if not success:
        exit(1)
