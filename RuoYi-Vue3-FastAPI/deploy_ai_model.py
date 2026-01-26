"""
AI模型配置功能快速部署脚本
"""
import pymysql
import sys
import os
from pathlib import Path

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',  # 请修改为实际密码
    'database': 'ry-vue',
    'charset': 'utf8mb4'
}


def print_step(step, message):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step}: {message}")
    print('='*60)


def execute_sql_file(cursor, file_path):
    """执行SQL文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # 分割SQL语句（按分号分割，但要注意存储过程等特殊情况）
        sql_commands = []
        current_command = []
        in_delimiter = False
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('--') or line.startswith('#'):
                continue
            
            # 处理DELIMITER
            if line.upper().startswith('DELIMITER'):
                in_delimiter = not in_delimiter
                continue
            
            current_command.append(line)
            
            # 如果不在DELIMITER块中，遇到分号就是一条完整语句
            if not in_delimiter and line.endswith(';'):
                sql_commands.append(' '.join(current_command))
                current_command = []
        
        # 执行所有SQL命令
        success_count = 0
        for command in sql_commands:
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    success_count += 1
                except Exception as e:
                    print(f"⚠️  警告: 执行SQL时出错: {str(e)[:100]}")
                    print(f"   SQL: {command[:100]}...")
        
        return success_count
    except Exception as e:
        print(f"❌ 错误: 读取或执行SQL文件失败: {e}")
        return 0


def check_table_exists(cursor, table_name):
    """检查表是否存在"""
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None


def check_menu_exists(cursor, menu_name):
    """检查菜单是否存在"""
    cursor.execute(f"SELECT COUNT(*) FROM sys_menu WHERE menu_name = '{menu_name}'")
    result = cursor.fetchone()
    return result[0] > 0


def main():
    """主函数"""
    print("\n" + "="*60)
    print("AI模型配置功能部署脚本")
    print("="*60)
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    backend_dir = script_dir / 'ruoyi-fastapi-backend'
    
    # 检查SQL文件是否存在
    schema_sql = backend_dir / 'sql' / 'ai_model_schema.sql'
    menu_sql = backend_dir / 'sql' / 'ai_model_menu.sql'
    
    if not schema_sql.exists():
        print(f"❌ 错误: 找不到文件 {schema_sql}")
        sys.exit(1)
    
    if not menu_sql.exists():
        print(f"❌ 错误: 找不到文件 {menu_sql}")
        sys.exit(1)
    
    print(f"\n✅ SQL文件检查通过")
    print(f"   - 表结构文件: {schema_sql}")
    print(f"   - 菜单文件: {menu_sql}")
    
    # 连接数据库
    print_step(1, "连接数据库")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print(f"✅ 数据库连接成功: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
    except Exception as e:
        print(f"❌ 错误: 数据库连接失败: {e}")
        print("\n请检查:")
        print("1. MySQL服务是否启动")
        print("2. 数据库配置是否正确（host, user, password, database）")
        print("3. 数据库用户是否有足够的权限")
        sys.exit(1)
    
    try:
        # 检查表是否已存在
        print_step(2, "检查数据库表")
        table_exists = check_table_exists(cursor, 'ai_write_ai_model_config')
        
        if table_exists:
            print("⚠️  表 'ai_write_ai_model_config' 已存在")
            response = input("是否要重新创建表？这将删除现有数据 (y/N): ")
            if response.lower() != 'y':
                print("跳过表创建")
            else:
                print("正在删除旧表...")
                cursor.execute("DROP TABLE IF EXISTS ai_write_ai_model_config")
                table_exists = False
        
        if not table_exists:
            print("正在创建表结构...")
            count = execute_sql_file(cursor, schema_sql)
            print(f"✅ 表结构创建成功，执行了 {count} 条SQL语句")
        
        # 检查菜单是否已存在
        print_step(3, "检查菜单配置")
        menu_exists = check_menu_exists(cursor, 'AI模型配置')
        
        if menu_exists:
            print("⚠️  菜单 'AI模型配置' 已存在")
            response = input("是否要重新创建菜单？这将删除现有菜单 (y/N): ")
            if response.lower() != 'y':
                print("跳过菜单创建")
            else:
                print("正在删除旧菜单...")
                cursor.execute("DELETE FROM sys_menu WHERE menu_name = 'AI模型配置'")
                cursor.execute("DELETE FROM sys_menu WHERE parent_id = (SELECT menu_id FROM sys_menu WHERE menu_name = 'AI模型配置')")
                menu_exists = False
        
        if not menu_exists:
            print("正在创建菜单...")
            
            # 先检查论文系统菜单是否存在
            cursor.execute("SELECT menu_id FROM sys_menu WHERE menu_id = 5000")
            if not cursor.fetchone():
                print("❌ 错误: 论文系统菜单(menu_id=5000)不存在")
                print("   请先执行 thesis_menus.sql 创建论文系统菜单")
                sys.exit(1)
            
            # 使用固定的menu_id插入菜单
            print("正在插入AI模型配置主菜单...")
            cursor.execute("""
                INSERT INTO sys_menu VALUES(
                    5600, 'AI模型配置', 5000, 6, 'ai-model', 'thesis/ai-model/index', '', '', 1, 0, 'C', '0', '0', 
                    'thesis:ai-model:list', 'cpu', 'admin', NOW(), '', NULL, 'AI模型配置管理'
                )
            """)
            
            print("正在插入按钮权限...")
            buttons = [
                (5601, '查询AI模型', 'thesis:ai-model:query'),
                (5602, '新增AI模型', 'thesis:ai-model:add'),
                (5603, '修改AI模型', 'thesis:ai-model:edit'),
                (5604, '删除AI模型', 'thesis:ai-model:remove'),
                (5605, '测试连接', 'thesis:ai-model:test'),
            ]
            
            for menu_id, menu_name, perms in buttons:
                cursor.execute(f"""
                    INSERT INTO sys_menu VALUES(
                        {menu_id}, '{menu_name}', 5600, {menu_id-5600}, '#', '', '', '', 1, 0, 'F', '0', '0', 
                        '{perms}', '#', 'admin', NOW(), '', NULL, ''
                    )
                """)
            
            print(f"✅ 菜单创建成功，创建了 6 个菜单项")
        
        # 提交事务
        print_step(4, "提交更改")
        conn.commit()
        print("✅ 所有更改已提交到数据库")
        
        # 验证部署
        print_step(5, "验证部署")
        
        # 检查表
        if check_table_exists(cursor, 'ai_write_ai_model_config'):
            cursor.execute("SELECT COUNT(*) FROM ai_write_ai_model_config")
            count = cursor.fetchone()[0]
            print(f"✅ 表 'ai_write_ai_model_config' 存在，包含 {count} 条预设模型")
        else:
            print("❌ 表 'ai_write_ai_model_config' 不存在")
        
        # 检查菜单
        if check_menu_exists(cursor, 'AI模型配置'):
            cursor.execute("SELECT COUNT(*) FROM sys_menu WHERE menu_name LIKE '%AI模型%'")
            count = cursor.fetchone()[0]
            print(f"✅ 菜单 'AI模型配置' 存在，包含 {count} 个菜单项")
        else:
            print("❌ 菜单 'AI模型配置' 不存在")
        
        # 部署完成
        print("\n" + "="*60)
        print("🎉 部署完成！")
        print("="*60)
        print("\n后续步骤:")
        print("1. 重启后端服务: python app.py")
        print("2. 刷新前端页面（清除缓存）")
        print("3. 登录系统，进入 '论文系统' -> 'AI模型配置'")
        print("4. 配置API Key并测试连接")
        print("\n详细文档: .kiro/specs/ai-thesis-writing/AI_MODEL_DEPLOYMENT_GUIDE.md")
        
    except Exception as e:
        print(f"\n❌ 错误: 部署失败: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    # 检查是否提供了数据库密码
    if len(sys.argv) > 1:
        DB_CONFIG['password'] = sys.argv[1]
    else:
        print("\n提示: 可以通过命令行参数提供数据库密码")
        print("用法: python deploy_ai_model.py <数据库密码>")
        print("\n或者直接修改脚本中的 DB_CONFIG['password']")
        
        # 提示用户输入密码
        import getpass
        password = getpass.getpass("\n请输入MySQL root密码: ")
        if password:
            DB_CONFIG['password'] = password
    
    main()
