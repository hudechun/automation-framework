# AI模型菜单生成失败 - 修复指南

## 问题原因

原始的 `ai_model_menu.sql` 使用了MySQL变量和动态menu_id，这在某些情况下会导致执行失败。

## 解决方案

已修复SQL文件，使用固定的menu_id（5600系列），与论文系统其他菜单保持一致。

## 快速修复

### 方式1: 使用Python脚本（推荐）

```bash
cd RuoYi-Vue3-FastAPI
python add_ai_model_menu.py <数据库密码>
```

### 方式2: 手动执行SQL

```bash
mysql -u root -p ry-vue < ruoyi-fastapi-backend/sql/ai_model_menu.sql
```

### 方式3: 使用完整部署脚本

```bash
cd RuoYi-Vue3-FastAPI
python deploy_ai_model.py <数据库密码>
```

## 验证菜单

执行以下SQL验证菜单是否创建成功：

```sql
-- 查看AI模型配置菜单
SELECT menu_id, menu_name, parent_id, order_num, perms 
FROM sys_menu 
WHERE menu_id >= 5600 AND menu_id < 5700
ORDER BY menu_id;
```

应该看到6个菜单项：
- 5600: AI模型配置（主菜单）
- 5601: 查询AI模型
- 5602: 新增AI模型
- 5603: 修改AI模型
- 5604: 删除AI模型
- 5605: 测试连接

## 菜单ID分配

论文系统菜单ID分配：
- 5000: AI论文写作（一级菜单）
- 5100: 会员管理
- 5200: 论文管理
- 5300: 模板管理
- 5400: 订单管理
- 5500: 支付管理
- **5600: AI模型配置** ← 新增

## 常见问题

### Q1: 提示"论文系统菜单不存在"

**原因**: 还没有创建论文系统的主菜单

**解决**:
```bash
mysql -u root -p ry-vue < ruoyi-fastapi-backend/sql/thesis_menus.sql
```

### Q2: 菜单重复

**原因**: 多次执行了菜单SQL

**解决**:
```sql
-- 删除重复菜单
DELETE FROM sys_menu WHERE menu_id >= 5600 AND menu_id < 5700;

-- 重新执行菜单脚本
```

### Q3: 菜单不显示

**原因**: 
1. 后端未重启
2. 前端缓存未清除
3. 用户角色没有权限

**解决**:
1. 重启后端服务
2. 清除浏览器缓存（Ctrl+Shift+Delete）
3. 检查角色权限：
```sql
-- 为管理员角色添加权限
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE menu_id >= 5600 AND menu_id < 5700;
```

## 完整部署流程

如果是全新部署，按以下顺序执行：

```bash
# 1. 创建表结构
mysql -u root -p ry-vue < ruoyi-fastapi-backend/sql/ai_model_schema.sql

# 2. 创建论文系统菜单（如果还没有）
mysql -u root -p ry-vue < ruoyi-fastapi-backend/sql/thesis_menus.sql

# 3. 创建AI模型菜单
python add_ai_model_menu.py <数据库密码>

# 4. 重启后端
cd ruoyi-fastapi-backend
python app.py

# 5. 刷新前端
# 清除浏览器缓存并刷新页面
```

## 修复后的SQL文件

新的 `ai_model_menu.sql` 文件特点：
- ✅ 使用固定的menu_id（5600系列）
- ✅ 不依赖MySQL变量
- ✅ 包含删除旧菜单的逻辑
- ✅ 与论文系统其他菜单格式一致
- ✅ 包含验证查询

## 联系支持

如果问题仍然存在，请提供以下信息：
1. 错误信息截图
2. 数据库版本：`SELECT VERSION();`
3. 现有菜单：`SELECT * FROM sys_menu WHERE menu_id = 5000;`

---

**更新时间**: 2026-01-25  
**状态**: ✅ 已修复
