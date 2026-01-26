"""
部署全局AI配置系统
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent / 'ruoyi-fastapi-backend'
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from config.database import get_db


async def deploy_global_ai_config():
    """部署全局AI配置系统"""
    print("=" * 60)
    print("开始部署全局AI配置系统")
    print("=" * 60)
    
    async for db in get_db():
        try:
            # 1. 创建系统AI模型配置表
            print("\n[1/3] 创建系统AI模型配置表...")
            with open('ruoyi-fastapi-backend/sql/sys_ai_model_config.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 分割SQL语句
            statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement:
                    await db.execute(text(statement))
            
            await db.commit()
            print("✓ 系统AI模型配置表创建成功")
            
            # 2. 插入菜单
            print("\n[2/3] 插入系统管理菜单...")
            with open('ruoyi-fastapi-backend/sql/sys_ai_model_menu.sql', 'r', encoding='utf-8') as f:
                menu_sql = f.read()
            
            # 分割SQL语句
            menu_statements = [s.strip() for s in menu_sql.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in menu_statements:
                if statement:
                    await db.execute(text(statement))
            
            await db.commit()
            print("✓ 系统管理菜单插入成功")
            
            # 3. 验证数据
            print("\n[3/3] 验证部署结果...")
            
            # 检查表是否创建
            result = await db.execute(text("SHOW TABLES LIKE 'sys_ai_model_config'"))
            if result.fetchone():
                print("✓ 表 sys_ai_model_config 创建成功")
            else:
                print("✗ 表 sys_ai_model_config 创建失败")
                return
            
            # 检查预设模型数量
            result = await db.execute(text("SELECT COUNT(*) FROM sys_ai_model_config WHERE is_preset = '1'"))
            preset_count = result.scalar()
            print(f"✓ 预设模型数量: {preset_count}")
            
            # 检查语言模型数量
            result = await db.execute(text("SELECT COUNT(*) FROM sys_ai_model_config WHERE model_type = 'language'"))
            language_count = result.scalar()
            print(f"✓ 语言模型数量: {language_count}")
            
            # 检查视觉模型数量
            result = await db.execute(text("SELECT COUNT(*) FROM sys_ai_model_config WHERE model_type = 'vision'"))
            vision_count = result.scalar()
            print(f"✓ 视觉模型数量: {vision_count}")
            
            # 检查菜单是否插入
            result = await db.execute(text("SELECT COUNT(*) FROM sys_menu WHERE menu_name = 'AI模型配置' AND parent_id = 1"))
            menu_count = result.scalar()
            if menu_count > 0:
                print("✓ 系统管理菜单插入成功")
            else:
                print("✗ 系统管理菜单插入失败")
            
            print("\n" + "=" * 60)
            print("全局AI配置系统部署完成！")
            print("=" * 60)
            print("\n下一步操作：")
            print("1. 重启后端服务")
            print("2. 在系统管理 > AI模型配置中配置API Key")
            print("3. 启用需要使用的模型")
            print("4. 设置默认模型")
            print("\n支持的模型类型：")
            print("- 语言模型（language）：用于文本生成、论文写作等")
            print("- 视觉模型（vision）：用于图像识别、验证码识别等")
            print("\n支持的提供商：")
            print("- OpenAI: GPT-4, GPT-3.5, GPT-4 Vision")
            print("- Anthropic: Claude 3 Opus, Sonnet, Haiku")
            print("- Qwen: 通义千问 Max, Plus, Turbo, Long, VL")
            
        except Exception as e:
            await db.rollback()
            print(f"\n✗ 部署失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        finally:
            await db.close()


if __name__ == '__main__':
    asyncio.run(deploy_global_ai_config())
