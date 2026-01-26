# 支付SDK安装指南

## 概述

统一支付网关需要安装3个支付SDK，本文档提供详细的安装和配置说明。

---

## 一、SDK列表

| SDK | 版本 | 用途 | 是否必需 |
|-----|------|------|---------|
| pingpp | 2.2.5 | Ping++聚合支付 | 可选 |
| alipay-sdk-python | 3.7.4 | 支付宝直连 | 可选 |
| wechatpayv3 | 1.2.8 | 微信支付直连 | 可选 |

**说明**：
- 至少需要安装一个SDK才能使用支付功能
- 建议安装Ping++，它支持最多的支付渠道
- 各SDK独立工作，未安装的SDK不影响其他SDK

---

## 二、安装方法

### 方法1：直接安装（推荐）

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend

# 安装所有支付SDK
pip install pingpp==2.2.5
pip install alipay-sdk-python==3.7.4
pip install wechatpayv3==1.2.8
```

### 方法2：通过requirements.txt安装

1. 编辑 `requirements.txt`，添加以下内容：

```txt
# 支付SDK
pingpp==2.2.5
alipay-sdk-python==3.7.4
wechatpayv3==1.2.8
```

2. 安装：

```bash
pip install -r requirements.txt
```

### 方法3：只安装需要的SDK

```bash
# 只安装Ping++（推荐，支持最多渠道）
pip install pingpp==2.2.5

# 或只安装支付宝
pip install alipay-sdk-python==3.7.4

# 或只安装微信
pip install wechatpayv3==1.2.8
```

---

## 三、验证安装

### 验证Ping++

```python
python -c "import pingpp; print('Ping++ SDK安装成功')"
```

### 验证支付宝

```python
python -c "from alipay.aop.api.AlipayClientConfig import AlipayClientConfig; print('支付宝SDK安装成功')"
```

### 验证微信

```python
python -c "from wechatpayv3 import WeChatPay; print('微信支付SDK安装成功')"
```

---

## 四、配置说明

### 1. Ping++配置

#### 注册账号
1. 访问 https://www.pingxx.com/
2. 注册企业账号
3. 完成企业认证（需要3-5个工作日）

#### 获取配置
1. 登录Ping++控制台
2. 创建应用
3. 获取以下信息：
   - API Key（sk_test_xxx 或 sk_live_xxx）
   - App ID（app_xxx）
   - 私钥文件（key.pem）
   - 公钥文件（pub_key.pem）

#### 更新数据库配置

```sql
UPDATE ai_write_payment_config 
SET config_data = '{
  "api_key": "sk_test_xxxxxx",
  "app_id": "app_xxxxxx",
  "private_key_path": "/path/to/key.pem",
  "pub_key_path": "/path/to/pub_key.pem",
  "webhook_url": "https://yourdomain.com/api/thesis/payment/webhook/pingpp"
}',
is_enabled = '1'
WHERE provider_type = 'pingpp';
```

### 2. 支付宝配置

#### 注册账号
1. 访问 https://open.alipay.com/
2. 注册开发者账号
3. 创建应用

#### 获取配置
1. 登录支付宝开放平台
2. 创建应用
3. 配置密钥（RSA2）
4. 获取以下信息：
   - App ID（2021001234567890）
   - 应用私钥
   - 支付宝公钥

#### 更新数据库配置

```sql
UPDATE ai_write_payment_config 
SET config_data = '{
  "app_id": "2021001234567890",
  "private_key": "MIIEvQIBADANBgkqhkiG9w0...",
  "alipay_public_key": "MIIBIjANBgkqhkiG9w0...",
  "notify_url": "https://yourdomain.com/api/thesis/payment/webhook/alipay",
  "return_url": "https://yourdomain.com/payment/success",
  "is_sandbox": false
}',
is_enabled = '1'
WHERE provider_type = 'alipay';
```

### 3. 微信支付配置

#### 注册账号
1. 访问 https://pay.weixin.qq.com/
2. 注册商户号
3. 完成企业认证

#### 获取配置
1. 登录微信支付商户平台
2. 获取以下信息：
   - App ID（wx1234567890abcdef）
   - 商户号（1234567890）
   - API v3密钥（32位字符）
   - 证书序列号
3. 下载API证书（apiclient_key.pem）

#### 更新数据库配置

```sql
UPDATE ai_write_payment_config 
SET config_data = '{
  "app_id": "wx1234567890abcdef",
  "mch_id": "1234567890",
  "api_v3_key": "your_api_v3_key_32_characters",
  "cert_serial_no": "1234567890ABCDEF",
  "private_cert_path": "/path/to/apiclient_key.pem",
  "notify_url": "https://yourdomain.com/api/thesis/payment/webhook/wechat",
  "is_sandbox": false
}',
is_enabled = '1'
WHERE provider_type = 'wechat';
```

---

## 五、测试环境配置

### Ping++测试环境

```sql
UPDATE ai_write_payment_config 
SET config_data = '{
  "api_key": "sk_test_xxxxxx",
  ...
}'
WHERE provider_type = 'pingpp';
```

**说明**：使用 `sk_test_` 开头的API Key即为测试环境

### 支付宝沙箱环境

```sql
UPDATE ai_write_payment_config 
SET config_data = '{
  "app_id": "沙箱应用ID",
  "is_sandbox": true,
  ...
}'
WHERE provider_type = 'alipay';
```

**说明**：
1. 访问 https://openhome.alipay.com/develop/sandbox/app
2. 获取沙箱应用ID和密钥
3. 设置 `is_sandbox: true`

### 微信测试环境

```sql
UPDATE ai_write_payment_config 
SET config_data = '{
  "mch_id": "测试商户号",
  ...
}'
WHERE provider_type = 'wechat';
```

**说明**：使用微信提供的测试商户号

---

## 六、证书文件管理

### 证书存放位置

建议将证书文件存放在安全目录：

```bash
# 创建证书目录
mkdir -p /opt/payment_certs

# 设置权限
chmod 700 /opt/payment_certs

# 存放证书
/opt/payment_certs/
├── pingpp/
│   ├── key.pem
│   └── pub_key.pem
├── alipay/
│   └── (不需要证书文件)
└── wechat/
    └── apiclient_key.pem
```

### 更新配置中的路径

```sql
-- Ping++
UPDATE ai_write_payment_config 
SET config_data = JSON_SET(
  config_data,
  '$.private_key_path', '/opt/payment_certs/pingpp/key.pem',
  '$.pub_key_path', '/opt/payment_certs/pingpp/pub_key.pem'
)
WHERE provider_type = 'pingpp';

-- 微信
UPDATE ai_write_payment_config 
SET config_data = JSON_SET(
  config_data,
  '$.private_cert_path', '/opt/payment_certs/wechat/apiclient_key.pem'
)
WHERE provider_type = 'wechat';
```

---

## 七、回调地址配置

### 配置回调地址

在各支付平台配置回调地址：

| 平台 | 回调地址 |
|------|---------|
| Ping++ | https://yourdomain.com/api/thesis/payment/webhook/pingpp |
| 支付宝 | https://yourdomain.com/api/thesis/payment/webhook/alipay |
| 微信 | https://yourdomain.com/api/thesis/payment/webhook/wechat |

### 注意事项

1. **必须使用HTTPS**（生产环境）
2. **回调地址必须公网可访问**
3. **确保服务器防火墙开放端口**
4. **测试环境可以使用内网穿透工具**（如ngrok）

---

## 八、快速测试

### 1. 测试SDK是否正常

```bash
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend

# 测试Ping++
python -c "
import pingpp
pingpp.api_key = 'sk_test_xxxxxx'
print('Ping++ SDK正常')
"

# 测试支付宝
python -c "
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
config = AlipayClientConfig()
print('支付宝SDK正常')
"

# 测试微信
python -c "
from wechatpayv3 import WeChatPay
print('微信支付SDK正常')
"
```

### 2. 测试API接口

```bash
# 获取可用支付渠道
curl http://localhost:8000/api/thesis/payment/channels

# 预期返回
{
  "code": 200,
  "data": [
    {
      "channel": "alipay_pc",
      "name": "支付宝PC支付",
      ...
    }
  ]
}
```

---

## 九、常见问题

### Q1: pip安装失败怎么办？

```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pingpp==2.2.5
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple alipay-sdk-python==3.7.4
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple wechatpayv3==1.2.8
```

### Q2: 证书文件找不到怎么办？

检查文件路径和权限：

```bash
# 检查文件是否存在
ls -la /opt/payment_certs/pingpp/key.pem

# 检查权限
chmod 600 /opt/payment_certs/pingpp/key.pem
```

### Q3: 回调地址无法访问怎么办？

测试环境可以使用内网穿透：

```bash
# 使用ngrok
ngrok http 8000

# 获得公网地址
https://xxxx.ngrok.io

# 配置回调地址
https://xxxx.ngrok.io/api/thesis/payment/webhook/pingpp
```

### Q4: 如何验证配置是否正确？

```bash
# 查看数据库配置
SELECT provider_type, is_enabled, priority 
FROM ai_write_payment_config 
WHERE del_flag='0';

# 测试创建支付
curl -X POST http://localhost:8000/api/thesis/payment/create \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "channel": "alipay_pc"}'
```

---

## 十、生产环境检查清单

部署到生产环境前，请确认：

- [ ] 所有SDK已安装
- [ ] 使用生产环境API Key（不是测试Key）
- [ ] 证书文件已上传到服务器
- [ ] 证书文件权限正确（600或400）
- [ ] 回调地址使用HTTPS
- [ ] 回调地址已在支付平台配置
- [ ] 防火墙已开放端口
- [ ] 数据库配置已更新
- [ ] 已启用需要的支付提供商
- [ ] 已测试支付流程

---

**最后更新**: 2026-01-25  
**更新人**: Kiro AI Assistant
