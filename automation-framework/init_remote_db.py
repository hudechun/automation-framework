"""
远程数据库初始化脚本
"""
import asyncio
import aiomysql
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "106.53.217.96")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "gyswxgyb7418!")
DB_NAME = os.getenv("DB_NAME", "automation_framework")


async def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("远程数据库初始化")
    print("=" * 60)
    print(f"主机: {DB_HOST}:{DB_PORT}")
    print(f"用户: {DB_USER}")
    print(f"数据库: {DB_NAME}")
    print()
    
    try:
        # 连接到MySQL服务器（不指定数据库）
        print("正在连接MySQL服务器...")
        conn = await aiomysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        
        print("✅ 连接成功")
        
        async with conn.cursor() as cursor:
            # 创建数据库（如果不存在）
            print(f"\n正在创建数据库 {DB_NAME}...")
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ 数据库创建成功")
            
            # 使用数据库
            await cursor.execute(f"USE {DB_NAME}")
            
            # 读取并执行SQL脚本
            print("\n正在读取SQL脚本...")
            with open("database/schema_minimal.sql", "r", encoding="utf-8") as f:
                sql_script = f.read()
            
            # 分割SQL语句并执行
            print("正在执行SQL语句...")
            statements = [s.strip() for s in sql_script.split(";") if s.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        await cursor.execute(statement)
                        print(f"  [{i}/{len(statements)}] ✅")
                    except Exception as e:
                        print(f"  [{i}/{len(statements)}] ⚠️  {str(e)[:50]}")
            
            await conn.commit()
            
            # 显示创建的表
            print("\n已创建的表:")
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            for table in tables:
                print(f"  - {table[0]}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)
        
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
