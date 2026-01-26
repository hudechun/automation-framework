# 统一支付网关实施清单

## 概述

本清单提供统一支付网关的完整实施步骤，支持多种支付方式（Ping++、支付宝、微信）动态切换。

---

## 第一阶段：数据库准备（30分钟）

### ✅ 任务清单

- [ ] 创建支付配置表（ai_write_payment_config）
- [ ] 创建支付流水表（ai_write_payment_transaction）
- [ ] 插入初始配置数据
- [ ] 验证表结构

### SQL脚本

```sql
-- 执行 UNIFIED_PAYMENT_GATEWAY.md 中的SQL脚本
```

---

## 第二阶段：SDK安装（10分钟）

### ✅ 任务清单

- [ ] 安装Ping++ SDK
- [ ] 安装支付宝SDK
- [ ] 安装微信支付SDK
- [ ] 验证安装

### 安装命令

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend

# 安装所有支付SDK
pip install pingpp==2.2.5
pip install alipay-sdk-python==3.7.4
pip install wechatpayv3==1.2.8

# 或添加到requirements.txt
echo "pingpp==2.2.5" >> requirements.txt
echo "alipay-sdk-python==3.7.4" >> requirements.txt
echo "wechatpayv3==1.2.8" >> requirements.txt
pip install -r requirements.txt
```

---

## 第三阶段：代码实现（4小时）

### ✅ 任务清单

#### 1. 基础架构（30分钟）
- [ ] 创建 `module_thesis/payment/` 目录
- [ ] 创建 `base_provider.py` - 支付提供商基类
- [ ] 创建 `__init__.py`

#### 2. 提供商实现（2小时）
- [ ] 创建 `pingpp_provider.py` - Ping++提供商
- [ ] 创建 `alipay_provider.py` - 支付宝提供商
- [ ] 创建 `wechat_provider.py` - 微信提供商
- [ ] 测试各提供商

#### 3. DAO层（30分钟）
- [ ] 创建 `payment_config_dao.py` - 支付配置DAO
- [ ] 创建 `payment_transaction_dao.py` - 支付流水DAO
- [ ] 添加到 `dao/__init__.py`

#### 4. Service层（1小时）
- [ ] 创建 `payment_gateway_service.py` - 统一网关服务
- [ ] 测试服务层

#### 5. Controller层（30分钟）
- [ ] 创建 `payment_controller.py` - 支付控制器
- [ ] 注册路由

---

## 第四阶段：配置管理（1小时）

### ✅ 任务清单

#### 1. Ping++配置
- [ ] 注册Ping++账号
- [ ] 完成企业认证
- [ ] 创建应用，获取API Key
- [ ] 配置支付渠道
- [ ] 更新数据库配置

#### 2. 支付宝配置（可选）
- [ ] 注册支付宝开放平台
- [ ] 创建应用
- [ ] 配置密钥
- [ ] 更新数据库配置

#### 3. 微信配置（可选）
- [ ] 注册微信支付商户
- [ ] 获取商户号和密钥
- [ ] 下载证书
- [ ] 更新数据库配置

---

## 第五阶段：前端集成（2小时）

### ✅ 任务清单

- [ ] 创建支付API接口文件
- [ ] 创建支付渠道选择组件
- [ ] 创建支付结果处理组件
- [ ] 创建支付配置管理页面
- [ ] 测试前端功能

---

## 第六阶段：测试（2小时）

### ✅ 测试清单

#### 1. 单元测试
- [ ] 测试Ping++提供商
- [ ] 测试支付宝提供商
- [ ] 测试微信提供商
- [ ] 测试网关服务

#### 2. 集成测试
- [ ] 测试创建支付（Ping++）
- [ ] 测试创建支付（支付宝）
- [ ] 测试创建支付（微信）
- [ ] 测试支付回调
- [ ] 测试查询支付
- [ ] 测试退款

#### 3. 场景测试
- [ ] 测试自动选择提供商
- [ ] 测试指定提供商
- [ ] 测试提供商切换
- [ ] 测试提供商故障切换

---

## 第七阶段：上线（1小时）

### ✅ 上线清单

#### 1. 生产环境配置
- [ ] 切换到生产API Key
- [ ] 配置生产回调地址
- [ ] 配置生产证书
- [ ] 验证配置

#### 2. 监控和日志
- [ ] 配置支付日志
- [ ] 配置异常告警
- [ ] 配置性能监控

#### 3. 文档
- [ ] 编写操作手册
- [ ] 编写故障处理手册
- [ ] 编写配置变更流程

---

## 快速开始（最小可用版本）

如果时间紧急，可以先实现最小可用版本：

### MVP版本（仅Ping++，2小时）

#### 1. 数据库（10分钟）
```sql
-- 只创建支付配置表，插入Ping++配置
INSERT INTO ai_write_payment_config (...) VALUES (...);
```

#### 2. 代码（1小时）
```python
# 只实现Ping++提供商
# 只实现基本的创建支付和回调
```

#### 3. 前端（30分钟）
```vue
<!-- 只实现支付宝PC支付 -->
```

#### 4. 测试（20分钟）
```bash
# 使用Ping++测试环境测试
```

---

## 文件结构

```
module_thesis/
├── payment/                          # 支付模块
│   ├── __init__.py
│   ├── base_provider.py             # 提供商基类
│   ├── pingpp_provider.py           # Ping++提供商
│   ├── alipay_provider.py           # 支付宝提供商
│   └── wechat_provider.py           # 微信提供商
│
├── dao/
│   ├── payment_config_dao.py        # 支付配置DAO
│   └── payment_transaction_dao.py   # 支付流水DAO
│
├── service/
│   └── payment_gateway_service.py   # 统一网关服务
│
└── controller/
    └── payment_controller.py        # 支付控制器
```

---

## 配置示例

### 数据库配置（JSON格式）

#### Ping++配置
```json
{
  "api_key": "sk_test_xxxxxx",
  "app_id": "app_xxxxxx",
  "private_key_path": "/path/to/key.pem",
  "pub_key_path": "/path/to/pub_key.pem",
  "webhook_url": "https://yourdomain.com/api/payment/webhook/pingpp"
}
```

#### 支付宝配置
```json
{
  "app_id": "2021001234567890",
  "private_key": "MIIEvQIBADANBgkqhkiG9w0...",
  "alipay_public_key": "MIIBIjANBgkqhkiG9w0...",
  "notify_url": "https://yourdomain.com/api/payment/webhook/alipay",
  "return_url": "https://yourdomain.com/payment/success",
  "is_sandbox": false
}
```

#### 微信配置
```json
{
  "app_id": "wx1234567890abcdef",
  "mch_id": "1234567890",
  "api_v3_key": "your_api_v3_key_32_characters",
  "cert_serial_no": "1234567890ABCDEF",
  "private_cert_path": "/path/to/apiclient_key.pem",
  "notify_url": "https://yourdomain.com/api/payment/webhook/wechat",
  "is_sandbox": false
}
```

---

## 常见问题

### Q1: 如何选择使用哪个提供商？
A: 系统会根据以下规则自动选择：
1. 如果指定了provider_type，使用指定的提供商
2. 否则，筛选支持该渠道的提供商
3. 按优先级排序，选择优先级最高的

### Q2: 如何切换提供商？
A: 修改数据库配置即可，无需改代码：
```sql
-- 禁用Ping++
UPDATE ai_write_payment_config SET is_enabled='0' WHERE provider_type='pingpp';

-- 启用支付宝
UPDATE ai_write_payment_config SET is_enabled='1', priority=100 WHERE provider_type='alipay';
```

### Q3: 可以同时启用多个提供商吗？
A: 可以。系统会根据优先级自动选择，也可以手动指定。

### Q4: 如何测试？
A: 所有提供商都提供测试环境：
- Ping++：使用测试API Key
- 支付宝：使用沙箱环境
- 微信：使用测试商户号

### Q5: 如何监控支付状态？
A: 建议：
1. 记录所有支付流水到数据库
2. 配置支付日志
3. 定时对账
4. 异常告警

---

## 进度跟踪

### 第1天
- [x] 数据库准备
- [x] SDK安装
- [ ] 基础架构实现
- [ ] Ping++提供商实现

### 第2天
- [ ] 支付宝提供商实现
- [ ] 微信提供商实现
- [ ] 网关服务实现
- [ ] Controller实现

### 第3天
- [ ] 前端集成
- [ ] 测试
- [ ] 上线

---

## 总结

### 实施时间
- **完整版本**：3天
- **MVP版本**：2小时

### 成本
- **开发成本**：3天 × 1000元 = 3,000元
- **维护成本**：几乎为0（配置化管理）
- **手续费**：根据选择的提供商

### 优势
- ✅ 灵活：支持多种支付方式
- ✅ 可靠：多个提供商互为备份
- ✅ 易维护：配置化管理
- ✅ 可扩展：易于添加新提供商

需要我帮您开始实现吗？
