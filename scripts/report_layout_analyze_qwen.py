#!/usr/bin/env python3
"""
第二方案：用 Qwen3-VL 视觉模型分析学籍报告样本图，输出 layout_config.json。

- 调用阿里云 DashScope（OpenAI 兼容）Qwen3-VL，传图 + 提示词，要求返回各字段取值及相对位置。
- API Key 从环境变量 QWEN_API_KEY 或 DASHSCOPE_API_KEY 读取，请勿写入代码或提交仓库。
- 若模型未返回 bbox，使用内置默认布局（典型学籍报告相对坐标），仍可被 report_fill_template 使用。

依赖: pip install openai Pillow
用法: set QWEN_API_KEY=sk-xxx && python scripts/report_layout_analyze_qwen.py <yuanxing.png> [--output layout_config.json]
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

# 学籍报告字段名，与 report_layout_analyze.py 一致
FIELD_LABELS = [
    "更新日期",
    "姓名",
    "性别",
    "出生日期",
    "民族",
    "学校名称",
    "层次",
    "专业",
    "学制",
    "学历类别",
    "分院",
    "系所",
    "入学日期",
    "学籍状态",
    "预计毕业日期",
]

# 默认相片区域（相对 0~1）
DEFAULT_PHOTO_REL = {"x": 0.55, "y": 0.12, "w": 0.37, "h": 0.26}

# 默认各字段“数据”区域相对坐标 [x, y, w, h]，用于 VL 未返回 bbox 时（典型两栏布局）
DEFAULT_FIELDS_LAYOUT = {
    "更新日期": [0.35, 0.07, 0.30, 0.04],
    "姓名": [0.42, 0.16, 0.15, 0.03],
    "性别": [0.42, 0.20, 0.08, 0.03],
    "出生日期": [0.42, 0.24, 0.25, 0.03],
    "民族": [0.42, 0.28, 0.12, 0.03],
    "学校名称": [0.42, 0.32, 0.35, 0.03],
    "层次": [0.42, 0.36, 0.08, 0.03],
    "专业": [0.42, 0.40, 0.20, 0.03],
    "学制": [0.42, 0.44, 0.08, 0.03],
    "学历类别": [0.42, 0.48, 0.25, 0.03],
    "分院": [0.42, 0.52, 0.20, 0.03],
    "系所": [0.42, 0.56, 0.25, 0.03],
    "入学日期": [0.42, 0.60, 0.25, 0.03],
    "学籍状态": [0.42, 0.64, 0.12, 0.03],
    "预计毕业日期": [0.42, 0.68, 0.25, 0.03],
}

PROMPT = """这是一张「教育部学籍在线验证报告」样本图。请严格按以下要求返回一个 JSON（不要 markdown 包裹，不要其它说明）：

1. 从图中识别并列出以下字段的**填写值**（即标签右侧的内容）：
更新日期、姓名、性别、出生日期、民族、学校名称、层次、专业、学制、学历类别、分院、系所、入学日期、学籍状态、预计毕业日期。
若某字段图中无内容则填空字符串。

2. 为每个字段估计其填写值在图片中的相对位置，用矩形表示，范围 0~1：value_bbox_rel 为 [x, y, w, h]，其中 x,y 为左上角相对整图宽高的比例，w,h 为宽高比例。若无法估计可省略该字段的 value_bbox_rel。

3. 估计右上角「照片」区域的相对矩形：photo 为 { "x": 0~1, "y": 0~1, "w": 0~1, "h": 0~1 }。

返回格式示例（仅作结构参考，请按实际识别结果填写）：
{
  "fields": [
    { "name": "更新日期", "value": "2026年01月29日", "value_bbox_rel": [0.35, 0.07, 0.30, 0.04] },
    { "name": "姓名", "value": "张三", "value_bbox_rel": [0.42, 0.16, 0.15, 0.03] }
  ],
  "photo": { "x": 0.55, "y": 0.12, "w": 0.37, "h": 0.26 }
}

请只输出上述 JSON，不要 ```json 等标记。"""


def get_api_key(api_key_override: str | None = None) -> str:
    key = (api_key_override or os.environ.get("QWEN_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")) or ""
    key = key.strip()
    if not key:
        raise RuntimeError(
            "未设置 API Key。请设置环境变量 QWEN_API_KEY，或使用 --api-key 传入；勿将 Key 提交仓库。"
        )
    return key


def image_to_base64_data_url(img_path: str, max_size: int = 2048) -> str:
    """将图片转为 base64 data URL；过大会先缩放以节省 token。"""
    from PIL import Image
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def call_qwen_vl(api_key: str, image_url: str, prompt: str, base_url: str, model: str):
    """调用 Qwen3-VL 视觉接口，返回 content 文本。"""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("请安装: pip install openai")
    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        max_tokens=2048,
    )
    if not resp.choices:
        raise RuntimeError("Qwen3-VL 未返回内容")
    return (resp.choices[0].message.content or "").strip()


def parse_json_from_response(text: str) -> dict:
    """从模型输出中截取 JSON（允许被 markdown 包裹）。"""
    text = text.strip()
    # 去掉 ```json ... ``` 包裹
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        text = m.group(1).strip()
    return json.loads(text)


def build_layout_config(parsed: dict, img_w: int, img_h: int) -> dict:
    """将 VL 返回的 JSON 转为与 report_layout_analyze 一致的 layout_config 结构。"""
    default_font = "SimSun"
    default_pt = 12

    fields_out = {}
    field_list = parsed.get("fields") or []
    for item in field_list:
        name = item.get("name") or ""
        if name not in FIELD_LABELS:
            continue
        value = item.get("value") or ""
        bbox_rel = item.get("value_bbox_rel")
        if not bbox_rel and name in DEFAULT_FIELDS_LAYOUT:
            bbox_rel = DEFAULT_FIELDS_LAYOUT[name]
        if bbox_rel and len(bbox_rel) >= 4:
            bbox_rel = [round(float(bbox_rel[i]), 4) for i in range(4)]
        fields_out[name] = {
            "value_text": value,
            "value_bbox_rel": bbox_rel,
            "font_size": default_pt,
            "font_family": default_font,
            "label_bbox": None,
            "value_bbox": None,
            "gap": 0,
        }

    # 补全未出现在 VL 返回中的字段
    for name in FIELD_LABELS:
        if name == "更新日期":
            continue
        if name not in fields_out:
            fields_out[name] = {
                "value_text": "",
                "value_bbox_rel": DEFAULT_FIELDS_LAYOUT.get(name),
                "font_size": default_pt,
                "font_family": default_font,
                "label_bbox": None,
                "value_bbox": None,
                "gap": 0,
            }

    # 更新日期
    update_date = {"font_size": default_pt, "font_family": default_font, "value_bbox": None, "gap": 0}
    for item in field_list:
        if (item.get("name") or "") == "更新日期":
            update_date["value_text"] = item.get("value") or ""
            update_date["value_bbox_rel"] = item.get("value_bbox_rel") or DEFAULT_FIELDS_LAYOUT.get("更新日期")
            break
    else:
        update_date["value_text"] = ""
        update_date["value_bbox_rel"] = DEFAULT_FIELDS_LAYOUT.get("更新日期")

    # 照片区域
    photo = parsed.get("photo") or {}
    photo_rel = {
        "x_rel": round(float(photo.get("x", DEFAULT_PHOTO_REL["x"])), 4),
        "y_rel": round(float(photo.get("y", DEFAULT_PHOTO_REL["y"])), 4),
        "w_rel": round(float(photo.get("w", DEFAULT_PHOTO_REL["w"])), 4),
        "h_rel": round(float(photo.get("h", DEFAULT_PHOTO_REL["h"])), 4),
    }
    photo_rel["x"] = int(photo_rel["x_rel"] * img_w)
    photo_rel["y"] = int(photo_rel["y_rel"] * img_h)
    photo_rel["w"] = int(photo_rel["w_rel"] * img_w)
    photo_rel["h"] = int(photo_rel["h_rel"] * img_h)

    return {
        "image_size": [img_w, img_h],
        "update_date": update_date,
        "fields": fields_out,
        "photo": photo_rel,
    }


def analyze(img_path: str, output_path: str | None = None, base_url: str | None = None, model: str = "qwen-vl-plus", api_key: str | None = None) -> str:
    api_key = get_api_key(api_key)
    img_path = Path(img_path)
    if not img_path.exists():
        raise FileNotFoundError(f"图片不存在: {img_path}")
    from PIL import Image
    with Image.open(img_path) as im:
        img_w, img_h = im.size
    base_url = base_url or os.environ.get("QWEN_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
    image_url = image_to_base64_data_url(str(img_path))
    text = call_qwen_vl(api_key, image_url, PROMPT, base_url, model)
    try:
        parsed = parse_json_from_response(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Qwen3-VL 返回内容无法解析为 JSON: {e}\n 返回片段: {text[:500]}") from e
    config = build_layout_config(parsed, img_w, img_h)
    out = Path(output_path) if output_path else img_path.parent / "layout_config.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return str(out)


def main():
    parser = argparse.ArgumentParser(description="学籍报告样本图布局分析（Qwen3-VL 方案）")
    parser.add_argument("image", help="样本图路径，如 yuanxing.png")
    parser.add_argument("--output", "-o", default=None, help="输出 JSON 路径")
    parser.add_argument("--api-key", "-k", default=None, help="Qwen/DashScope API Key（也可用环境变量 QWEN_API_KEY）")
    parser.add_argument("--base-url", default=None, help="API base_url，默认 DashScope 兼容地址")
    parser.add_argument("--model", default="qwen-vl-plus", help="模型名，如 qwen-vl-plus / qwen2-vl-7b-instruct")
    args = parser.parse_args()
    try:
        path = analyze(args.image, args.output, args.base_url, args.model, args.api_key)
        print(f"已保存布局配置: {path}")
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
