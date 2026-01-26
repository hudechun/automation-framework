"""
重新导入AI论文写作系统菜单
"""
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('ruoyi-fastapi-backend/.env.dev')

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'ry-vue'),
    'charset': 'utf8mb4'
}

def reimport_menus():
    """重新导入菜单"""
    try:
        # 连接数据库
        print("正在连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. 删除旧菜单（如果存在）
        print("\n1. 删除旧菜单...")
        cursor.execute("DELETE FROM sys_menu WHERE menu_id >= 5000 AND menu_id < 6000")
        deleted_count = cursor.rowcount
        print(f"   删除了 {deleted_count} 条旧菜单记录")
        
        # 2. 读取并执行SQL文件
        print("\n2. 导入新菜单...")
        sql_file = 'ruoyi-fastapi-backend/sql/thesis_menus.sql'
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句（按分号分割，忽略注释）
        sql_statements = []
        for statement in sql_content.split(';'):
            statement = statement.strip()
            # 跳过空语句和注释
            if statement and not statement.startswith('--'):
                sql_statements.append(statement)
        
        # 执行每条SQL语句
        success_count = 0
        for sql in sql_statements:
            if sql.strip():
                try:
                    cursor.execute(sql)
                    success_count += 1
                except Exception as e:
                    print(f"   警告: SQL执行失败: {str(e)[:100]}")
        
        print(f"   成功执行 {success_count} 条SQL语句")
        
        # 3. 提交事务
        conn.commit()
        print("\n3. 提交事务成功")
        
        # 4. 验证导入结果
        print("\n4. 验证导入结果...")
        cursor.execute("""
            SELECT menu_id, menu_name, component 
            FROM sys_menu 
            WHERE menu_id >= 5000 AND menu_id < 6000
            ORDER BY menu_id
        """)
        
        menus = cursor.fetchall()
        print(f"\n   共导入 {len(menus)} 个菜单项:")
        print("   " + "-" * 80)
        print(f"   {'ID':<8} {'菜单名称':<20} {'组件路径':<40}")
        print("   " + "-" * 80)
        
        for menu in menus[:10]:  # 只显示前10个
            menu_id, menu_name, component = menu
            component = component or '(无)'
            print(f"   {menu_id:<8} {menu_name:<20} {component:<40}")
        
        if len(menus) > 10:
            print(f"   ... 还有 {len(menus) - 10} 个菜单项")
        
        print("\n✅ 菜单导入完成！")
        print("\n📝 下一步操作:")
        print("   1. 重新登录系统")
        print("   2. 菜单会自动刷新")
        print("   3. 点击菜单验证组件是否正常加载")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 80)
    print("AI论文写作系统 - 菜单重新导入工具")
    print("=" * 80)
    reimport_menus()
