"""
清除 Redis 中的速率限制计数器
"""
import asyncio
import redis.asyncio as redis


async def clear_rate_limit():
    """清除速率限制计数器"""
    # 连接 Redis
    r = await redis.from_url('redis://localhost:6379/0', decode_responses=True)
    
    try:
        # 查找所有速率限制的键
        keys = []
        async for key in r.scan_iter('rate_limit:*'):
            keys.append(key)
        
        if keys:
            # 删除所有速率限制键
            deleted = await r.delete(*keys)
            print(f'✅ 已清除 {deleted} 个速率限制计数器')
        else:
            print('ℹ️  没有找到速率限制计数器')
    
    finally:
        await r.close()


if __name__ == '__main__':
    asyncio.run(clear_rate_limit())
