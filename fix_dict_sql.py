"""修复数据字典SQL文件的字段顺序"""
import re

# 读取文件
with open('RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_dicts.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复sys_dict_type的INSERT语句
# 原格式: NULL, 'thesis_package_type', '会员套餐类型', '0', ...
# 新格式: NULL, '会员套餐类型', 'thesis_package_type', '0', ...
def fix_dict_type(match):
    full_match = match.group(0)
    code = match.group(1)  # thesis_package_type
    name = match.group(2)  # 会员套餐类型
    rest = match.group(3)  # '0', 'admin', NOW(), ...
    
    return f"INSERT INTO sys_dict_type VALUES(\n    NULL, '{name}', '{code}', {rest});"

# 使用正则表达式替换
pattern = r"INSERT INTO sys_dict_type VALUES\(\s*NULL,\s*'([^']+)',\s*'([^']+)',\s*(.+?)\);"
content = re.sub(pattern, fix_dict_type, content, flags=re.DOTALL)

# 保存修复后的文件
with open('RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/thesis_dicts_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ SQL文件已修复')
print('   原文件: thesis_dicts.sql')
print('   新文件: thesis_dicts_fixed.sql')
print('\n修复内容:')
print('   - 交换了dict_name和dict_type的顺序')
print('   - 现在格式为: NULL, dict_name, dict_type, ...')
