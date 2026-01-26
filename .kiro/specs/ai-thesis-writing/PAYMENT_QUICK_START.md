# 支付系统快速实施指南

## 当前状态

❌ **缺少的内容**：
1. 支付配置表（ai_write_payment_config）
2. 支付流水表（ai_write_payment_transaction）
3. 支付宝SDK集成
4. 微信支付SDK集成
5. 支付服务层（PaymentService）
6. 支付回调接口

---

## 快速实施（3步）

### 第1步：创建数据库表（5分钟）

执行以下SQL：

```sql
-- 支付配置表
CREATE TABLE ai_write_payment_config (
  config_id         BIGINT(20)      NOT NULL AUTO_INCREMENT    COMMENT '配置ID',
  payment_type      VARCHAR(20)     NOT NULL                   COMMENT '支付类型（alipay/wechat）',
  config_name       VARCHAR(50)     NOT NULL                   COMMENT '配置名称',
  
  app_id            VARCHAR(100)    DEFAULT ''                 COMMENT '应用ID',
  private_key       TEXT            DEFAULT NULL               COMMENT '应用私钥',
  public_key        TEXT            DEFAULT NULL               COMMENT '公钥',
  alipay_public_key TEXT            DEFAULT NULL               COMMENT '支付宝公钥',
  
  mch_id            VARCHAR(50)     DEFAULT ''                 COMMENT '商户号',
  api_key           VARCHAR(100)    DEFAULT ''                 COMMENT 'API密钥',
  api_v3_key        VARCHAR(100)    DEFAULT ''                 COMMENT 'APIv3密钥',
  cert_serial_no    VARCHAR(100)    DEFAULT ''                 COMMENT '证书序列号',
  private_cert_path VARCHAR(200)    DEFAULT ''                 COMMENT '私钥证书路径',
  
  notify_url        VARCHAR(200)    NOT NULL                   COMMENT '异步通知地址',
  return_url        VARCHAR(200)    DEFAULT ''                 COMMENT '同步返回地址',
  
  is_sandbox        CHAR(1)         DEFAULT '0'                COMMENT '是否沙箱（0否 1是）',
  is_default        CHAR(1)         DEFAULT '0'                COMMENT '是否默认（0否 1是）',
  
  status            CHAR(1)         DEFAULT '0'                COMMENT '状态（0正常 1停用）',
  del_flag          CHAR(1)         DEFAULT '0'                COMMENT '删除标志',
  create_by         VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       DATETIME                                   COMMENT '创建时间',
  update_by         VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       DATETIME                                   COMMENT '更新时间',
  remark            VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  PRIMARY KEY (config_id),
  UNIQUE KEY uk_payment_type (payment_type, is_default)
) ENGINE=INNODB COMMENT = '支付配置表';

-- 支付流水表
CREATE TABLE ai_write_payment_transaction (
  transaction_id    BIGINT(20)      NOT NULL AUTO_INCREMENT    COMMENT '流水ID',
  order_no          VARCHAR(50)     NOT NULL                   COMMENT '订单号',
  payment_type      VARCHAR(20)     NOT NULL                   COMMENT '支付类型',
  
  trade_no          VARCHAR(100)    DEFAULT ''                 COMMENT '第三方交易号',
  buyer_id          VARCHAR(100)    DEFAULT ''                 COMMENT '买家ID',
  buyer_account     VARCHAR(100)    DEFAULT ''                 COMMENT '买家账号',
  
  total_amount      DECIMAL(10,2)   NOT NULL                   COMMENT '订单金额',
  receipt_amount    DECIMAL(10,2)   DEFAULT 0.00               COMMENT '实收金额',
  
  payment_time      DATETIME        DEFAULT NULL               COMMENT '支付时间',
  notify_time       DATETIME        DEFAULT NULL               COMMENT '通知时间',
  
  trade_status      VARCHAR(20)     NOT NULL                   COMMENT '交易状态',
  notify_data       TEXT            DEFAULT NULL               COMMENT '通知原始数据',
  
  create_by         VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time       DATETIME                                   COMMENT '创建时间',
  update_by         VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time       DATETIME                                   COMMENT '更新时间',
  remark            VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  PRIMARY KEY (transaction_id),
  UNIQUE KEY uk_order_no (order_no),
  INDEX idx_trade_no (trade_no)
) ENGINE=INNODB COMMENT = '支付流水表';

-- 插入测试配置（沙箱环境）
INSERT INTO ai_write_payment_config (
  payment_type, config_name, app_id, notify_url, is_sandbox, is_default, status, create_by, create_time
) VALUES (
  'alipay', '支付宝沙箱配置', '你的APPID', 'https://yourdomain.com/api/thesis/order/payment/alipay/notify', '1', '1', '0', 'admin', NOW()
);
```

### 第2步：安装SDK（2分钟）

```bash
# 进入后端目录
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend

# 安装支付SDK
pip install alipay-sdk-python==3.7.4
pip install wechatpayv3==1.2.8

# 或添加到 requirements.txt
echo "alipay-sdk-python==3.7.4" >> requirements.txt
echo "wechatpayv3==1.2.8" >> requirements.txt
```

### 第3步：配置支付参数（10分钟）

#### 支付宝配置
1. 登录 [支付宝开放平台](https://open.alipay.com/)
2. 创建应用，获取 APPID
3. 配置应用公钥和私钥
4. 获取支付宝公钥
5. 配置回调地址

#### 微信支付配置
1. 登录 [微信支付商户平台](https://pay.weixin.qq.com/)
2. 获取商户号（mch_id）
3. 配置APIv3密钥
4. 下载商户证书
5. 配置回调地址

---

## 最小可用实现（MVP）

如果时间紧急，可以先实现最基础的功能：

### 方案A：仅支付宝PC支付（最简单）

```python
# 1. 安装SDK
pip install alipay-sdk-python==3.7.4

# 2. 在 order_service.py 中添加
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest

@classmethod
async def create_alipay_payment(cls, order_no: str, subject: str, amount: Decimal) -> str:
    """创建支付宝支付"""
    config = AlipayClientConfig()
    config.app_id = '你的APPID'
    config.app_private_key = '你的私钥'
    config.alipay_public_key = '支付宝公钥'
    config.server_url = 'https://openapi.alipaydev.com/gateway.do'  # 沙箱
    
    client = DefaultAlipayClient(alipay_client_config=config)
    
    model = AlipayTradePagePayModel()
    model.out_trade_no = order_no
    model.subject = subject
    model.total_amount = str(amount)
    model.product_code = 'FAST_INSTANT_TRADE_PAY'
    
    request = AlipayTradePagePayRequest(biz_model=model)
    request.notify_url = 'https://yourdomain.com/api/thesis/order/payment/alipay/notify'
    request.return_url = 'https://yourdomain.com/payment/success'
    
    return client.page_execute(request, http_method='GET')

# 3. 在 order_controller.py 中添加
@order_controller.post('/payment/create')
async def create_payment(
    order_id: int,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
):
    """创建支付"""
    order = await OrderService.get_order_detail(query_db, order_id)
    pay_url = await OrderService.create_alipay_payment(
        order.order_no,
        f'购买{order.order_type}',
        order.amount
    )
    return ResponseUtil.success(data={'pay_url': pay_url})

@order_controller.post('/payment/alipay/notify', include_in_schema=False)
async def alipay_notify(request: Request, query_db: Annotated[AsyncSession, DBSessionDependency()]):
    """支付宝回调"""
    form_data = await request.form()
    params = dict(form_data)
    
    # 简化版：不验证签名（仅测试用）
    order_no = params.get('out_trade_no')
    trade_status = params.get('trade_status')
    trade_no = params.get('trade_no')
    
    if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
        await OrderService.process_payment(query_db, order_no, trade_no)
    
    return 'success'
```

### 方案B：使用第三方聚合支付（推荐）

如果不想自己对接SDK，可以使用聚合支付服务：

**推荐服务**：
1. **Ping++** - https://www.pingxx.com/
2. **BeeCloud** - https://beecloud.cn/
3. **PayJS** - https://payjs.cn/

**优势**：
- ✅ 一次对接，支持多种支付方式
- ✅ SDK简单，文档完善
- ✅ 提供测试环境
- ✅ 有技术支持

---

## 测试流程

### 1. 沙箱测试（支付宝）

```python
# 使用支付宝沙箱账号测试
# 沙箱账号：https://openhome.alipay.com/develop/sandbox/app

# 测试步骤：
1. 创建订单
2. 调用支付接口，获取支付URL
3. 在浏览器打开支付URL
4. 使用沙箱买家账号登录支付
5. 确认支付
6. 等待回调通知
7. 检查订单状态
```

### 2. 本地回调测试

```bash
# 使用内网穿透工具（如ngrok）
ngrok http 8000

# 将生成的公网地址配置为回调地址
https://xxxx.ngrok.io/api/thesis/order/payment/alipay/notify
```

---

## 常见问题

### Q1: 回调地址必须是公网地址吗？
A: 是的，支付宝和微信都要求回调地址必须是公网可访问的HTTPS地址。本地测试可以使用ngrok等内网穿透工具。

### Q2: 沙箱环境和生产环境有什么区别？
A: 沙箱环境用于测试，不会真实扣款。生产环境需要企业认证和签约。

### Q3: 如何保证回调的安全性？
A: 必须验证签名，确保回调来自支付平台。同时要防止重复通知。

### Q4: 支付失败如何处理？
A: 记录失败原因，提示用户重新支付。可以提供订单查询功能，让用户手动刷新状态。

### Q5: 需要对账吗？
A: 建议每天定时对账，确保订单状态和支付平台一致。

---

## 下一步

完成支付系统后，建议：

1. ✅ 添加支付日志记录
2. ✅ 实现自动对账功能
3. ✅ 添加支付超时处理
4. ✅ 实现退款审核流程
5. ✅ 添加支付统计报表

---

## 参考文档

- [支付宝开放平台文档](https://opendocs.alipay.com/open/270)
- [微信支付开发文档](https://pay.weixin.qq.com/wiki/doc/apiv3/index.shtml)
- [alipay-sdk-python](https://github.com/alipay/alipay-sdk-python-all)
- [wechatpayv3](https://github.com/wechatpay-apiv3/wechatpay-python)
