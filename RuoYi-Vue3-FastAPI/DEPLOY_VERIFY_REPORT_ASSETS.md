# 学籍验证报告资源部署说明

报告生成依赖以下文件，因 .gitignore 忽略，**需手动上传到服务器**。

## 一、需要部署的文件

| 本地路径 | 服务器路径 |
|---------|-----------|
| `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/templete.png` | `{backend目录}/uploads/pic/templete.png` |
| `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/layout_config.json` | `{backend目录}/uploads/pic/layout_config.json` |
| `scripts/report_fill_from_ai.py` | `{项目根}/scripts/report_fill_from_ai.py` |
| `scripts/requirements-report.txt`（若脚本需额外依赖） | `{项目根}/scripts/` |

**路径说明**：
- `{backend目录}` = `ruoyi-fastapi-backend` 所在目录，如 `/home/ruoyi/automation-framework/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend`
- `{项目根}` = `automation-framework` 或 `AutoFlow-Platform` 根目录，即 backend 的上一级的上一级

## 二、快速上传命令（在本地执行）

```bash
# 替换为你的服务器地址和路径
SERVER="root@106.53.217.96"
BACKEND="/home/ruoyi/automation-framework/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend"
ROOT="/home/ruoyi/automation-framework"

# 创建目录
ssh $SERVER "mkdir -p $BACKEND/uploads/pic/photo $ROOT/scripts"

# 上传报告模板和配置
scp RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/templete.png $SERVER:$BACKEND/uploads/pic/
scp RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/layout_config.json $SERVER:$BACKEND/uploads/pic/

# 上传报告填充脚本
scp scripts/report_fill_from_ai.py $SERVER:$ROOT/scripts/
scp scripts/requirements-report.txt $SERVER:$ROOT/scripts/ 2>/dev/null || true
```

## 三、服务器上安装脚本依赖与中文字体

### 3.1 Python 依赖

```bash
cd /home/ruoyi/automation-framework/scripts
pip install Pillow qrcode
# 或若有 requirements-report.txt: pip install -r requirements-report.txt
```

### 3.2 中文字体（必装，否则报告中文会乱码）

```bash
# CentOS 7 安装文泉驿正黑
yum install -y wqy-zenhei-fonts

# 验证字体存在
ls /usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc
# 或
ls /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
```

若无法安装 wqy-zenhei，可尝试 Google Noto 字体：

```bash
yum install -y google-noto-sans-cjk-fonts
```

## 四、验证

在服务器上执行：

```bash
ls -la /home/ruoyi/automation-framework/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/
# 应看到 templete.png 和 layout_config.json

ls -la /home/ruoyi/automation-framework/scripts/report_fill_from_ai.py
# 应存在
```

## 五、中文乱码排查

若报告中文显示为方块或乱码，说明未找到中文字体。请确认：

1. 已安装 `wqy-zenhei-fonts` 或 `google-noto-sans-cjk-fonts`
2. 已重新上传最新的 `report_fill_from_ai.py`（含更多 Linux 字体回退路径）
3. 手动测试：`cd scripts && python report_fill_from_ai.py --template ../RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/templete.png --config ../RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/layout_config.json --data 姓名=测试 --output /tmp/test.png`
