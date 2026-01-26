"""
更新现有AI模型记录的model_type字段
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent / 'ruoyi-fastapi-backend'
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from config.database import get_db


async def update_model_type():
    """更新现有AI模型记录的model_type字段"""
    print("=" * 60)
    print("更新AI模型记录的model_type字段")
    print("=" * 60)
    
    async for db in get_db():
        try:
            # 1. 更新model_type字段
            print("\n1. 更新model_type字段...")
            result = await db.execute(text("""
                UPDATE ai_write_ai_model_config 
                SET model_type = 'language' 
                WHERE model_type IS NULL OR model_type = ''
            """))
            await db.commit()
            print(f"   ✅ 已更新 {result.rowcount} 条记录的model_type字段")
            
            # 2. 更新provider字段
            print("\n2. 更新provider字段...")
            result = await db.execute(text("""
                UPDATE ai_write_ai_model_config 
                SET provider = model_code 
                WHERE provider IS NULL OR provider = ''
            """))
            await db.commit()
            print(f"   ✅ 已更新 {result.rowcount} 条记录的provider字段")
            
            # 3. 查询更新后的结果
            print("\n3. 查询更新后的结果...")
            result = await db.execute(text("""
                SELECT 
                    config_id,
                    model_name,
                    model_type,
                    provider,
                    is_enabled,
                    is_default
                FROM ai_write_ai_model_config
                WHERE del_flag = '0'
                ORDER BY priority DESC
            """))
            records = result.fetchall()
            
            if records:
                print(f"   找到 {len(records)} 条记录:")
                for record in records:
                    config_id, model_name, model_type, provider, is_enabled, is_default = record
                    status = "✅ 启用" if is_enabled == '1' else "❌ 禁用"
                    default = " [默认]" if is_default == '1' else ""
                    print(f"   - [{config_id}] {model_name}{default}")
                    print(f"     类型: {model_type}, 提供商: {provider}, {status}")
            else:
                print("   ⚠️  没有找到记录")
            
            # 4. 检查是否有默认的语言模型
            print("\n4. 检查默认语言模型...")
            result = await db.execute(text("""
                SELECT 
                    model_name,
                    model_type,
                    provider
                FROM ai_write_ai_model_config
                WHERE model_type = 'language'
                  AND is_default = '1'
                  AND is_enabled = '1'
                  AND del_flag = '0'
            """))
            default_model = result.fetchone()
            
            if default_model:
                model_name, model_type, provider = default_model
                print(f"   ✅ 默认语言模型: {model_name} ({provider})")
            else:
                print("   ⚠️  没有设置默认语言模型")
                print("   提示: 请在AI模型管理页面设置一个默认的语言模型")
            
            print("\n" + "=" * 60)
            print("更新完成！")
            print("=" * 60)
            print("\n下一步:")
            print("1. 重启后端服务")
            print("2. 访问 http://localhost/thesis/ai-model")
            print("3. 如果没有默认模型，点击某个模型的'设为默认'按钮")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break


if __name__ == '__main__':
    asyncio.run(update_model_type())
