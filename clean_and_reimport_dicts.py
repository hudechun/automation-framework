"""清理并重新导入数据字典"""
import pymysql

DB_CONFIG = {
    'host': '106.53.217.96',
    'port': 3306,
    'user': 'root',
    'password': 'gyswxgyb7418!',
    'database': 'ruoyi-fastapi',
    'charset': 'utf8mb4'
}

def clean_and_import():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("清理并重新导入数据字典")
        print("=" * 60)
        
        # 步骤1：完全删除thesis相关字典
        print("\n【步骤1】完全删除thesis字典...")
        
        # 先删除字典数据
        cursor.execute("""
            DELETE FROM sys_dict_data 
            WHERE dict_type IN (
                SELECT dict_type FROM sys_dict_type WHERE dict_type LIKE 'thesis_%'
            )
        """)
        deleted_data = cursor.rowcount
        print(f"   - 删除字典数据: {deleted_data} 条")
        
        # 再删除字典类型
        cursor.execute("DELETE FROM sys_dict_type WHERE dict_type LIKE 'thesis_%'")
        deleted_types = cursor.rowcount
        print(f"   - 删除字典类型: {deleted_types} 条")
        
        conn.commit()
        print("   ✅ 清理完成")
        
        # 步骤2：读取修复后的SQL文件
        print("\n【步骤2】读取SQL文件...")
        with open('RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_dicts_fixed.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print("   ✅ 文件读取成功")
        
        # 步骤3：解析SQL语句
        print("\n【步骤3】解析SQL语句...")
        statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # 如果行以分号结尾，表示一条SQL语句结束
            if line.endswith(';'):
                statement = ' '.join(current_statement)
                statements.append(statement)
                current_statement = []
        
        print(f"   ✅ 解析完成，共 {len(statements)} 条SQL语句")
        
        # 步骤4：执行SQL语句
        print("\n【步骤4】执行SQL语句...")
        success_count = 0
        error_count = 0
        
        for statement in statements:
            try:
                cursor.execute(statement)
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"   ❌ 执行失败: {str(e)[:100]}")
        
        conn.commit()
        
        print(f"\n【步骤5】导入完成:")
        print(f"   - 成功: {success_count} 条")
        print(f"   - 失败: {error_count} 条")
        
        # 步骤6：验证导入结果
        print("\n【步骤6】验证导入结果...")
        
        # 字典类型数量
        cursor.execute("SELECT COUNT(*) FROM sys_dict_type WHERE dict_type LIKE 'thesis_%'")
        dict_types = cursor.fetchone()[0]
        
        # 字典数据数量
        cursor.execute("""
            SELECT COUNT(*) FROM sys_dict_data 
            WHERE dict_type IN (
                SELECT dict_type FROM sys_dict_type WHERE dict_type LIKE 'thesis_%'
            )
        """)
        dict_data = cursor.fetchone()[0]
        
        # 各类型详细统计
        cursor.execute("""
            SELECT dt.dict_name, COUNT(dd.dict_code) as count
            FROM sys_dict_type dt
            LEFT JOIN sys_dict_data dd ON dt.dict_type = dd.dict_type
            WHERE dt.dict_type LIKE 'thesis_%'
            GROUP BY dt.dict_type
            ORDER BY dt.dict_type
        """)
        
        print(f"\n📊 验证结果:")
        print(f"   - 字典类型: {dict_types} (预期: 11)")
        print(f"   - 字典数据: {dict_data} (预期: 44)")
        
        print(f"\n   各类型数据量:")
        for row in cursor.fetchall():
            print(f"      {row[0]:20s}: {row[1]:2d} 条")
        
        # 检查重复
        cursor.execute("""
            SELECT dict_type, dict_label, COUNT(*) as count
            FROM sys_dict_data
            WHERE dict_type LIKE 'thesis_%'
            GROUP BY dict_type, dict_label
            HAVING count > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"\n   ⚠️ 发现 {len(duplicates)} 个重复项")
        else:
            print(f"\n   ✅ 没有重复数据")
        
        if dict_types == 11 and dict_data == 44 and not duplicates:
            print("\n🎉 数据字典导入成功！")
        else:
            print("\n⚠️ 数据字典可能不完整，请检查")
        
    except Exception as e:
        print(f"\n❌ 操作失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    clean_and_import()
