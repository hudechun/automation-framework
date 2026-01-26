"""
扩展AI模型配置表字段
"""
import pymysql
from pathlib import Path

def extend_ai_model_table():
    """扩展AI模型配置表"""
    print("=" * 60)
    print("扩展AI模型配置表字段")
    print("=" * 60)
    
    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'ry-vue',
        'charset': 'utf8mb4'
    }
    
    try:
        # 连接数据库
        print("\n[1/3] 连接数据库...")
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 读取SQL文件
        print("\n[2/3] 读取SQL文件...")
        sql_file = Path(__file__).parent / 'ruoyi-fastapi-backend' / 'sql' / 'extend_ai_model_fields.sql'
        
        if not sql_file.exists():
            print(f"❌ SQL文件不存在: {sql_file}")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("✅ SQL文件读取成功")
        
        # 执行SQL语句
        print("\n[3/3] 执行SQL语句...")
        
        # 分割SQL语句（按分号分割，忽略注释）
        statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            line = line.strip()
            # 跳过空行和注释
            if not line or line.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # 如果行以分号结尾，表示一条完整的SQL语句
            if line.endswith(';'):
                statement = ' '.join(current_statement)
                statements.append(statement)
                current_statement = []
        
        # 执行每条SQL语句
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                conn.commit()
                print(f"  ✅ 执行第 {i}/{len(statements)} 条语句成功")
            except pymysql.err.OperationalError as e:
                if 'Duplicate column name' in str(e):
                    print(f"  ⚠️  第 {i}/{len(statements)} 条语句: 字段已存在，跳过")
                else:
                    print(f"  ❌ 第 {i}/{len(statements)} 条语句执行失败: {e}")
            except Exception as e:
                print(f"  ❌ 第 {i}/{len(statements)} 条语句执行失败: {e}")
        
        print("\n" + "=" * 60)
        print("✅ AI模型配置表扩展完成！")
        print("=" * 60)
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 扩展失败: {e}")
        return False


if __name__ == '__main__':
    extend_ai_model_table()
    input("\n按回车键退出...")
