"""验证AI论文写作系统数据库安装"""
import pymysql
from typing import List, Dict

# 数据库配置
DB_CONFIG = {
    'host': '106.53.217.96',
    'port': 3306,
    'user': 'root',
    'password': 'gyswxgyb7418!',
    'database': 'ruoyi-fastapi',
    'charset': 'utf8mb4'
}

def check_tables() -> Dict[str, bool]:
    """检查数据库表是否存在"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 需要检查的表（使用实际的表名）
    tables = [
        # 会员相关表
        'ai_write_member_package',
        'ai_write_user_membership',
        'ai_write_user_feature_quota',
        'ai_write_quota_record',
        # 论文相关表
        'ai_write_thesis',
        'ai_write_thesis_outline',
        'ai_write_thesis_chapter',
        'ai_write_thesis_version',
        # 模板相关表
        'ai_write_format_template',
        'ai_write_template_format_rule',
        # 订单相关表
        'ai_write_order',
        'ai_write_feature_service',
        'ai_write_export_record',
        # 支付相关表
        'ai_write_payment_config',
        'ai_write_payment_transaction'
    ]
    
    results = {}
    for table in tables:
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        results[table] = cursor.fetchone() is not None
    
    cursor.close()
    conn.close()
    return results

def check_menus() -> Dict[str, int]:
    """检查菜单是否创建"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 检查AI论文写作菜单
    cursor.execute("SELECT COUNT(*) FROM sys_menu WHERE menu_id >= 5000 AND menu_id < 6000")
    menu_count = cursor.fetchone()[0]
    
    # 检查一级菜单
    cursor.execute("SELECT COUNT(*) FROM sys_menu WHERE menu_id = 5000")
    root_menu = cursor.fetchone()[0]
    
    # 检查二级菜单
    cursor.execute("SELECT COUNT(*) FROM sys_menu WHERE parent_id = 5000 AND menu_type = 'C'")
    sub_menus = cursor.fetchone()[0]
    
    # 检查按钮权限
    cursor.execute("SELECT COUNT(*) FROM sys_menu WHERE parent_id >= 5100 AND parent_id < 5600 AND menu_type = 'F'")
    buttons = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return {
        'total': menu_count,
        'root': root_menu,
        'sub_menus': sub_menus,
        'buttons': buttons
    }

def check_dicts() -> Dict[str, int]:
    """检查数据字典是否创建"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 检查字典类型
    cursor.execute("SELECT COUNT(*) FROM sys_dict_type WHERE dict_type LIKE 'thesis_%'")
    dict_types = cursor.fetchone()[0]
    
    # 检查字典数据
    cursor.execute("""
        SELECT COUNT(*) FROM sys_dict_data 
        WHERE dict_type IN (
            SELECT dict_type FROM sys_dict_type WHERE dict_type LIKE 'thesis_%'
        )
    """)
    dict_data = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return {
        'types': dict_types,
        'data': dict_data
    }

def main():
    print("=" * 60)
    print("AI论文写作系统 - 数据库验证")
    print("=" * 60)
    
    # 1. 检查数据库表
    print("\n【1】检查数据库表...")
    tables = check_tables()
    success_count = sum(1 for v in tables.values() if v)
    total_count = len(tables)
    
    print(f"✅ 数据库表: {success_count}/{total_count} 创建成功")
    
    if success_count < total_count:
        print("\n❌ 缺失的表:")
        for table, exists in tables.items():
            if not exists:
                print(f"   - {table}")
    else:
        print("   所有表创建成功！")
    
    # 2. 检查菜单
    print("\n【2】检查菜单配置...")
    menus = check_menus()
    print(f"✅ 菜单总数: {menus['total']}")
    print(f"   - 一级菜单: {menus['root']} (预期: 1)")
    print(f"   - 二级菜单: {menus['sub_menus']} (预期: 5)")
    print(f"   - 按钮权限: {menus['buttons']} (预期: 35)")
    
    if menus['root'] == 1 and menus['sub_menus'] == 5:
        print("   菜单配置正确！")
    else:
        print("   ⚠️ 菜单配置可能不完整")
    
    # 3. 检查数据字典
    print("\n【3】检查数据字典...")
    dicts = check_dicts()
    print(f"✅ 字典类型: {dicts['types']} (预期: 11)")
    print(f"✅ 字典数据: {dicts['data']} (预期: 50+)")
    
    if dicts['types'] == 11:
        print("   数据字典配置正确！")
    else:
        print("   ⚠️ 数据字典配置可能不完整")
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    all_success = (
        success_count == total_count and
        menus['root'] == 1 and
        menus['sub_menus'] == 5 and
        dicts['types'] == 11
    )
    
    if all_success:
        print("🎉 所有检查通过！系统安装成功！")
        print("\n下一步:")
        print("1. 重启后端服务")
        print("2. 访问 http://localhost:9099/docs 查看API文档")
        print("3. 登录系统查看【AI论文写作】菜单")
    else:
        print("⚠️ 部分检查未通过，请检查SQL脚本执行情况")
    
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        print("请检查数据库连接配置")
