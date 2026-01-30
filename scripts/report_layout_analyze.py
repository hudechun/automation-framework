#!/usr/bin/env python3
"""
阶段一：从样本图（如 yuanxing.png）分析布局，保存为 layout_config.json。

- 使用 EasyOCR 检测+识别所有文本框，得到内容与外接矩形（避免 PaddleOCR 依赖哈希问题）。
- 预定义字段名列表，按「标签在左、数据在右」配对，计算 value_bbox、font_size、gap。
- 相片区域：取右上角不含文字的大矩形（或使用相对坐标默认值）。
- 输出 JSON 含 fields、update_date、photo；坐标同时保存像素与相对 0~1，便于模板尺寸变化。

依赖: pip install -r scripts/requirements-report.txt
用法: python scripts/report_layout_analyze.py <yuanxing.png> [--output layout_config.json]
"""

import argparse
import json
import sys
from pathlib import Path

# 学籍报告字段名（标签），与样本图一致
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

# 默认相片区域（相对 0~1），样本图若无文字块可据此标定
DEFAULT_PHOTO_REL = {"x": 0.55, "y": 0.12, "w": 0.37, "h": 0.26}


def box_to_xywh(box):
    """OCR box 四点 [[x,y],...] -> (x, y, w, h) 像素."""
    pts = list(box)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (int(min(xs)), int(min(ys)), int(max(xs) - min(xs)), int(max(ys) - min(ys)))


def pixel_to_pt(height_px, dpi=96):
    """像素高度 -> 近似字号(pt). 常见 96 DPI 下 高度≈字号*1.33."""
    return max(8, min(24, round(height_px * 72 / dpi)))


def _run_ocr_easyocr(img_path: str):
    """EasyOCR，返回 [(text, (x,y,w,h)), ...]。若遇 PyTorch DLL 错误则抛异常由上层回退。"""
    import easyocr
    reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
    result = reader.readtext(img_path)
    out = []
    for box, text, _ in result:
        x, y, w, h = box_to_xywh(box)
        out.append((str(text).strip(), (x, y, w, h)))
    return out


def _run_ocr_pytesseract(img_path: str):
    """pytesseract（需本机安装 Tesseract-OCR 及 chi_sim），返回 [(text, (x,y,w,h)), ...]。"""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError("请安装: pip install pytesseract Pillow；并安装 Tesseract-OCR 与中文语言包 chi_sim")
    img = Image.open(img_path)
    try:
        data = pytesseract.image_to_data(img, lang="chi_sim+eng", output_type=pytesseract.Output.DICT)
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError("未找到 Tesseract，请安装并加入 PATH：https://github.com/UB-Mannheim/tesseract/wiki")
    out = []
    for i in range(len(data["text"])):
        text = (data["text"][i] or "").strip()
        if not text:
            continue
        x = data["left"][i]
        y = data["top"][i]
        w = data["width"][i]
        h = data["height"][i]
        if w <= 0 or h <= 0:
            continue
        out.append((text, (x, y, w, h)))
    return out


def run_ocr(img_path: str):
    """OCR：优先 pytesseract（无 PyTorch，免 DLL 问题）；不可用时再试 EasyOCR。返回 [(text, (x,y,w,h)), ...]。"""
    try:
        return _run_ocr_pytesseract(img_path)
    except Exception as e1:
        try:
            import sys
            print("pytesseract 不可用，尝试 EasyOCR：", e1, file=sys.stderr)
            return _run_ocr_easyocr(img_path)
        except Exception as e2:
            raise RuntimeError(
                "OCR 失败。建议：1) pip install pytesseract  2) 安装 Tesseract-OCR 并勾选中文、加入 PATH。"
                f" 错误: {e1}; {e2}"
            ) from e2


def _same_line(bbox_a, bbox_b, thresh=0.5):
    """两框 y 重叠超过 thresh 视为同一行."""
    y1, h1 = bbox_a[1], bbox_a[3]
    y2, h2 = bbox_b[1], bbox_b[3]
    cy1, cy2 = y1 + h1 / 2, y2 + h2 / 2
    return abs(cy1 - cy2) <= max(h1, h2) * thresh


def find_label_value_pairs(ocr_items, img_w, img_h):
    """
    按「标签在左、数据在右」配对。OCR 项为 (text, (x,y,w,h))。
    返回 { label_text: { "label_bbox": [x,y,w,h], "value_bbox": [x,y,w,h]|None, "value_text": str, "gap": int } }
    """
    items = [(t, (x, y, w, h)) for t, (x, y, w, h) in ocr_items]
    if not items:
        return {}

    # 按 (y 中心, x) 排序，便于按行扫描
    sorted_items = sorted(items, key=lambda x: (x[1][1] + x[1][3] / 2, x[1][0]))

    pairs = {}
    for label in FIELD_LABELS:
        label_box = None
        value_candidate = None
        for text, bbox in sorted_items:
            if not (label == text or (len(text) <= 8 and label in text)):
                continue
            lx, ly, lw, lh = bbox
            label_right = lx + lw
            # 同一行右侧最近的非标签块作为 value
            for t2, b2 in sorted_items:
                if t2 == text and b2[0] == lx:
                    continue
                x2, y2, w2, h2 = b2
                if x2 < label_right:
                    continue
                if not _same_line(bbox, b2):
                    continue
                # 避免把其他标签当 value（如「性别」右侧才是「女」）
                if t2 in FIELD_LABELS and t2 != label:
                    continue
                value_candidate = (t2, b2)
                break
            label_box = bbox
            break

        if label_box is not None:
            lx, ly, lw, lh = label_box
            if value_candidate:
                vt, vbox = value_candidate
                gap = vbox[0] - (lx + lw)
                pairs[label] = {
                    "label_bbox": list(label_box),
                    "value_bbox": list(vbox),
                    "value_text": vt,
                    "gap": max(0, int(gap)),
                }
            else:
                pairs[label] = {
                    "label_bbox": list(label_box),
                    "value_bbox": None,
                    "value_text": "",
                    "gap": 0,
                }
    return pairs


def compute_font_size_and_save(pairs, img_w, img_h, default_font="SimSun"):
    """根据 value_bbox 高度算 font_size(pt)，并补全相对坐标、font_family."""
    default_pt = 12
    for label, p in pairs.items():
        p["font_family"] = default_font
        if p.get("value_bbox"):
            x, y, w, h = p["value_bbox"]
            p["font_size"] = pixel_to_pt(h)
            p["value_bbox_rel"] = [round(x / img_w, 4), round(y / img_h, 4), round(w / img_w, 4), round(h / img_h, 4)]
        else:
            p["font_size"] = default_pt
            p["value_bbox_rel"] = None
        if p.get("label_bbox"):
            x, y, w, h = p["label_bbox"]
            p["label_bbox_rel"] = [round(x / img_w, 4), round(y / img_h, 4), round(w / img_w, 4), round(h / img_h, 4)]
    return pairs


def detect_photo_region(ocr_items, img_w, img_h):
    """右上角大块无文字区域作为相片框。若有 OCR 框则取右上角最大空白矩形近似."""
    # 简单策略：右上角固定比例
    x = int(DEFAULT_PHOTO_REL["x"] * img_w)
    y = int(DEFAULT_PHOTO_REL["y"] * img_h)
    w = int(DEFAULT_PHOTO_REL["w"] * img_w)
    h = int(DEFAULT_PHOTO_REL["h"] * img_h)
    return {
        "x": x, "y": y, "w": w, "h": h,
        "x_rel": round(x / img_w, 4), "y_rel": round(y / img_h, 4),
        "w_rel": round(w / img_w, 4), "h_rel": round(h / img_h, 4),
    }


def analyze(img_path: str, output_path: str | None = None) -> str:
    img_path = Path(img_path)
    if not img_path.exists():
        raise FileNotFoundError(f"图片不存在: {img_path}")
    try:
        from PIL import Image
        with Image.open(img_path) as im:
            img_w, img_h = im.size
    except Exception as e:
        raise RuntimeError(f"无法读取图片尺寸: {e}") from e

    ocr_items = run_ocr(str(img_path))
    pairs = find_label_value_pairs(ocr_items, img_w, img_h)
    compute_font_size_and_save(pairs, img_w, img_h)
    photo = detect_photo_region(ocr_items, img_w, img_h)

    # 更新日期单独（若在 FIELD_LABELS 里已配对则复用）
    update_date = pairs.get("更新日期", {})
    if not update_date and "更新日期" in FIELD_LABELS:
        update_date = {"value_bbox": None, "font_size": 12, "gap": 0, "font_family": "SimSun", "value_bbox_rel": None}

    config = {
        "image_size": [img_w, img_h],
        "update_date": update_date,
        "fields": {k: v for k, v in pairs.items() if k != "更新日期"},
        "photo": photo,
    }

    out = Path(output_path) if output_path else img_path.parent / "layout_config.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return str(out)


def main():
    parser = argparse.ArgumentParser(description="学籍报告样本图布局分析，输出 layout_config.json")
    parser.add_argument("image", help="样本图路径，如 yuanxing.png")
    parser.add_argument("--output", "-o", default=None, help="输出 JSON 路径，默认与图片同目录 layout_config.json")
    args = parser.parse_args()
    try:
        path = analyze(args.image, args.output)
        print(f"已保存布局配置: {path}")
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
