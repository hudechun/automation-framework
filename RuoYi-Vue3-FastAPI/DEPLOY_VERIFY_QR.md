# 学籍验证部署指南：二维码使用服务器地址

## 一、核心配置：`VERIFY_BASE_URL`

二维码和报告图中的链接由 **`VERIFY_BASE_URL`** 决定，需在部署时配置为**服务器对外可访问的地址**。

### 1. 配置方式

**方式 A：环境变量（推荐）**

```bash
export VERIFY_BASE_URL=http://192.168.1.100
# 或使用域名
export VERIFY_BASE_URL=https://your-domain.com
```

**方式 B：`.env` 文件**

在 `ruoyi-fastapi-backend/` 下的 `.env` 或 `.env.prod` 中：

```ini
# 学籍验证对外 H5 基础 URL（二维码、报告图链接前缀）
VERIFY_BASE_URL = http://192.168.1.100
```

> 注意：不要以 `/` 结尾，不要包含 `/verify` 路径。最终链接形如 `{VERIFY_BASE_URL}/verify?code=xxx`

### 2. 常见场景示例

| 部署方式 | VERIFY_BASE_URL 示例 |
|---------|---------------------|
| 内网 IP 访问 | `http://192.168.1.100` |
| 域名 + 80 端口 | `https://verify.example.com` |
| 域名 + 非 80 端口 | `http://192.168.1.100:8080` |
| Nginx 反向代理 | 与用户浏览器地址栏一致，如 `https://your-domain.com` |

---

## 二、部署步骤

### 1. 后端

1. 创建/编辑 `.env`：
   ```bash
   cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
   cp .env.example .env
   # 编辑 .env，设置：
   # VERIFY_BASE_URL = http://你的服务器IP或域名
   ```

2. 启动：
   ```bash
   python -m pip install -r requirements.txt
   python app.py
   # 或使用 uvicorn、gunicorn 等
   ```

### 2. 前端

1. 构建：
   ```bash
   cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
   npm run build
   ```

2. 将 `dist/` 部署到 Nginx 或其他 Web 服务器。

### 3. Nginx 示例（重要）

确保 `/verify` 路由到前端 SPA，API 代理到后端：

```nginx
server {
    listen 80;
    server_name 192.168.1.100;  # 或 your-domain.com

    # 前端静态资源
    location / {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /dev-api/ {
        proxy_pass http://127.0.0.1:9099/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 三、验证

1. 部署后，在管理端「学籍验证」列表点击某条记录的「二维码」下载。
2. 用手机扫码，应跳转到 `http://你的服务器IP/verify?code=xxx` 并正常显示验证报告。
3. 若仍跳 localhost，检查：
   - 后端 `.env` 中 `VERIFY_BASE_URL` 是否已修改
   - 是否重启了后端进程
   - 确认 pydantic-settings 正确加载了环境变量

---

## 四、Docker 部署

若使用 Docker，在 `docker-compose.yml` 或 `docker run` 中传入环境变量：

```yaml
environment:
  - VERIFY_BASE_URL=http://192.168.1.100
```

或在 `Dockerfile` 中：

```dockerfile
ENV VERIFY_BASE_URL=http://192.168.1.100
```
