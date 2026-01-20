"""
添加automation-framework业务表到RuoYi数据库
"""
import asyncio
import aiomysql

DB_HOST = "106.53.217.96"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "gyswxgyb7418!"
DB_NAME = "ruoyi-fastapi"


async def add_automation_tables():
    """添加自动化框架业务表"""
    print("=" * 60)
    print("添加Automation Framework业务表")
    print("=" * 60)
    print(f"数据库: {DB_NAME}")
    print()
    
    try:
        # 连接数据库
        print("正在连接数据库...")
        conn = await aiomysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset='utf8mb4'
        )
        print("✅ 连接成功")
        
        async with conn.cursor() as cursor:
            # 读取automation-framework的SQL文件
            print("\n正在读取业务表SQL...")
            sql_file = "../automation-framework/database/schema_minimal.sql"
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()
            
            # 移除CREATE DATABASE语句，只保留CREATE TABLE
            lines = []
            skip_next = False
            for line in sql_content.split('\n'):
                if 'CREATE DATABASE' in line or 'USE ' in line:
                    skip_next = True
                    continue
                if skip_next and line.strip() == '':
                    skip_next = False
                    continue
                lines.append(line)
            
            sql_content = '\n'.join(lines)
            print("✅ SQL文件读取成功")
            
            # 执行SQL
            print("\n正在创建业务表...")
            statements = [s.strip() for s in sql_content.split(";") if s.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        await cursor.execute(statement)
                        print(f"  [{i}/{len(statements)}] ✅")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            print(f"  [{i}/{len(statements)}] ⚠️  表已存在")
                        else:
                            print(f"  [{i}/{len(statements)}] ❌ {str(e)[:80]}")
            
            await conn.commit()
            print("✅ 业务表创建完成")
            
            # 显示所有表
            print("\n当前数据库中的所有表:")
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            
            # 分类显示
            ruoyi_tables = []
            automation_tables = []
            
            for table in tables:
                table_name = table[0]
                if table_name.startswith('sys_') or table_name.startswith('gen_'):
                    ruoyi_tables.append(table_name)
                else:
                    automation_tables.append(table_name)
            
            print(f"\n📋 RuoYi系统表 ({len(ruoyi_tables)}个):")
            for t in ruoyi_tables[:5]:
                print(f"  - {t}")
            if len(ruoyi_tables) > 5:
                print(f"  ... 还有 {len(ruoyi_tables) - 5} 个")
            
            print(f"\n🤖 Automation业务表 ({len(automation_tables)}个):")
            for t in automation_tables:
                print(f"  - {t}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ 业务表添加完成！")
        print("=" * 60)
        print("\n现在数据库包含:")
        print(f"  - RuoYi系统表: {len(ruoyi_tables)}个")
        print(f"  - Automation业务表: {len(automation_tables)}个")
        print()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(add_automation_tables())
    if not success:
        exit(1)
