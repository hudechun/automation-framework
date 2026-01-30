# 后台部署指南（服务器 106.53.217.96）

本文档描述在已安装 MySQL、Redis、Nginx、Python 3.9 的 Linux 服务器上部署 RuoYi-FastAPI 后台的完整流程。

---

## 一、前置条件

| 组件 | 版本/要求 | 说明 |
|------|----------|------|
| 操作系统 | Linux (Ubuntu/CentOS) | - |
| Python | 3.9 或 3.10 | 已安装 |
| MySQL | 8.0 推荐 | 已安装 |
| Redis | 5.0+ | 已安装 |
| Nginx | 1.18+ | 已安装 |

---

## 二、MySQL 配置

### 2.1 创建数据库和用户

```bash
# 登录 MySQL
mysql -u root -p

# 执行以下 SQL
CREATE DATABASE IF NOT EXISTS `ruoyi-fastapi` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE USER 'ruoyi'@'localhost' IDENTIFIED BY '你的数据库密码';
GRANT ALL PRIVILEGES ON `ruoyi-fastapi`.* TO 'ruoyi'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2.2 导入初始化 SQL（按顺序执行）

```bash
cd /opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql

# 1. 主库结构
mysql -u ruoyi -p ruoyi-fastapi < ruoyi-fastapi.sql

# 2. 学籍验证相关
mysql -u ruoyi -p ruoyi-fastapi < student_verification_schema.sql
mysql -u ruoyi -p ruoyi-fastapi < student_verification_menu.sql
mysql -u ruoyi -p ruoyi-fastapi < student_verification_add_learning_form.sql

# 3. 若使用论文模块
mysql -u ruoyi -p ruoyi-fastapi < thesis_schema.sql
mysql -u ruoyi -p ruoyi-fastapi < thesis_dicts.sql
mysql -u ruoyi -p ruoyi-fastapi < thesis_menus.sql

# 4. 若使用 AI 模型配置
mysql -u ruoyi -p ruoyi-fastapi < ai_model_schema.sql
mysql -u ruoyi -p ruoyi-fastapi < sys_ai_model_config.sql
mysql -u ruoyi -p ruoyi-fastapi < sys_ai_model_menu.sql
```

> 若使用 root 用户，将 `ruoyi` 改为 `root`。

---

## 三、Redis 配置

确认 Redis 已启动并可选配置密码：

```bash
# 检查 Redis 状态
redis-cli ping
# 应返回 PONG

# 若 Redis 有密码，需在 .env.prod 中配置 REDIS_PASSWORD
```

---

## 四、后台代码与虚拟环境

### 4.1 上传代码

将项目上传到服务器，例如 `/opt/ruoyi/`：

```bash
# 方式一：git clone（若已有仓库）
cd /opt/ruoyi
git clone <你的仓库地址> AutoFlow-Platform
cd AutoFlow-Platform

# 方式二：本地上传
# 使用 scp、rsync 或 SFTP 将 RuoYi-Vue3-FastAPI 目录上传到 /opt/ruoyi/
```

### 4.2 创建虚拟环境并安装依赖

```bash
cd /opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend

# 创建虚拟环境（Python 3.9）
python3.9 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate   # Linux
# .venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 五、环境变量配置

### 5.1 创建 .env.prod

```bash
cd /opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
cp .env.example .env.prod
vim .env.prod   # 或 nano / vi
```

### 5.2 .env.prod 完整示例（针对 106.53.217.96）

```ini
# -------- 应用配置 --------
APP_ENV = 'prod'
APP_NAME = 'RuoYi-FastAPI'
APP_ROOT_PATH = '/prod-api'
APP_HOST = '0.0.0.0'
APP_PORT = 9099
APP_VERSION = '1.8.1'
APP_RELOAD = false
APP_IP_LOCATION_QUERY = true
APP_SAME_TIME_LOGIN = true

# 学籍验证二维码/报告链接（必须设为服务器地址）
VERIFY_BASE_URL = "http://106.53.217.96"

# -------- Jwt配置 --------
# 务必修改为随机密钥！生成: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY = '你的64位十六进制密钥'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = 1440
JWT_REDIS_EXPIRE_MINUTES = 30

# -------- 数据库配置 --------
DB_TYPE = 'mysql'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USERNAME = 'ruoyi'
DB_PASSWORD = '你的数据库密码'
DB_DATABASE = 'ruoyi-fastapi'
DB_ECHO = false
DB_MAX_OVERFLOW = 10
DB_POOL_SIZE = 50
DB_POOL_RECYCLE = 3600
DB_POOL_TIMEOUT = 30

# -------- Redis配置 --------
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_USERNAME = ''
REDIS_PASSWORD = ''
REDIS_DATABASE = 2
```

**必须修改项：**

- `JWT_SECRET_KEY`：生产环境随机密钥
- `DB_PASSWORD`：数据库密码
- `REDIS_PASSWORD`：若 Redis 有密码则填写

---

## 六、启动后台（测试）

```bash
cd /opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
source .venv/bin/activate

# 使用 prod 环境启动
python app.py --env=prod
```

访问 `http://106.53.217.96:9099/prod-api/docs` 应能打开 Swagger 文档。确认无误后按 Ctrl+C 停止，继续配置 systemd。

---

## 七、systemd 服务（开机自启）

### 7.1 创建服务文件

```bash
sudo vim /etc/systemd/system/ruoyi-backend.service
```

### 7.2 服务配置内容

```ini
[Unit]
Description=RuoYi-FastAPI Backend
After=network.target mysql.service redis.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
Environment="PATH=/opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/.venv/bin"
Environment="APP_ENV=prod"
ExecStart=/opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/.venv/bin/python app.py --env=prod
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> 将 `User=root` 改为实际运行用户；路径按实际部署调整。

### 7.3 启用并启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable ruoyi-backend
sudo systemctl start ruoyi-backend
sudo systemctl status ruoyi-backend
```

### 7.4 常用命令

```bash
sudo systemctl restart ruoyi-backend   # 重启
sudo systemctl stop ruoyi-backend     # 停止
sudo journalctl -u ruoyi-backend -f   # 查看日志
```

---

## 八、Nginx 配置

### 8.1 创建站点配置

```bash
sudo vim /etc/nginx/conf.d/ruoyi.conf
```

### 8.2 配置内容（仅后台 API）

```nginx
server {
    listen 80;
    server_name 106.53.217.96;

    # 后端 API 代理
    location /prod-api/ {
        proxy_pass http://127.0.0.1:9099/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # 兼容 dev-api（若前端开发环境直连）
    location /dev-api/ {
        proxy_pass http://127.0.0.1:9099/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 8.3 若同时部署前端

```nginx
server {
    listen 80;
    server_name 106.53.217.96;

    # 前端静态资源
    location / {
        root /opt/ruoyi/ruoyi-frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /prod-api/ {
        proxy_pass http://127.0.0.1:9099/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    location /dev-api/ {
        proxy_pass http://127.0.0.1:9099/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 8.4 检查并重载 Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 九、验证部署

### 9.1 接口测试

```bash
# 健康检查（若有）
curl http://106.53.217.96/prod-api/

# 登录接口
curl -X POST http://106.53.217.96/prod-api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","code":"","uuid":""}'
```

### 9.2 学籍验证二维码

1. 登录管理后台，进入「学籍验证」
2. 下载某条记录的二维码
3. 扫码应跳转到 `http://106.53.217.96/verify?code=xxx`

---

## 十、目录与权限

```bash
# 确保上传目录可写（若使用文件上传）
mkdir -p /opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads
chmod -R 755 /opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads

# 学籍验证照片目录
mkdir -p /opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/photo
chmod -R 755 /opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads
```

---

## 十一、常见问题

| 问题 | 处理 |
|------|------|
| 502 Bad Gateway | 检查后端是否运行：`systemctl status ruoyi-backend` |
| 数据库连接失败 | 核对 `.env.prod` 中 DB_HOST、DB_USERNAME、DB_PASSWORD |
| Redis 连接失败 | 核对 REDIS_HOST、REDIS_PASSWORD，确认 Redis 已启动 |
| 二维码仍是 localhost | 检查 `VERIFY_BASE_URL` 是否为 `http://106.53.217.96` 并重启后端 |
| 端口 9099 被占用 | 修改 `.env.prod` 中 `APP_PORT` 和 Nginx 中 `proxy_pass` 端口 |

---

## 十二、一键部署脚本示例

```bash
#!/bin/bash
# deploy_backend.sh - 在服务器上执行

set -e
BACKEND_DIR="/opt/ruoyi/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend"
cd "$BACKEND_DIR"

source .venv/bin/activate
pip install -r requirements.txt -q
sudo systemctl restart ruoyi-backend
echo "Backend restarted."
```

保存为 `deploy_backend.sh`，`chmod +x deploy_backend.sh` 后执行即可用于快速更新部署。
