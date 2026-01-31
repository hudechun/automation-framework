#!/usr/bin/env python3
"""
模板2 专用：教育部学历证书电子注册备案表 填充脚本。

- 使用 layout_config2.json、templete2.jpg，与 report_fill_from_ai.py（模板1）完全独立。
- 字段：更新日期、姓名、性别、出生日期、入学日期、毕（结）业日期、学校名称、专业、学制、
  层次、学历类别、学习形式、毕（结）业、证书编号、校（院）长姓名、在线验证码、照片、二维码。

依赖: Pillow, qrcode
用法:
  python scripts/report_fill_template2.py -t uploads/pic/templete2.jpg -c uploads/pic/layout_config2.json [--photo photo.png] [--output result.png]
  --data-json scripts/sample_report_data_template2.json 或 --data 姓名=xxx ...
"""

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

DEFAULT_FONT_PATHS = [
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]

FONT_FAMILY_PATHS = {
    "SimSun": "C:/Windows/Fonts/simsun.ttc",
    "宋体": "C:/Windows/Fonts/simsun.ttc",
    "SimHei": "C:/Windows/Fonts/simhei.ttf",
    "黑体": "C:/Windows/Fonts/simhei.ttf",
    "微软雅黑": "C:/Windows/Fonts/msyh.ttc",
}

# 模板2 跳过的字段（更新日期单独绘制）
SKIP_FIELD_NAMES = {"更新日期"}

DEFAULT_PHOTO_REL = {"x_rel": 0.52, "y_rel": 0.14, "w_rel": 0.40, "h_rel": 0.32}
PHOTO_SCALE = 0.25


def resolve_font_path(config: dict, font_path_arg: str | None) -> str | None:
    if font_path_arg and Path(font_path_arg).exists():
        return font_path_arg
    path = config.get("font_path")
    if path and Path(path).exists():
        return path
    name = config.get("font_family")
    if name and name in FONT_FAMILY_PATHS and Path(FONT_FAMILY_PATHS[name]).exists():
        return FONT_FAMILY_PATHS[name]
    for p in DEFAULT_FONT_PATHS:
        if p and Path(p).exists():
            return p
    return None


def get_font(font_path: str | None, size_pt: int):
    size_pt = max(8, min(24, int(size_pt)))
    paths = [font_path] if font_path else DEFAULT_FONT_PATHS
    for p in paths:
        if p and Path(p).exists():
            try:
                return ImageFont.truetype(p, size_pt)
            except Exception:
                continue
    return ImageFont.load_default()


def clamp_rel(rel: list) -> list:
    if not rel or len(rel) < 4:
        return rel or []
    x, y, w, h = max(0, min(1, float(rel[0]))), max(0, min(1, float(rel[1]))), max(0.01, float(rel[2])), max(0.01, float(rel[3]))
    return [round(x, 4), round(y, 4), round(min(w, 1 - x), 4), round(min(h, 1 - y), 4)]


def rel_to_pixel(rel: list | None, tw: int, th: int) -> tuple | None:
    if not rel or len(rel) < 4:
        return None
    rel = clamp_rel(rel)
    return (int(rel[0] * tw), int(rel[1] * th), int(rel[2] * tw), int(rel[3] * th))


def _parse_fill(cfg: dict | None) -> tuple:
    if not cfg:
        return (0, 0, 0)
    raw = cfg.get("fill")
    if isinstance(raw, (list, tuple)) and len(raw) >= 3:
        return (int(raw[0]), int(raw[1]), int(raw[2]))
    return (0, 0, 0)


def draw_text_at(img, text: str, value_bbox_rel: list, font_size: int, font_path, fill=(0, 0, 0)):
    if not text or not value_bbox_rel:
        return
    tw, th = img.size
    xywh = rel_to_pixel(value_bbox_rel, tw, th)
    if not xywh:
        return
    x, y, w, h = xywh
    font = get_font(font_path, font_size)
    ImageDraw.Draw(img).text((x, y), text, font=font, fill=fill)


def _photo_rect(photo_cfg: dict, tw: int, th: int) -> tuple | None:
    if "x_rel" in photo_cfg:
        x = int(photo_cfg["x_rel"] * tw)
        y = int(photo_cfg["y_rel"] * th)
        w = int(photo_cfg.get("w_rel", 0.4) * tw)
        h = int(photo_cfg.get("h_rel", 0.32) * th)
    else:
        x, y = int(photo_cfg.get("x", 0)), int(photo_cfg.get("y", 0))
        w = int(photo_cfg.get("w", photo_cfg.get("w_rel", 0.4) * tw))
        h = int(photo_cfg.get("h", photo_cfg.get("h_rel", 0.32) * th))
    if w <= 0 or h <= 0:
        return None
    return (x, y, w, h)


def paste_photo(img, photo_path: str, photo_cfg: dict, tw: int, th: int):
    rect = _photo_rect(photo_cfg, tw, th)
    if not rect:
        return
    x, y, w, h = rect
    scale = photo_cfg.get("scale", PHOTO_SCALE)
    w2, h2 = int(w * scale), int(h * scale)
    if w2 <= 0 or h2 <= 0:
        return
    px, py = x + (w - w2) // 2, y + (h - h2) // 2
    photo = Image.open(photo_path).convert("RGB").resize((w2, h2), Image.Resampling.LANCZOS)
    img.paste(photo, (px, py))


def draw_photo_placeholder(img, photo_cfg: dict, tw: int, th: int, font_path):
    rect = _photo_rect(photo_cfg, tw, th)
    if not rect:
        return
    x, y, w, h = rect
    scale = photo_cfg.get("scale", PHOTO_SCALE)
    w2, h2 = int(w * scale), int(h * scale)
    px, py = x + (w - w2) // 2, y + (h - h2) // 2
    draw = ImageDraw.Draw(img)
    draw.rectangle([px, py, px + w2, py + h2], fill=(240, 240, 240), outline=(200, 200, 200), width=2)
    font = get_font(font_path, max(10, min(w2, h2) // 8))
    draw.text((px + (w2 - 60) // 2, py + (h2 - 16) // 2), "暂无照片", font=font, fill=(150, 150, 150))


def fill_template2(
    template_path: str,
    config_path: str,
    photo_path: str | None,
    output_path: str,
    data_override: dict | None = None,
    font_path: str | None = None,
) -> None:
    template_path = Path(template_path)
    config_path = Path(config_path)
    if not template_path.exists():
        raise FileNotFoundError(f"模板不存在: {template_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"配置不存在: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    font_path = resolve_font_path(config, font_path)
    img = Image.open(template_path).convert("RGB")
    tw, th = img.size

    data = dict(data_override) if data_override else {}
    fields = config.get("fields") or {}
    update_date_cfg = config.get("update_date") or {}

    # 1) 更新日期
    ud_value = data.get("更新日期")
    if ud_value is None or str(ud_value).strip() == "":
        ud_value = (update_date_cfg.get("value_text") or "").strip()
    if ud_value:
        vbr = update_date_cfg.get("value_bbox_rel")
        if vbr and len(vbr) >= 4:
            fill = _parse_fill(update_date_cfg)
            draw_text_at(img, str(ud_value), vbr, update_date_cfg.get("font_size", 12), font_path, fill=fill)

    # 2) 各字段
    for name, field in fields.items():
        if name in SKIP_FIELD_NAMES or not isinstance(field, dict):
            continue
        value = data.get(name)
        if value is None:
            value = (field.get("value_text") or "").strip()
        elif isinstance(value, str) and value.strip() == "":
            value = ""
        if not value:
            continue
        vbr = field.get("value_bbox_rel")
        if not vbr or len(vbr) < 4:
            continue
        draw_text_at(img, str(value).strip(), vbr, field.get("font_size", 12), font_path)

    # 3) 二维码
    qr_cfg = config.get("qr_code_placeholder")
    if qr_cfg and isinstance(qr_cfg, dict):
        x_rel = qr_cfg.get("x_rel")
        y_rel = qr_cfg.get("y_rel")
        w_rel = qr_cfg.get("w_rel")
        h_rel = qr_cfg.get("h_rel")
        if x_rel is not None and y_rel is not None and w_rel and h_rel:
            x0 = int(x_rel * tw)
            y0 = int(y_rel * th)
            size = min(int(w_rel * tw), int(h_rel * th))
            content = data.get("二维码内容") or qr_cfg.get("content") or qr_cfg.get("url")
            if content and HAS_QRCODE:
                qr = qrcode.QRCode(version=1, box_size=10, border=1)
                qr.add_data(str(content).strip())
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB").resize((size, size), Image.Resampling.LANCZOS)
                img.paste(qr_img, (x0, y0))
            else:
                draw = ImageDraw.Draw(img)
                draw.rectangle([x0, y0, x0 + size, y0 + size], fill=tuple(qr_cfg.get("fill", [248, 248, 248])), outline=tuple(qr_cfg.get("outline", [180, 180, 180])), width=1)

    # 4) 在线验证码
    vc_cfg = config.get("verification_code")
    if vc_cfg and isinstance(vc_cfg, dict):
        vbr = vc_cfg.get("value_bbox_rel")
        if vbr and len(vbr) >= 4:
            vc_value = data.get("在线验证码")
            if vc_value is None or str(vc_value).strip() == "":
                vc_value = (vc_cfg.get("value_text") or "").strip()
            else:
                vc_value = str(vc_value).strip()
            if vc_value:
                vc_font = resolve_font_path(vc_cfg, None) or font_path
                draw_text_at(img, vc_value, vbr, vc_cfg.get("font_size", 14), vc_font, fill=_parse_fill(vc_cfg))

    # 5) 照片
    if not config.get("skip_photo"):
        photo_cfg = config.get("photo") or DEFAULT_PHOTO_REL
        if photo_cfg:
            if photo_path and Path(photo_path).exists():
                paste_photo(img, photo_path, photo_cfg, tw, th)
            else:
                draw_photo_placeholder(img, photo_cfg, tw, th, font_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95)
    print(f"已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="模板2：学历证书电子注册备案表 填充")
    parser.add_argument("--template", "-t", required=True, help="空白模板 templete2.jpg")
    parser.add_argument("--config", "-c", required=True, help="layout_config2.json")
    parser.add_argument("--photo", "-p", default=None, help="学生照片（可选）")
    parser.add_argument("--output", "-o", default=None, help="输出图片路径")
    parser.add_argument("--data-json", default=None, help="字段数据 JSON")
    parser.add_argument("--data", nargs="*", default=None, help="键值对 如 姓名=李思媛")
    parser.add_argument("--font", "-f", default=None, help="中文字体路径")
    args = parser.parse_args()

    data = {}
    if args.data_json and Path(args.data_json).exists():
        with open(args.data_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    if args.data:
        for pair in args.data:
            if "=" in pair:
                k, v = pair.split("=", 1)
                data[k.strip()] = v.strip()

    output = args.output or str(Path(args.template).parent / "result_template2.png")
    try:
        fill_template2(args.template, args.config, args.photo, output, data if data else None, args.font)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
