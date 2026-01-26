"""
清理重复的支付配置记录
"""
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('ruoyi-fastapi-backend/.env.dev')

def clean_duplicates():
    """清理重复记录"""
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'ry-vue'),
            charset='utf8mb4'
        )
        
        print(f"✓ 已连接到数据库: {os.getenv('MYSQL_DATABASE')}")
        
        cursor = connection.cursor()
        
        # 查看重复记录
        print("\n检查重复记录...")
        cursor.execute("""
            SELECT provider_type, COUNT(*) as count 
            FROM ai_write_payment_config 
            WHERE del_flag = '0'
            GROUP BY provider_type 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print("发现重复记录：")
            for row in duplicates:
                print(f"  - {row[0]}: {row[1]} 条记录")
        else:
            print("✓ 没有发现重复记录")
            cursor.close()
            connection.close()
            return True
        
        # 清理重复记录
        print("\n开始清理重复记录...")
        
        for provider_type in ['alipay', 'wechat', 'pingpp']:
            cursor.execute(f"""
                DELETE FROM ai_write_payment_config 
                WHERE provider_type = '{provider_type}' 
                AND config_id NOT IN (
                    SELECT * FROM (
                        SELECT MIN(config_id) 
                        FROM ai_write_payment_config 
                        WHERE provider_type = '{provider_type}' AND del_flag = '0'
                    ) AS temp
                )
            """)
            deleted = cursor.rowcount
            if deleted > 0:
                print(f"✓ 删除了 {deleted} 条 {provider_type} 的重复记录")
        
        connection.commit()
        
        # 验证清理结果
        print("\n验证清理结果...")
        cursor.execute("""
            SELECT config_id, provider_type, provider_name, is_enabled, create_time 
            FROM ai_write_payment_config 
            WHERE del_flag = '0'
            ORDER BY provider_type
        """)
        results = cursor.fetchall()
        
        print("\n当前支付配置：")
        for row in results:
            enabled = "启用" if row[3] == '1' else "禁用"
            print(f"  ID: {row[0]}, 类型: {row[1]}, 名称: {row[2]}, 状态: {enabled}")
        
        print("\n" + "="*60)
        print("✓ 清理完成！")
        print("="*60)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    print("="*60)
    print("清理重复的支付配置记录")
    print("="*60)
    clean_duplicates()
