"""单独导入数据字典"""
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': '106.53.217.96',
    'port': 3306,
    'user': 'root',
    'password': 'gyswxgyb7418!',
    'database': 'ruoyi-fastapi',
    'charset': 'utf8mb4'
}

def import_dicts():
    """导入数据字典"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 步骤1：删除已有的thesis相关字典
        print("\n【步骤1】清理已有的thesis字典...")
        
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
        
        # 步骤2：读取SQL文件
        print("\n【步骤2】读取SQL文件...")
        with open('RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_dicts_fixed.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print("   ✅ 文件读取成功")
        
        # 步骤3：分割SQL语句
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
                print(f"❌ 执行失败: {str(e)[:100]}")
        
        conn.commit()
        
        print(f"\n【步骤5】导入完成:")
        print(f"   - 成功: {success_count} 条")
        print(f"   - 失败: {error_count} 条")
        
        # 步骤6：验证导入结果
        print("\n【步骤6】验证导入结果...")
        cursor.execute("SELECT COUNT(*) FROM sys_dict_type WHERE dict_type LIKE 'thesis_%'")
        dict_types = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM sys_dict_data 
            WHERE dict_type IN (
                SELECT dict_type FROM sys_dict_type WHERE dict_type LIKE 'thesis_%'
            )
        """)
        dict_data = cursor.fetchone()[0]
        
        print(f"\n📊 验证结果:")
        print(f"   - 字典类型: {dict_types} (预期: 11)")
        print(f"   - 字典数据: {dict_data} (预期: 50+)")
        
        if dict_types == 11 and dict_data >= 50:
            print("\n🎉 数据字典导入成功！")
        else:
            print("\n⚠️ 数据字典可能不完整，请检查")
        
    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("导入AI论文写作系统数据字典")
    print("=" * 60)
    import_dicts()
