"""
初始化支付配置
插入三种支付方式的默认配置记录
"""
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('ruoyi-fastapi-backend/.env.dev')

def init_payment_configs():
    """初始化支付配置"""
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
        
        # 读取 SQL 文件
        with open('init_payment_configs.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割并执行每条 SQL 语句
        sql_statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for sql in sql_statements:
            if sql:
                try:
                    cursor.execute(sql)
                    print(f"✓ 执行成功")
                except Exception as e:
                    print(f"✗ 执行失败: {str(e)}")
        
        connection.commit()
        print("\n" + "="*60)
        print("✓ 支付配置初始化完成！")
        print("="*60)
        print("\n已插入三种支付方式的默认配置：")
        print("  1. 支付宝 (alipay) - 默认禁用")
        print("  2. 微信支付 (wechat) - 默认禁用")
        print("  3. Ping++ (pingpp) - 默认禁用")
        print("\n请使用管理员账号登录系统，在【支付配置】页面填写：")
        print("  - 商户ID")
        print("  - API密钥")
        print("  - 回调地址")
        print("  - 启用支付渠道")
        print("="*60)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    print("="*60)
    print("初始化支付配置")
    print("="*60)
    init_payment_configs()
