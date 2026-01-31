#!/usr/bin/env python3
"""
模板2 布局格式调整：教育部学历证书电子注册备案表

- 从样本图（yuanxing.jpg，已填写数据的样例）分析布局，输出 layout_config2.json。
- 支持 OCR 分析（pytesseract/EasyOCR）或使用内置默认坐标。
- 字段：更新日期、姓名、性别、出生日期、入学日期、毕（结）业日期、学校名称、专业、学制、
  层次、学历类别、学习形式、毕（结）业、证书编号、校（院）长姓名、在线验证码、照片、二维码。

用法:
  python scripts/report_layout_adjust_template2.py <样本图路径> [--output layout_config2.json]
  示例: python scripts/report_layout_adjust_template2.py RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/yuanxing.jpg -o RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/uploads/pic/layout_config2.json

  若样本图不存在，可用 --default 直接生成默认布局供手动调整:
  python scripts/report_layout_adjust_template2.py --default --template templete2.jpg -o layout_config2.json
"""

import argparse
import json
import sys
from pathlib import Path

# 模板2 字段名（教育部学历证书电子注册备案表）
FIELD_LABELS_TEMPLATE2 = [
    "更新日期",
    "姓名",
    "性别",
    "出生日期",
    "入学日期",
    "毕（结）业日期",
    "学校名称",
    "专业",
    "学制",
    "层次",
    "学历类别",
    "学习形式",
    "毕（结）业",
    "证书编号",
    "校（院）长姓名",
]

# 标签别名（OCR 可能识别为不同写法）
LABEL_ALIASES = {
    "毕（结）业日期": ["毕(结)业日期", "毕业日期", "结业日期"],
    "毕（结）业": ["毕(结)业", "毕业", "结业"],
    "校（院）长姓名": ["校(院)长姓名", "校长姓名", "院长姓名"],
}

# 默认布局（相对坐标 0~1，典型两栏：左标签右数据，照片右上，验证码区底部）
DEFAULT_IMAGE_SIZE = [595, 842]  # A4 比例常见尺寸
DEFAULT_UPDATE_DATE = [0.42, 0.14, 0.28, 0.032]
DEFAULT_PHOTO_REL = {"x_rel": 0.52, "y_rel": 0.14, "w_rel": 0.40, "h_rel": 0.32}
DEFAULT_QR_PLACEHOLDER = {"x_rel": 0.12, "y_rel": 0.77, "w_rel": 0.1152, "h_rel": 0.1152, "content": "https://www.chsi.com.cn/xlcx/rhsq.jsp", "fill": [248, 248, 248], "outline": [180, 180, 180]}
DEFAULT_VERIFICATION_CODE = [0.28, 0.73, 0.269, 0.026]

# 所有学生字段 X 轴对齐 x=0.27，整体上移一个汉字高度 (y - 0.015)
DEFAULT_FIELDS_LAYOUT = {
    "姓名": [0.27, 0.14, 0.12, 0.030],
    "性别": [0.27, 0.177, 0.08, 0.030],
    "出生日期": [0.27, 0.214, 0.22, 0.030],
    "入学日期": [0.27, 0.251, 0.22, 0.030],
    "毕（结）业日期": [0.27, 0.303, 0.22, 0.030],
    "学校名称": [0.27, 0.325, 0.32, 0.030],
    "专业": [0.27, 0.362, 0.18, 0.030],
    "学制": [0.27, 0.399, 0.08, 0.030],
    "层次": [0.27, 0.436, 0.10, 0.030],
    "学历类别": [0.27, 0.473, 0.22, 0.030],
    "学习形式": [0.27, 0.51, 0.18, 0.030],
    "毕（结）业": [0.27, 0.547, 0.10, 0.030],
    "证书编号": [0.27, 0.584, 0.30, 0.030],
    "校（院）长姓名": [0.27, 0.621, 0.12, 0.030],
}


def box_to_xywh(box):
    """OCR box 四点 -> (x, y, w, h) 像素."""
    pts = list(box)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (int(min(xs)), int(min(ys)), int(max(xs) - min(xs)), int(max(ys) - min(ys)))


def pixel_to_pt(height_px, dpi=96):
    return max(8, min(24, round(height_px * 72 / dpi)))


def _run_ocr_pytesseract(img_path: str):
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError("请安装: pip install pytesseract Pillow")
    img = Image.open(img_path)
    try:
        data = pytesseract.image_to_data(img, lang="chi_sim+eng", output_type=pytesseract.Output.DICT)
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError("未找到 Tesseract，请安装并加入 PATH")
    out = []
    for i in range(len(data["text"])):
        text = (data["text"][i] or "").strip()
        if not text:
            continue
        x, y = data["left"][i], data["top"][i]
        w, h = data["width"][i], data["height"][i]
        if w <= 0 or h <= 0:
            continue
        out.append((text, (x, y, w, h)))
    return out


def _run_ocr_easyocr(img_path: str):
    import easyocr
    reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
    result = reader.readtext(img_path)
    out = []
    for box, text, _ in result:
        x, y, w, h = box_to_xywh(box)
        out.append((str(text).strip(), (x, y, w, h)))
    return out


def run_ocr(img_path: str):
    try:
        return _run_ocr_pytesseract(img_path)
    except Exception as e1:
        try:
            print("pytesseract 不可用，尝试 EasyOCR:", e1, file=sys.stderr)
            return _run_ocr_easyocr(img_path)
        except Exception as e2:
            raise RuntimeError(f"OCR 失败: {e1}; {e2}") from e2


def _label_matches(ocr_text: str, label: str) -> bool:
    if label == ocr_text:
        return True
    for alias in LABEL_ALIASES.get(label, []):
        if alias == ocr_text or (len(ocr_text) <= 10 and alias in ocr_text):
            return True
    if len(ocr_text) <= 10 and label in ocr_text:
        return True
    return False


def _same_line(bbox_a, bbox_b, thresh=0.5):
    y1, h1 = bbox_a[1], bbox_a[3]
    y2, h2 = bbox_b[1], bbox_b[3]
    cy1, cy2 = y1 + h1 / 2, y2 + h2 / 2
    return abs(cy1 - cy2) <= max(h1, h2) * thresh


def find_label_value_pairs(ocr_items, img_w, img_h):
    """按「标签在左、数据在右」配对，支持模板2字段及别名。"""
    items = [(t, (x, y, w, h)) for t, (x, y, w, h) in ocr_items]
    if not items:
        return {}
    sorted_items = sorted(items, key=lambda x: (x[1][1] + x[1][3] / 2, x[1][0]))
    pairs = {}

    for label in FIELD_LABELS_TEMPLATE2:
        label_box = None
        value_candidate = None
        for text, bbox in sorted_items:
            if not _label_matches(text, label):
                continue
            lx, ly, lw, lh = bbox
            label_right = lx + lw
            for t2, b2 in sorted_items:
                if t2 == text and b2[0] == lx:
                    continue
                x2, y2, w2, h2 = b2
                if x2 < label_right:
                    continue
                if not _same_line(bbox, b2):
                    continue
                if t2 in FIELD_LABELS_TEMPLATE2 and t2 != label:
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


def build_config_from_ocr(pairs, img_w, img_h, ocr_items):
    """从 OCR 配对结果构建 layout_config 结构。"""
    default_pt = 12
    default_font = "SimSun"
    fields_out = {}

    for label in FIELD_LABELS_TEMPLATE2:
        if label == "更新日期":
            continue  # 单独处理 update_date
        p = pairs.get(label, {})
        value_bbox = p.get("value_bbox")
        value_text = p.get("value_text", "")
        if value_bbox:
            x, y, w, h = value_bbox
            font_size = pixel_to_pt(h)
            value_bbox_rel = [round(x / img_w, 4), round(y / img_h, 4), round(w / img_w, 4), round(h / img_h, 4)]
        else:
            font_size = default_pt
            value_bbox_rel = DEFAULT_FIELDS_LAYOUT.get(label)
        fields_out[label] = {
            "value_text": value_text,
            "value_bbox_rel": value_bbox_rel,
            "font_size": font_size,
            "font_family": default_font,
            "label_bbox": None,
            "value_bbox": None,
            "gap": p.get("gap", 0),
        }

    update_date = pairs.get("更新日期", {})
    if not update_date.get("value_bbox_rel"):
        vbr = update_date.get("value_bbox")
        if vbr:
            x, y, w, h = vbr
            update_date = {
                "value_text": update_date.get("value_text") or "2026年01月25日",
                "value_bbox_rel": [round(x / img_w, 4), round(y / img_h, 4), round(w / img_w, 4), round(h / img_h, 4)],
                "font_size": pixel_to_pt(h),
                "font_family": default_font,
                "fill": [100, 100, 100],
            }
        else:
            update_date = {
                "value_text": "2026年01月25日",
                "value_bbox_rel": DEFAULT_UPDATE_DATE,
                "font_size": default_pt,
                "font_family": default_font,
                "fill": [100, 100, 100],
            }
    else:
        update_date.setdefault("value_text", "2026年01月25日")
        update_date.setdefault("fill", [100, 100, 100])

    photo = {
        "x_rel": DEFAULT_PHOTO_REL["x_rel"],
        "y_rel": DEFAULT_PHOTO_REL["y_rel"],
        "w_rel": DEFAULT_PHOTO_REL["w_rel"],
        "h_rel": DEFAULT_PHOTO_REL["h_rel"],
    }

    return {
        "image_size": [img_w, img_h],
        "font_path": "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc",
        "font_family": "微软雅黑",
        "update_date": update_date,
        "fields": fields_out,
        "photo": photo,
        "qr_code_placeholder": DEFAULT_QR_PLACEHOLDER.copy(),
        "verification_code": {
            "value_bbox_rel": DEFAULT_VERIFICATION_CODE,
            "font_size": 9,
            "font_family": "黑体",
            "value_text": "0000000000000000",
        },
    }


def build_default_config(img_w: int, img_h: int):
    """生成默认布局配置（无 OCR）。"""
    default_pt = 12
    default_font = "SimSun"
    fields_out = {}
    for label in FIELD_LABELS_TEMPLATE2:
        if label == "更新日期":
            continue
        bbox = DEFAULT_FIELDS_LAYOUT.get(label)
        fields_out[label] = {
            "value_text": "",
            "value_bbox_rel": bbox,
            "font_size": default_pt,
            "font_family": default_font,
            "label_bbox": None,
            "value_bbox": None,
            "gap": 0,
        }
    return {
        "image_size": [img_w, img_h],
        "font_path": "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc",
        "font_family": "微软雅黑",
        "update_date": {
            "value_text": "2026年01月25日",
            "value_bbox_rel": DEFAULT_UPDATE_DATE,
            "font_size": default_pt,
            "font_family": default_font,
            "fill": [128, 128, 128],
        },
        "fields": fields_out,
        "photo": DEFAULT_PHOTO_REL.copy(),
        "qr_code_placeholder": DEFAULT_QR_PLACEHOLDER.copy(),
        "verification_code": {
            "value_bbox_rel": DEFAULT_VERIFICATION_CODE,
            "font_size": 9,
            "font_family": "黑体",
            "value_text": "0000000000000000",
        },
    }


def analyze(image_path: str, output_path: str | None = None, use_ocr: bool = True) -> str:
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"图片不存在: {image_path}")

    from PIL import Image
    with Image.open(image_path) as im:
        img_w, img_h = im.size

    if use_ocr:
        try:
            ocr_items = run_ocr(str(image_path))
            pairs = find_label_value_pairs(ocr_items, img_w, img_h)
            config = build_config_from_ocr(pairs, img_w, img_h, ocr_items)
        except Exception as e:
            print(f"OCR 失败，使用默认布局: {e}", file=sys.stderr)
            config = build_default_config(img_w, img_h)
    else:
        config = build_default_config(img_w, img_h)

    out = Path(output_path) if output_path else image_path.parent / "layout_config2.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return str(out)


def main():
    parser = argparse.ArgumentParser(description="模板2（学历证书电子注册备案表）布局格式调整")
    parser.add_argument("image", nargs="?", default=None, help="样本图路径，如 yuanxing.jpg")
    parser.add_argument("--output", "-o", default=None, help="输出 layout_config2.json 路径")
    parser.add_argument("--default", action="store_true", help="不使用 OCR，直接生成默认布局")
    parser.add_argument("--template", "-t", default=None, help="与 --default 联用：指定空白模板路径以获取尺寸")
    args = parser.parse_args()

    if args.default:
        if args.template:
            tpl = Path(args.template)
            if not tpl.exists():
                print(f"模板不存在: {tpl}", file=sys.stderr)
                sys.exit(1)
            from PIL import Image
            with Image.open(tpl) as im:
                w, h = im.size
        else:
            w, h = DEFAULT_IMAGE_SIZE
        config = build_default_config(w, h)
        out = Path(args.output or "layout_config2.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"已生成默认布局配置: {out}")
        return

    if not args.image:
        print("请提供样本图路径，或使用 --default 生成默认布局", file=sys.stderr)
        sys.exit(1)

    try:
        path = analyze(args.image, args.output, use_ocr=not args.default)
        print(f"已保存布局配置: {path}")
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
