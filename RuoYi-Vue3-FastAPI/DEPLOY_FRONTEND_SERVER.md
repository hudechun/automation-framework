# 前端部署指南（服务器 106.53.217.96）

本文档描述在已部署后端、已安装 Nginx 的服务器上部署 RuoYi-Vue3 前端的流程。

---

## 一、前置条件

- 后端已部署并运行（9099 端口）
- Nginx 已安装
- Node.js 16+ 已安装（用于本地或服务器构建）

---

## 二、构建前端

### 方式 A：本地构建后上传（推荐）

在本地（Windows）执行：

```bash
cd d:\AUTO-PC\AutoFlow-Platform\RuoYi-Vue3-FastAPI\ruoyi-fastapi-frontend

# 安装依赖（若未安装）
npm install --registry=https://registry.npmmirror.com

# 使用生产环境配置构建
npm run build
```

构建完成后，`dist/` 目录即为静态资源。

### 方式 B：在服务器上构建

在服务器上（需已安装 Node.js）：

```bash
cd /home/ruoyi/automation-framework/RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend

# 安装依赖
npm install --registry=https://registry.npmmirror.com

# 构建
npm run build
```

---

## 三、上传 dist 到服务器

### 本地构建后上传

```bash
# 方式 1：scp
scp -r dist/* root@106.53.217.96:/opt/ruoyi/ruoyi-frontend/dist/

# 方式 2：rsync
rsync -avz --delete dist/ root@106.53.217.96:/opt/ruoyi/ruoyi-frontend/dist/
```

**需先在服务器创建目录：**

```bash
ssh root@106.53.217.96 "mkdir -p /opt/ruoyi/ruoyi-frontend/dist"
```

---

## 四、Nginx 配置

### 4.1 创建或编辑站点配置

```bash
sudo vim /etc/nginx/conf.d/ruoyi.conf
```

### 4.2 完整配置（前端 + 后端代理）

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

    # 后端 API（与后端部署指南一致）
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

### 4.3 若前端目录不同

若 dist 放在其他路径，修改 `root` 为实际路径，例如：

- `/home/ruoyi/automation-framework/RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend/dist`

### 4.4 检查并重载 Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 五、验证

1. 访问：http://106.53.217.96
2. 应看到登录页
3. 使用默认账号登录：admin / admin123
4. 学籍验证二维码扫码应跳转到 http://106.53.217.96/verify?code=xxx

---

## 六、生产环境变量说明

构建时使用 `.env.production`：

| 变量 | 说明 | 当前值 |
|------|------|--------|
| VITE_APP_BASE_API | API 基础路径 | `/prod-api` |
| VITE_APP_ENV | 环境 | `production` |

API 请求会发往：`当前域名 + /prod-api`，即 `http://106.53.217.96/prod-api/xxx`，由 Nginx 代理到后端 9099。

---

## 七、一键部署脚本示例

**本地执行（构建 + 上传）：**

```bash
# deploy_frontend.sh
cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
npm run build
rsync -avz --delete dist/ root@106.53.217.96:/opt/ruoyi/ruoyi-frontend/dist/
echo "前端部署完成，请访问 http://106.53.217.96"
```

**服务器执行（若在服务器构建）：**

```bash
# deploy_frontend_server.sh
cd /home/ruoyi/automation-framework/RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
git pull
npm install --registry=https://registry.npmmirror.com
npm run build
echo "构建完成，dist 已在当前目录，Nginx 已配置指向该路径则无需额外操作"
```

---

## 八、常见问题

| 问题 | 处理 |
|------|------|
| 白屏 | 检查 dist 是否上传成功，Nginx root 路径是否正确 |
| 404 | 确保 `try_files $uri $uri/ /index.html` 存在，用于 SPA 路由 |
| 接口 404 | 检查 Nginx 中 `/prod-api/` 是否代理到 127.0.0.1:9099 |
| 跨域 | 前端使用 /prod-api 同源，无跨域；后端 CORS 已配置 |
