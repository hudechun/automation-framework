# 会员表与功能配额表对比分析

## 表结构对比

### 1. ai_write_user_membership（用户会员表）

**用途**: 记录用户购买的会员套餐信息和整体配额

**核心字段**:
```sql
membership_id     -- 会员ID（主键）
user_id           -- 用户ID
package_id        -- 套餐ID

total_word_quota  -- 总字数配额
used_word_quota   -- 已使用字数

total_usage_quota -- 总使用次数
used_usage_quota  -- 已使用次数

start_date        -- 开始时间
end_date          -- 结束时间
status            -- 状态（0正常 1停用 2过期）
```

**特点**:
- **一个用户一条记录**（或按套餐续费时更新）
- **整体配额管理**：统一管理字数和使用次数
- **与套餐绑定**：记录用户购买的具体套餐
- **时间范围**：有明确的开始和结束时间

### 2. ai_write_user_feature_quota（用户功能配额表）

**用途**: 按功能类型细分管理用户的配额

**核心字段**:
```sql
quota_id          -- 配额ID（主键）
user_id           -- 用户ID
service_type      -- 服务类型（de_ai/polish/aigc_detection/plagiarism_check）

total_quota       -- 总配额（字数）
used_quota        -- 已使用配额

start_date        -- 开始时间
end_date          -- 结束时间

source            -- 来源（package/purchase）
source_id         -- 来源ID（套餐ID或订单ID）
status            -- 状态（0正常 1停用 2过期）
```

**特点**:
- **一个用户多条记录**（按服务类型分开）
- **细分配额管理**：每种服务类型独立配额
- **多来源支持**：可以来自套餐，也可以单独购买
- **灵活扩展**：支持不同服务类型的独立配额

## 设计意图对比

| 维度 | ai_write_user_membership | ai_write_user_feature_quota |
|------|-------------------------|----------------------------|
| **粒度** | 粗粒度（整体会员） | 细粒度（按功能类型） |
| **记录数** | 1条/用户 | N条/用户（N=服务类型数） |
| **配额类型** | 字数 + 使用次数 | 字数（按服务类型） |
| **业务场景** | 套餐会员 | 单次服务购买 |
| **时间管理** | 会员有效期 | 配额有效期 |
| **来源追溯** | 套餐ID | 套餐ID或订单ID |

## 使用场景

### 场景1: 用户购买会员套餐

**流程**:
1. 用户购买"专业版套餐"（199元/月）
2. 在 `ai_write_user_membership` 创建记录：
   ```
   user_id: 1
   package_id: 2
   total_word_quota: 100000
   total_usage_quota: 50
   start_date: 2026-01-26
   end_date: 2026-02-26
   ```

**当前实现**: ✅ 只使用会员表，配额统一管理

### 场景2: 用户单独购买某项服务

**流程**:
1. 用户单独购买"AI降重服务"（50元/5000字）
2. 在 `ai_write_user_feature_quota` 创建记录：
   ```
   user_id: 1
   service_type: 'de_ai'
   total_quota: 5000
   source: 'purchase'
   source_id: 订单ID
   start_date: 2026-01-26
   end_date: 2026-12-31
   ```

**当前实现**: ❌ 未实现，功能配额表未使用

### 场景3: 套餐包含多种服务配额

**流程**:
1. 用户购买"旗舰版套餐"
2. 套餐包含：
   - 论文生成：50次
   - AI降重：20000字
   - 查重检测：10次
   - 智能润色：15000字

**方案A（当前）**: 在会员表统一管理
```
ai_write_user_membership:
  total_usage_quota: 50  // 所有功能共享次数
  total_word_quota: 100000  // 所有功能共享字数
```

**方案B（细分）**: 在功能配额表分别管理
```
ai_write_user_feature_quota:
  [service_type='thesis_generation', total_quota=50]
  [service_type='de_ai', total_quota=20000]
  [service_type='plagiarism_check', total_quota=10]
  [service_type='polish', total_quota=15000]
```

## 当前问题分析

### 问题1: 表设计不一致

**会员表字段**:
- `total_word_quota` / `used_word_quota`
- `total_usage_quota` / `used_usage_quota`

**功能配额表字段**:
- `total_quota` / `used_quota`（只有一种配额）

**结论**: 会员表支持"字数+次数"双配额，功能配额表只支持单一配额

### 问题2: 代码逻辑混乱

**原代码问题**:
```python
# check_quota() 查询功能配额表
quota = await UserFeatureQuotaDao.get_quota_by_user_and_feature(...)

# 但 activate_membership() 不初始化功能配额表
# await cls._init_user_quotas(query_db, user_id, package.features)  # 被注释掉
```

**导致**: 会员激活后，功能配额表没有记录，check_quota() 返回 False

### 问题3: 业务需求不明确

**当前需求**: 只支持套餐购买，不支持单次服务购买
**表设计**: 两个表都存在，但只用了会员表

## 解决方案对比

### 方案A: 只使用会员表（当前采用）

**优点**:
- 简单直接，易于理解
- 适合纯套餐模式
- 减少表关联查询

**缺点**:
- 无法细分不同服务的配额
- 无法支持单次服务购买
- 扩展性较差

**适用场景**:
- 只有套餐购买
- 所有功能共享配额
- 不需要区分服务类型

### 方案B: 同时使用两个表

**优点**:
- 支持套餐 + 单次购买
- 可以细分不同服务配额
- 扩展性强

**缺点**:
- 逻辑复杂
- 需要处理配额叠加
- 查询性能略低

**适用场景**:
- 套餐 + 单次服务混合模式
- 需要区分不同服务配额
- 需要灵活的配额管理

### 方案C: 只使用功能配额表

**优点**:
- 统一配额管理
- 灵活性最高
- 支持所有场景

**缺点**:
- 需要重构会员表
- 套餐激活时需要拆分配额
- 查询时需要聚合多条记录

**适用场景**:
- 完全按服务类型计费
- 需要精细化配额管理
- 未来可能增加更多服务类型

## 推荐方案

### 短期方案（已实施）

**只使用会员表**，简化逻辑：

```python
# 配额检查
membership = await get_user_membership(user_id)
remaining = membership.total_usage_quota - membership.used_usage_quota

# 配额扣减
await UserMembershipDao.update_quota_usage(
    membership_id, 
    word_count=0, 
    usage_count=1
)
```

**优点**: 快速解决当前问题，代码简单

### 长期方案（建议）

**保留两个表，明确分工**：

1. **ai_write_user_membership**: 管理会员身份和套餐配额
   - 用户购买套餐时创建
   - 记录会员有效期
   - 记录套餐整体配额

2. **ai_write_user_feature_quota**: 管理细分服务配额
   - 套餐激活时，根据套餐内容拆分创建
   - 单独购买服务时创建
   - 支持多来源配额叠加

**实现逻辑**:
```python
# 套餐激活
async def activate_membership(user_id, package_id):
    # 1. 创建会员记录
    await create_membership(user_id, package_id)
    
    # 2. 拆分创建功能配额
    package = await get_package(package_id)
    for service_type, quota in package.features.items():
        await create_feature_quota(
            user_id=user_id,
            service_type=service_type,
            total_quota=quota,
            source='package',
            source_id=package_id
        )

# 配额检查（优先使用功能配额）
async def check_quota(user_id, service_type, amount):
    # 1. 查询该服务类型的所有有效配额
    quotas = await get_feature_quotas(user_id, service_type)
    
    # 2. 计算总剩余配额
    total_remaining = sum(q.total_quota - q.used_quota for q in quotas)
    
    return total_remaining >= amount
```

## 数据迁移建议

如果要从方案A迁移到方案B/C：

```sql
-- 1. 从会员表拆分到功能配额表
INSERT INTO ai_write_user_feature_quota (
    user_id, service_type, total_quota, used_quota,
    start_date, end_date, source, source_id, status
)
SELECT 
    user_id,
    'thesis_generation' as service_type,
    total_usage_quota as total_quota,
    used_usage_quota as used_quota,
    start_date,
    end_date,
    'package' as source,
    package_id as source_id,
    status
FROM ai_write_user_membership
WHERE status = '0';

-- 2. 可以保留会员表作为会员身份记录
-- 或者删除会员表的配额字段
```

## 总结

**两个表的本质区别**:

| 表名 | 管理对象 | 粒度 | 用途 |
|------|---------|------|------|
| ai_write_user_membership | 会员身份 | 粗 | 套餐会员管理 |
| ai_write_user_feature_quota | 服务配额 | 细 | 功能配额管理 |

**当前状态**: 只使用会员表，功能配额表闲置

**建议**: 
- 短期：继续使用会员表（已实施）
- 长期：如果需要支持单次服务购买，启用功能配额表
