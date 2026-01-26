"""
快速添加AI模型配置菜单
"""
import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',  # 请修改为实际密码
    'database': 'ry-vue',
    'charset': 'utf8mb4'
}


def main():
    """主函数"""
    print("\n" + "="*60)
    print("添加AI模型配置菜单")
    print("="*60)
    
    # 获取密码
    if len(sys.argv) > 1:
        DB_CONFIG['password'] = sys.argv[1]
    else:
        import getpass
        password = getpass.getpass("\n请输入MySQL root密码: ")
        if password:
            DB_CONFIG['password'] = password
    
    try:
        # 连接数据库
        print("\n正在连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 检查论文系统菜单是否存在
        print("\n正在检查论文系统菜单...")
        cursor.execute("SELECT menu_id FROM sys_menu WHERE menu_id = 5000")
        if not cursor.fetchone():
            print("❌ 错误: 论文系统菜单(menu_id=5000)不存在")
            print("   请先执行 thesis_menus.sql 创建论文系统菜单")
            sys.exit(1)
        print("✅ 论文系统菜单存在")
        
        # 删除旧菜单（如果存在）
        print("\n正在删除旧菜单（如果存在）...")
        cursor.execute("DELETE FROM sys_menu WHERE menu_id >= 5600 AND menu_id < 5700")
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            print(f"✅ 删除了 {deleted_count} 个旧菜单")
        else:
            print("✅ 没有旧菜单需要删除")
        
        # 插入AI模型配置主菜单
        print("\n正在创建AI模型配置菜单...")
        cursor.execute("""
            INSERT INTO sys_menu VALUES(
                5600, 'AI模型配置', 5000, 6, 'ai-model', 'thesis/ai-model/index', '', '', 1, 0, 'C', '0', '0', 
                'thesis:ai-model:list', 'cpu', 'admin', NOW(), '', NULL, 'AI模型配置管理'
            )
        """)
        print("✅ 主菜单创建成功")
        
        # 插入按钮权限
        print("\n正在创建按钮权限...")
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
            print(f"  ✅ {menu_name}")
        
        # 提交事务
        conn.commit()
        print("\n✅ 所有菜单创建成功！")
        
        # 验证菜单
        print("\n正在验证菜单...")
        cursor.execute("""
            SELECT menu_id, menu_name, parent_id, order_num, perms 
            FROM sys_menu 
            WHERE menu_id >= 5600 AND menu_id < 5700
            ORDER BY menu_id
        """)
        
        results = cursor.fetchall()
        print(f"\n创建了 {len(results)} 个菜单项:")
        print("-" * 80)
        print(f"{'ID':<8} {'名称':<20} {'父ID':<8} {'排序':<8} {'权限':<30}")
        print("-" * 80)
        for row in results:
            menu_id, menu_name, parent_id, order_num, perms = row
            print(f"{menu_id:<8} {menu_name:<20} {parent_id or '-':<8} {order_num:<8} {perms or '-':<30}")
        
        print("\n" + "="*60)
        print("🎉 菜单添加完成！")
        print("="*60)
        print("\n后续步骤:")
        print("1. 重启后端服务")
        print("2. 刷新前端页面（清除缓存）")
        print("3. 登录系统，进入 'AI论文写作' -> 'AI模型配置'")
        
    except pymysql.Error as e:
        print(f"\n❌ 数据库错误: {e}")
        conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
