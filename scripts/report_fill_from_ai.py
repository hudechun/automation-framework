#!/usr/bin/env python3
"""
第二阶段（专用）：处理 AI 生成的 layout_config.json，在空白模板上填充文字和照片。

- 输入：report_layout_analyze_qwen.py 输出的 layout_config.json、空白模板图、学生照片。
- 数据来源：优先使用 --data-json / --data；未提供时使用 config 内 AI 识别的 value_text。
- 约定：仅消费 AI 生成的 config 结构（update_date、fields、photo）；跳过 fields 中的「更新日期」避免重复绘制；相对坐标超范围时裁剪到 [0,1]。

依赖: Pillow
用法:
  python scripts/report_fill_from_ai.py --template templete.png --photo photo.png --config layout_config.json [--output result.png]
  [--data-json data.json] 或 [--data 姓名=xxx ...] 不传则用 config 里的 value_text
"""

import argparse
import json
import random
import string
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
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]

# 字体名 -> 路径，用于与原型图一致（学籍报告常用仿宋）
FONT_FAMILY_PATHS = {
    "SimSun": "C:/Windows/Fonts/simsun.ttc",
    "宋体": "C:/Windows/Fonts/simsun.ttc",
    "FangSong": "C:/Windows/Fonts/simfang.ttf",
    "仿宋": "C:/Windows/Fonts/simfang.ttf",
    "KaiTi": "C:/Windows/Fonts/simkai.ttf",
    "楷体": "C:/Windows/Fonts/simkai.ttf",
    "SimHei": "C:/Windows/Fonts/simhei.ttf",
    "黑体": "C:/Windows/Fonts/simhei.ttf",
    "Microsoft YaHei": "C:/Windows/Fonts/msyh.ttc",
    "微软雅黑": "C:/Windows/Fonts/msyh.ttc",
    "Microsoft YaHei Bold": "C:/Windows/Fonts/msyhbd.ttc",
    "微软雅黑粗体": "C:/Windows/Fonts/msyhbd.ttc",
    "DengXian": "C:/Windows/Fonts/dengl.ttf",
    "等线": "C:/Windows/Fonts/dengl.ttf",
}


def resolve_font_path(config: dict, font_path_arg: str | None) -> str | None:
    """优先用命令行字体，否则用 config 的 font_path / font_family."""
    if font_path_arg and Path(font_path_arg).exists():
        return font_path_arg
    path = config.get("font_path")
    if path and Path(path).exists():
        return path
    name = config.get("font_family")
    if name and name in FONT_FAMILY_PATHS:
        p = FONT_FAMILY_PATHS[name]
        if Path(p).exists():
            return p
    return None


def _font_path_from_cfg(cfg: dict | None) -> str | None:
    """从子配置（如 verification_code）解析字体路径."""
    if not cfg:
        return None
    path = cfg.get("font_path")
    if path and Path(path).exists():
        return path
    name = cfg.get("font_family")
    if name and name in FONT_FAMILY_PATHS:
        p = FONT_FAMILY_PATHS[name]
        if Path(p).exists():
            return p
    return None


def gen_verification_code(length: int = 16, chars: str = None) -> str:
    """生成随机大写字母+数字组合，默认16位."""
    if chars is None:
        chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


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
    """将相对坐标限制在 [0,1] 内，避免 AI 返回 0.94、1.0 等导致错位."""
    if not rel or len(rel) < 4:
        return rel or []
    x, y, w, h = rel[0], rel[1], rel[2], rel[3]
    x = max(0, min(1, float(x)))
    y = max(0, min(1, float(y)))
    w = max(0.01, min(1 - x, float(w)))
    h = max(0.01, min(1 - y, float(h)))
    return [round(x, 4), round(y, 4), round(w, 4), round(h, 4)]


def rel_to_pixel(rel: list | None, tw: int, th: int) -> tuple[int, int, int, int] | None:
    if not rel or len(rel) < 4:
        return None
    rel = clamp_rel(rel)
    return (
        int(rel[0] * tw),
        int(rel[1] * th),
        int(rel[2] * tw),
        int(rel[3] * th),
    )


def _parse_fill(cfg: dict | None) -> tuple[int, int, int]:
    """从配置解析 fill 颜色，支持 [r,g,b] 或 (r,g,b)，默认黑色."""
    if not cfg:
        return (0, 0, 0)
    raw = cfg.get("fill")
    if raw is None:
        return (0, 0, 0)
    if isinstance(raw, (list, tuple)) and len(raw) >= 3:
        return (int(raw[0]), int(raw[1]), int(raw[2]))
    return (0, 0, 0)


def draw_text_at(img: Image.Image, text: str, value_bbox_rel: list, font_size: int, font_path: str | None, fill=(0, 0, 0)):
    if not text or not value_bbox_rel:
        return
    tw, th = img.size
    xywh = rel_to_pixel(value_bbox_rel, tw, th)
    if not xywh:
        return
    x, y, w, h = xywh
    font = get_font(font_path, font_size)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, font=font, fill=fill)


# 当 config.photo 为 null 时使用的默认照片区域（右上角，相对坐标 0~1）
DEFAULT_PHOTO_REL = {"x_rel": 0.52, "y_rel": 0.12, "w_rel": 0.40, "h_rel": 0.26}
# 照片显示尺寸缩放：1/4 表示宽高各缩小为原来的 1/4
PHOTO_SCALE = 0.25


def _photo_rect(photo_cfg: dict, tw: int, th: int) -> tuple[int, int, int, int] | None:
    """从 photo_cfg 计算 (x, y, w, h)。支持 w/h 固定像素或 w_rel/h_rel 相对比例。"""
    if "x_rel" in photo_cfg:
        x = int(photo_cfg["x_rel"] * tw)
        y = int(photo_cfg["y_rel"] * th)
    else:
        x = int(photo_cfg.get("x", 0))
        y = int(photo_cfg.get("y", 0))
    if "w" in photo_cfg and "h" in photo_cfg:
        w = int(photo_cfg["w"])
        h = int(photo_cfg["h"])
    elif "w_rel" in photo_cfg and "h_rel" in photo_cfg:
        w = int(photo_cfg["w_rel"] * tw)
        h = int(photo_cfg["h_rel"] * th)
    else:
        w = int(photo_cfg.get("w", 0))
        h = int(photo_cfg.get("h", 0))
    if w <= 0 or h <= 0:
        return None
    return (x, y, w, h)


def paste_photo(img: Image.Image, photo_path: str, photo_cfg: dict, tw: int, th: int) -> None:
    rect = _photo_rect(photo_cfg, tw, th)
    if rect is None:
        return
    x, y, w, h = rect
    if "w" in photo_cfg and "h" in photo_cfg:
        w2, h2 = w, h
        px, py = x, y
    else:
        scale = photo_cfg.get("scale", PHOTO_SCALE)
        w2, h2 = int(w * scale), int(h * scale)
        if w2 <= 0 or h2 <= 0:
            return
        px = x + (w - w2) // 2
        py = y + (h - h2) // 2
    photo = Image.open(photo_path).convert("RGB")
    photo = photo.resize((w2, h2), Image.Resampling.LANCZOS)
    img.paste(photo, (px, py))


def draw_photo_placeholder(
    img: Image.Image, photo_cfg: dict, tw: int, th: int, font_path: str | None = None
) -> None:
    """无照片时绘制灰色框 +「暂无照片」"""
    rect = _photo_rect(photo_cfg, tw, th)
    if rect is None:
        return
    x, y, w, h = rect
    if "w" in photo_cfg and "h" in photo_cfg:
        px, py, w2, h2 = x, y, w, h
    else:
        scale = photo_cfg.get("scale", PHOTO_SCALE)
        w2, h2 = int(w * scale), int(h * scale)
        if w2 <= 0 or h2 <= 0:
            return
        px = x + (w - w2) // 2
        py = y + (h - h2) // 2
    draw = ImageDraw.Draw(img)
    fill = (240, 240, 240)
    outline = (200, 200, 200)
    draw.rectangle([px, py, px + w2, py + h2], fill=fill, outline=outline, width=2)
    font_size = max(10, min(w2, h2) // 8)
    font = get_font(font_path, font_size)
    text = "暂无照片"
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw_text, th_text = bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        tw_text, th_text = draw.textsize(text, font=font)  # type: ignore
    tx = px + (w2 - tw_text) // 2
    ty = py + (h2 - th_text) // 2
    draw.text((tx, ty), text, font=font, fill=(150, 150, 150))


def fill_from_ai_config(
    template_path: str,
    config_path: str,
    photo_path: str | None,
    output_path: str,
    data_override: dict | None = None,
    font_path: str | None = None,
) -> None:
    """
    仅处理 AI 生成的 layout_config：update_date、fields、photo。
    data_override 若提供则覆盖 config 中的 value_text；否则用 config 里的 value_text。
    """
    template_path = Path(template_path)
    config_path = Path(config_path)
    if not template_path.exists():
        raise FileNotFoundError(f"模板不存在: {template_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"配置不存在: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 字体：命令行 > config.font_path > config.font_family 映射
    font_path = resolve_font_path(config, font_path)

    img = Image.open(template_path).convert("RGB")
    tw, th = img.size

    # 数据：优先命令行/文件，否则用 AI 的 value_text
    data = dict(data_override) if data_override else {}
    fields = config.get("fields") or {}
    update_date_cfg = config.get("update_date") or {}

    # 1) 更新日期（只画一次，不从 fields 再画）
    ud_value = data.get("更新日期")
    if ud_value is None or str(ud_value).strip() == "":
        ud_value = (update_date_cfg.get("value_text") or "").strip()
    if ud_value:
        vbr = update_date_cfg.get("value_bbox_rel")
        if vbr and len(vbr) >= 4:
            fill = _parse_fill(update_date_cfg)
            draw_text_at(img, str(ud_value), vbr, update_date_cfg.get("font_size", 12), font_path, fill=fill)

    # 2) 各字段（跳过「更新日期」；跳过「学籍状态」，模板上已有不填）
    SKIP_FIELD_NAMES = {"更新日期", "学籍状态"}
    for name, field in fields.items():
        if name in SKIP_FIELD_NAMES:
            continue
        if not isinstance(field, dict):
            continue
        value = data.get(name)
        if value is None or str(value).strip() == "":
            value = (field.get("value_text") or "").strip()
        if not value:
            continue
        vbr = field.get("value_bbox_rel")
        if not vbr or len(vbr) < 4:
            continue
        pt = field.get("font_size", 12)
        draw_text_at(img, str(value).strip(), vbr, pt, font_path)

    # 2.4) 二维码占位符：有 content/url 时生成二维码并贴上，否则画方框占位
    qr_cfg = config.get("qr_code_placeholder")
    if qr_cfg and isinstance(qr_cfg, dict):
        x_rel = qr_cfg.get("x_rel")
        y_rel = qr_cfg.get("y_rel")
        w_rel = qr_cfg.get("w_rel")
        h_rel = qr_cfg.get("h_rel")
        if x_rel is not None and y_rel is not None and w_rel and h_rel:
            x0 = int(x_rel * tw)
            y0 = int(y_rel * th)
            qw = int(w_rel * tw)
            qh = int(h_rel * th)
            # 1:1 正方形：取宽高较小值，避免 w_rel/h_rel 乘不同边导致竖长条
            size = min(qw, qh)
            content = qr_cfg.get("content") or qr_cfg.get("url") or data.get("二维码内容")
            if content and HAS_QRCODE:
                qr = qrcode.QRCode(version=1, box_size=10, border=1)
                qr.add_data(str(content).strip())
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
                qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
                img.paste(qr_img, (x0, y0))
            else:
                x1, y1 = x0 + size, y0 + size
                draw = ImageDraw.Draw(img)
                fill_color = tuple(qr_cfg.get("fill", [248, 248, 248]))
                outline_color = tuple(qr_cfg.get("outline", [180, 180, 180]))
                draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=outline_color, width=1)

    # 2.5) 在线验证码：常量，优先用 data「在线验证码」，否则用 config.value_text；随机生成在别处处理
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
                vc_font_path = _font_path_from_cfg(vc_cfg) or font_path
                vc_fill = _parse_fill(vc_cfg)
                draw_text_at(img, vc_value, vbr, vc_cfg.get("font_size", 12), vc_font_path, fill=vc_fill)

    # 3) 照片（config 中 "skip_photo": true 时跳过；有 photo 区域时贴图或占位）
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
    parser = argparse.ArgumentParser(description="第二阶段：按 AI 生成的 layout_config 填充学籍报告模板")
    parser.add_argument("--template", "-t", required=True, help="空白模板图片")
    parser.add_argument("--photo", "-p", default=None, help="学生照片（可选）")
    parser.add_argument("--config", "-c", required=True, help="AI 输出的 layout_config.json")
    parser.add_argument("--output", "-o", default=None, help="输出图片路径")
    parser.add_argument("--data-json", default=None, help="覆盖字段数据 JSON；不传则用 config 内 value_text")
    parser.add_argument("--data", nargs="*", default=None, help="覆盖键值对，如 姓名=朱妍")
    parser.add_argument("--font", "-f", default=None, help="中文字体路径")
    args = parser.parse_args()

    data = {}
    if args.data_json:
        with open(args.data_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    if args.data:
        for pair in args.data:
            if "=" in pair:
                k, v = pair.split("=", 1)
                data[k.strip()] = v.strip()

    output = args.output or str(Path(args.template).parent / "result.png")
    try:
        fill_from_ai_config(
            args.template,
            args.config,
            args.photo,
            output,
            data_override=data if data else None,
            font_path=args.font,
        )
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
