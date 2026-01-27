"""
初始化通用格式指令系统
将JSON文件中的完整指令系统插入到数据库
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal
from module_thesis.dao.template_dao import UniversalInstructionSystemDao
from utils.log_util import logger


async def init_universal_instruction_system():
    """
    初始化通用格式指令系统
    """
    # 获取JSON文件路径
    current_dir = Path(__file__).parent.parent
    json_file = current_dir / 'config' / 'universal_instruction_system.json'
    
    if not json_file.exists():
        logger.error(f"完整指令系统JSON文件不存在: {json_file}")
        return False
    
    # 读取JSON文件
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            instruction_data = json.load(f)
        logger.info(f"成功读取完整指令系统JSON文件: {json_file}")
    except Exception as e:
        logger.error(f"读取完整指令系统JSON文件失败: {str(e)}")
        return False
    
    # 连接数据库
    async with AsyncSessionLocal() as db:
        try:
            # 检查是否已存在激活的指令系统
            existing = await UniversalInstructionSystemDao.get_active_instruction_system(db)
            
            if existing:
                logger.info(f"已存在激活的指令系统（版本: {existing.version}），是否更新？")
                # 如果需要更新，可以先停用旧的，然后插入新的
                # 这里先跳过，如果需要更新可以手动处理
                logger.info("跳过初始化（已存在激活的指令系统）")
                return True
            
            # 准备插入数据
            insert_data = {
                'version': instruction_data.get('version', '1.0'),
                'description': instruction_data.get('description', '通用格式指令系统'),
                'instruction_data': instruction_data,
                'is_active': '1',
                'create_by': 'system',
                'remark': '系统自动初始化'
            }
            
            # 插入数据库
            new_system = await UniversalInstructionSystemDao.add_instruction_system(db, insert_data)
            
            # 在commit之前访问属性，避免异步上下文问题
            system_id = new_system.id
            system_version = new_system.version
            
            await db.commit()
            
            logger.info(f"成功初始化完整指令系统，ID: {system_id}, 版本: {system_version}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"初始化完整指令系统失败: {str(e)}", exc_info=True)
            return False


async def main():
    """
    主函数
    """
    logger.info("=" * 100)
    logger.info("开始初始化通用格式指令系统")
    logger.info("=" * 100)
    
    success = await init_universal_instruction_system()
    
    if success:
        logger.info("=" * 100)
        logger.info("✓ 通用格式指令系统初始化成功")
        logger.info("=" * 100)
    else:
        logger.error("=" * 100)
        logger.error("✗ 通用格式指令系统初始化失败")
        logger.error("=" * 100)
    
    return success


if __name__ == '__main__':
    asyncio.run(main())
