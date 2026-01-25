# GitHub Skills 推荐

## 概述

GitHub Skills 是 GitHub Actions 的预构建工作流模板，可以帮助你快速设置 CI/CD、代码质量检查、自动化测试等。以下是一些优秀的 GitHub Skills 推荐。

## 核心开发技能

### 1. **Python 项目技能**

#### Python Lint
```yaml
- name: Python Lint
  uses: github/super-linter@v4
  env:
    DEFAULT_BRANCH: main
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    PYTHON_FILE_NAME: src/**/*.py
```

**推荐理由**：
- 自动检查 Python 代码风格（PEP 8）
- 支持多种 linter（pylint, flake8, black 等）
- 自动修复常见问题

#### Python Testing
```yaml
- name: Python Tests
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pytest tests/
```

**推荐理由**：
- 自动运行单元测试
- 生成测试覆盖率报告
- 支持多种测试框架

### 2. **前端项目技能**

#### Node.js CI
```yaml
- name: Node.js CI
  uses: actions/setup-node@v3
  with:
    node-version: '18'
- name: Install and Build
  run: |
    npm ci
    npm run build
```

**推荐理由**：
- 自动构建前端项目
- 运行前端测试
- 检查依赖安全

#### Vue.js 项目
```yaml
- name: Vue.js CI
  uses: actions/setup-node@v3
  with:
    node-version: '18'
- name: Build
  run: npm run build
- name: Test
  run: npm run test:unit
```

### 3. **代码质量检查**

#### CodeQL Analysis
```yaml
- name: CodeQL Analysis
  uses: github/codeql-action/init@v2
  with:
    languages: python, javascript
```

**推荐理由**：
- 自动检测安全漏洞
- 代码质量分析
- 免费使用

#### SonarCloud
```yaml
- name: SonarCloud Scan
  uses: SonarSource/sonarcloud-github-action@master
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**推荐理由**：
- 深度代码质量分析
- 技术债务追踪
- 代码覆盖率报告

### 4. **Docker 相关技能**

#### Docker Build and Push
```yaml
- name: Build and Push Docker Image
  uses: docker/build-push-action@v4
  with:
    context: .
    push: true
    tags: user/app:latest
```

**推荐理由**：
- 自动构建 Docker 镜像
- 推送到 Docker Hub 或 GitHub Container Registry
- 支持多平台构建

### 5. **数据库相关技能**

#### Database Migrations
```yaml
- name: Run Migrations
  run: |
    pip install alembic
    alembic upgrade head
```

**推荐理由**：
- 自动运行数据库迁移
- 确保数据库 schema 一致性
- 支持回滚

## 自动化测试技能

### 1. **自动化测试框架**

#### Playwright Tests
```yaml
- name: Playwright Tests
  uses: microsoft/playwright-github-action@v1
  with:
    browsers: chromium, firefox, webkit
```

**推荐理由**：
- 端到端测试
- 跨浏览器测试
- 自动截图和视频

#### Selenium Tests
```yaml
- name: Selenium Tests
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
- name: Install Dependencies
  run: |
    pip install selenium pytest
- name: Run Tests
  run: pytest tests/selenium/
```

### 2. **API 测试**

#### REST API Testing
```yaml
- name: API Tests
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
- name: Run API Tests
  run: |
    pip install pytest requests
    pytest tests/api/
```

## DevOps 技能

### 1. **部署技能**

#### Deploy to Server
```yaml
- name: Deploy
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.HOST }}
    username: ${{ secrets.USERNAME }}
    key: ${{ secrets.SSH_KEY }}
    script: |
      cd /app
      git pull
      docker-compose up -d --build
```

#### Deploy to Cloud
```yaml
- name: Deploy to AWS
  uses: aws-actions/configure-aws-credentials@v2
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1
```

### 2. **监控和通知**

#### Slack Notification
```yaml
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment completed!'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

#### Email Notification
```yaml
- name: Send Email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: 'Build Status'
    body: 'Build completed successfully!'
```

## 安全相关技能

### 1. **依赖安全检查**

#### Dependabot
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

**推荐理由**：
- 自动检查依赖安全漏洞
- 自动创建 PR 更新依赖
- 支持多种包管理器

#### Snyk Security Scan
```yaml
- name: Snyk Security Scan
  uses: snyk/actions/python@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

### 2. **密钥扫描**

#### Secret Scanning
```yaml
- name: Secret Scanning
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: ${{ github.event.repository.default_branch }}
    head: HEAD
```

## 文档生成技能

### 1. **API 文档**

#### Swagger/OpenAPI Docs
```yaml
- name: Generate API Docs
  run: |
    pip install fastapi[all]
    python -m fastapi docs
```

### 2. **代码文档**

#### Sphinx Documentation
```yaml
- name: Build Docs
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
- name: Build Sphinx Docs
  run: |
    pip install sphinx
    sphinx-build docs/ docs/_build/
```

## 性能测试技能

### 1. **负载测试**

#### k6 Load Testing
```yaml
- name: k6 Load Test
  uses: grafana/k6-action@v0.3.0
  with:
    filename: tests/load.js
```

### 2. **性能分析**

#### Lighthouse CI
```yaml
- name: Lighthouse CI
  uses: treosh/lighthouse-ci-action@v9
  with:
    urls: |
      https://example.com
    uploadArtifacts: true
```

## 推荐的工作流组合

### 完整的 CI/CD 流程

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Python Lint
        uses: github/super-linter@v4
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Run Tests
        run: |
          pip install -r requirements.txt
          pytest tests/
  
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: CodeQL Analysis
        uses: github/codeql-action/init@v2
        with:
          languages: python
  
  build:
    needs: [lint, test, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker Image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: false
          tags: app:latest
  
  deploy:
    needs: [build]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /app && docker-compose up -d --build
```

## 最佳实践

### 1. **使用缓存加速构建**

```yaml
- name: Cache Dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### 2. **并行执行任务**

```yaml
jobs:
  lint:
    # ...
  test:
    # ...
  security:
    # ...
```

### 3. **条件执行**

```yaml
- name: Deploy
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: ./deploy.sh
```

### 4. **使用矩阵策略**

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
    os: [ubuntu-latest, windows-latest, macos-latest]
```

## 有用的资源

### GitHub Actions 市场
- https://github.com/marketplace?type=actions

### 官方文档
- https://docs.github.com/en/actions

### 社区资源
- https://github.com/actions/starter-workflows

## 针对本项目的推荐

基于你的自动化平台项目，推荐以下技能：

1. **Python Lint & Test** - 确保代码质量
2. **Docker Build** - 自动化容器构建
3. **Database Migrations** - 自动运行数据库迁移
4. **API Testing** - 测试自动化框架的 API
5. **Security Scanning** - 检查依赖和代码安全
6. **Deployment Automation** - 自动部署到服务器

这些技能可以帮助你：
- 提高代码质量
- 自动化测试和部署
- 确保安全性
- 减少手动工作
