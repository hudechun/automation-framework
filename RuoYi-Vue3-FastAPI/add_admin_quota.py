"""
为管理员账号添加论文生成配额
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / 'ruoyi-fastapi-backend'))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config.env import DataBaseConfig


async def add_admin_quota():
    """为admin用户添加配额"""
    
    # 创建数据库连接
    if DataBaseConfig.db_type == 'mysql':
        db_url = f"mysql+aiomysql://{DataBaseConfig.db_username}:{DataBaseConfig.db_password}@{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}?charset=utf8mb4"
    else:
        db_url = f"postgresql+asyncpg://{DataBaseConfig.db_username}:{DataBaseConfig.db_password}@{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}"
    
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 1. 查找admin用户的user_id
            result = await session.execute(
                text('SELECT user_id FROM sys_user WHERE user_name = "admin"')
            )
            admin_user = result.first()
            
            if not admin_user:
                print("❌ 未找到admin用户")
                return
            
            user_id = admin_user[0]
            print(f"✅ 找到admin用户，user_id: {user_id}")
            
            # 2. 检查是否已有配额记录
            result = await session.execute(
                text("""
                SELECT quota_id, total_quota, used_quota, remaining_quota 
                FROM thesis_user_feature_quota 
                WHERE user_id = :user_id AND feature_type = 'thesis_generation'
                """),
                {"user_id": user_id}
            )
            quota_record = result.first()
            
            if quota_record:
                print(f"📊 当前配额状态:")
                print(f"   - 总配额: {quota_record[1]}")
                print(f"   - 已使用: {quota_record[2]}")
                print(f"   - 剩余: {quota_record[3]}")
                
                # 更新配额
                await session.execute(
                    text("""
                    UPDATE thesis_user_feature_quota 
                    SET total_quota = 1000, 
                        remaining_quota = 1000 - used_quota,
                        update_time = NOW()
                    WHERE quota_id = :quota_id
                    """),
                    {"quota_id": quota_record[0]}
                )
                print("✅ 配额已更新为 1000")
            else:
                # 插入新配额记录
                await session.execute(
                    text("""
                    INSERT INTO thesis_user_feature_quota 
                    (user_id, feature_type, total_quota, used_quota, remaining_quota, 
                     expire_time, status, create_time, update_time)
                    VALUES 
                    (:user_id, 'thesis_generation', 1000, 0, 1000, 
                     DATE_ADD(NOW(), INTERVAL 1 YEAR), '0', NOW(), NOW())
                    """),
                    {"user_id": user_id}
                )
                print("✅ 已创建新配额记录，配额: 1000")
            
            await session.commit()
            print("\n🎉 配额配置成功！")
            print("💡 提示: 你现在可以创建论文了")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ 配置失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == '__main__':
    print("=" * 60)
    print("为管理员账号添加论文生成配额")
    print("=" * 60)
    asyncio.run(add_admin_quota())
