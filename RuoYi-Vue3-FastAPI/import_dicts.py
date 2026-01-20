#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导入字典数据到数据库"""

import pymysql

def import_dicts():
    """导入字典数据"""
    try:
        # 连接数据库
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='mysqlroot',
            database='ruoyi-fastapi',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        print("正在读取 SQL 文件...")
        with open('add_automation_dicts.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割 SQL 语句
        statements = []
        current = []
        for line in sql_content.split('\n'):
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('--') or line.startswith('USE'):
                continue
            current.append(line)
            if line.endswith(';'):
                statements.append(' '.join(current))
                current = []
        
        print(f"共 {len(statements)} 条 SQL 语句")
        
        # 执行 SQL 语句
        success = 0
        for i, stmt in enumerate(statements, 1):
            try:
                cursor.execute(stmt)
                success += 1
                print(f"[{i}/{len(statements)}] 执行成功")
            except Exception as e:
                print(f"[{i}/{len(statements)}] 执行失败: {e}")
        
        conn.commit()
        print(f"\n导入完成！成功 {success}/{len(statements)} 条")
        
        # 验证导入结果
        cursor.execute("SELECT dict_type, COUNT(*) as cnt FROM sys_dict_data WHERE dict_type LIKE 'automation_%' GROUP BY dict_type")
        results = cursor.fetchall()
        print("\n字典数据统计:")
        for row in results:
            print(f"  {row[0]}: {row[1]} 条")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        return False
    
    return True

if __name__ == '__main__':
    import_dicts()
