# 管理员配额配置指南

## 问题描述
当管理员尝试创建论文时，出现"论文生成配额不足"的错误。

## 解决方案

### 方法1: 通过前端界面配置（推荐）

1. **登录系统**
   - 使用管理员账号登录（admin/admin123）

2. **进入会员配额管理**
   - 点击左侧菜单：`论文系统` → `会员管理` → `配额管理`
   - 或直接访问：http://localhost/thesis/member/quota

3. **添加配额**
   - 点击"新增"按钮
   - 填写表单：
     - 用户ID: 1 (admin用户的ID)
     - 功能类型: thesis_generation (论文生成)
     - 总配额: 1000
     - 已使用配额: 0
     - 剩余配额: 1000
     - 过期时间: 选择一年后的日期
     - 状态: 正常
   - 点击"确定"保存

### 方法2: 通过SQL脚本配置

如果前端界面无法访问，可以直接在数据库中执行SQL：

```sql
-- 1. 查看admin用户的user_id
SELECT user_id, user_name FROM sys_user WHERE user_name = 'admin';

-- 2. 为admin用户添加配额（假设user_id=1）
INSERT INTO thesis_user_feature_quota 
(user_id, feature_type, total_quota, used_quota, remaining_quota, 
 expire_time, status, create_time, update_time)
VALUES 
(1, 'thesis_generation', 1000, 0, 1000, 
 DATE_ADD(NOW(), INTERVAL 1 YEAR), '0', NOW(), NOW())
ON DUPLICATE KEY UPDATE
    total_quota = 1000,
    remaining_quota = 1000 - used_quota,
    update_time = NOW();

-- 3. 验证配额已添加
SELECT * FROM thesis_user_feature_quota 
WHERE user_id = 1 AND feature_type = 'thesis_generation';
```

**执行步骤：**
1. 连接到MySQL数据库：
   ```bash
   mysql -h 106.53.217.96 -u root -p ruoyi-fastapi
   ```
2. 输入密码：`gyswxgyb7418!`
3. 复制上面的SQL语句并执行
4. 刷新前端页面，重新尝试创建论文

### 方法3: 使用提供的SQL文件

我已经创建了一个SQL文件：`RuoYi-Vue3-FastAPI/add_admin_quota.sql`

你可以：
1. 使用MySQL客户端工具（如Navicat、DBeaver）打开这个文件
2. 连接到数据库后执行其中的SQL语句
3. 按照文件中的注释逐步操作

## 配额说明

### 功能类型 (feature_type)
- `thesis_generation`: 论文生成配额
- `template_usage`: 模板使用配额
- `ai_writing`: AI写作配额

### 状态 (status)
- `0`: 正常
- `1`: 禁用
- `2`: 已过期

### 配额计算
- `remaining_quota` = `total_quota` - `used_quota`
- 每次生成论文会扣减 `remaining_quota`
- 当 `remaining_quota` <= 0 时，无法继续生成

## 验证配额是否生效

1. 刷新浏览器页面
2. 进入"论文管理" → "论文列表"
3. 点击"新增"按钮
4. 填写论文信息并提交
5. 如果不再出现"配额不足"错误，说明配置成功

## 常见问题

### Q1: 为什么添加了配额还是提示不足？
A: 可能原因：
- 浏览器缓存，尝试刷新页面（Ctrl+F5）
- 配额记录的user_id不正确，确认是否为当前登录用户的ID
- 配额状态为禁用或已过期，检查status字段和expire_time字段

### Q2: 如何查看当前用户的user_id？
A: 执行SQL：
```sql
SELECT user_id, user_name FROM sys_user WHERE user_name = 'admin';
```

### Q3: 如何给其他用户添加配额？
A: 将SQL中的user_id替换为目标用户的ID即可

### Q4: 配额用完了怎么办？
A: 可以通过以下方式增加配额：
1. 前端界面：编辑配额记录，增加total_quota和remaining_quota
2. SQL更新：
```sql
UPDATE thesis_user_feature_quota 
SET total_quota = total_quota + 1000,
    remaining_quota = remaining_quota + 1000,
    update_time = NOW()
WHERE user_id = 1 AND feature_type = 'thesis_generation';
```

## 相关文件
- SQL脚本：`RuoYi-Vue3-FastAPI/add_admin_quota.sql`
- 前端页面：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/src/views/thesis/member/quota.vue`
- 后端接口：`RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_thesis/controller/member_controller.py`
