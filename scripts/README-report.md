# 学籍验证报告图片填充

## 依赖

```bash
pip install -r scripts/requirements-report.txt
```

**阶段一有两种方式：**

- **方式 A（OCR）**：`report_layout_analyze.py`，使用 pytesseract。需本机安装 [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki) 及中文包 chi_sim 并加入 PATH。
- **方式 B（Qwen3-VL）**：`report_layout_analyze_qwen.py`，调用阿里云 DashScope Qwen3-VL 视觉模型，无需 Tesseract。需设置环境变量 **QWEN_API_KEY**（或 DASHSCOPE_API_KEY），**请勿将 Key 写入代码或提交仓库**。

## 阶段一：分析样本图，生成布局配置

对已填好的样本图（如 `yuanxing.png`）分析，得到各字段位置及相片区域，保存为 `layout_config.json`。

**方式 A（OCR，pytesseract）：**
```bash
python scripts/report_layout_analyze.py RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/yuanxing.png --output RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/layout_config.json
```

**方式 B（Qwen3-VL 视觉模型）：** 需先设置 API Key（勿提交到仓库）。
```bash
set QWEN_API_KEY=sk-你的密钥
python scripts/report_layout_analyze_qwen.py RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/yuanxing.png --output RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/layout_config.json
```
可选：`--model qwen-vl-plus`（默认）、`--base-url <自定义 base_url>`。

## 阶段二：按配置填充空白模板

**推荐：AI 方案专用脚本**（处理 report_layout_analyze_qwen.py 的输出，避免重复绘制、坐标越界）

```bash
python scripts/report_fill_from_ai.py --template RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/templete.png --photo RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/photo.png --config RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/layout_config.json --output RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/result.png
```

- 不传 `--data-json` / `--data` 时，使用 config 里 AI 识别的 **value_text** 填充。
- 传 `--data-json` 或 `--data` 时，用你提供的数据覆盖对应字段。

**通用脚本**（也支持 OCR 生成的 config）：

```bash
python scripts/report_fill_template.py -t uploads/pic/templete.png -p uploads/pic/photo.png -c uploads/pic/layout_config.json --data-json scripts/sample_report_data.json -o uploads/pic/result.png
```

## 字体

默认使用系统宋体（Windows `simsun.ttc`）。若路径不同，可用 `--font` 指定：

```bash
python scripts/report_fill_template.py ... --font C:/Windows/Fonts/simsun.ttc
```
