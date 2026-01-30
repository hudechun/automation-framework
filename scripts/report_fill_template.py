#!/usr/bin/env python3
"""
阶段二：按 layout_config.json 在空白模板上填充文字和照片，输出最终报告图。

- 读入 templete.png、layout_config.json、photo.png 及字段数据（命令行或 JSON）。
- 使用相对坐标（value_bbox_rel / photo x_rel 等）适配模板尺寸；字号、字体从配置读取。
- 依赖: Pillow（及中文字体，如系统宋体）。

用法:
  python scripts/report_fill_template.py --template templete.png --photo photo.png --config layout_config.json --output result.png
  --data 更新日期="2026年01月29日" 姓名=朱妍 性别=女 ...
  或 --data-json data.json（JSON 内为 { "更新日期": "...", "姓名": "...", ... }）
"""

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# 默认中文字体路径（Windows）
DEFAULT_FONT_PATHS = [
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]


def get_font(font_path: str | None, size_pt: int):
    """加载支持中文的字体，size 为磅数."""
    paths = [font_path] if font_path else DEFAULT_FONT_PATHS
    for p in paths:
        if p and Path(p).exists():
            try:
                return ImageFont.truetype(p, size_pt)
            except Exception:
                continue
    return ImageFont.load_default()


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def rel_to_pixel(rel: list | None, tw: int, th: int) -> tuple[int, int, int, int] | None:
    """相对 [x,y,w,h] (0~1) -> 像素 (x,y,w,h)."""
    if not rel or len(rel) < 4:
        return None
    return (
        int(rel[0] * tw),
        int(rel[1] * th),
        int(rel[2] * tw),
        int(rel[3] * th),
    )


def draw_text_on_image(
    img: Image.Image,
    text: str,
    value_bbox_rel: list | None,
    font_size: int,
    font_path: str | None,
    fill=(0, 0, 0),
) -> None:
    """在底图上按配置位置和字号绘制单行文字（左上角对齐 value_bbox）."""
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


def paste_photo(img: Image.Image, photo_path: str, photo_config: dict, tw: int, th: int) -> None:
    """将 photo 缩放到配置的相片区域并粘贴；优先使用 x_rel/y_rel/w_rel/h_rel 以适配模板尺寸."""
    if "x_rel" in photo_config:
        x = int(photo_config["x_rel"] * tw)
        y = int(photo_config["y_rel"] * th)
        w = int(photo_config["w_rel"] * tw)
        h = int(photo_config["h_rel"] * th)
    else:
        # 像素坐标（样本图与模板同尺寸时）
        x = int(photo_config.get("x", 0))
        y = int(photo_config.get("y", 0))
        w = int(photo_config.get("w", 0))
        h = int(photo_config.get("h", 0))
    if w <= 0 or h <= 0:
        return
    try:
        photo = Image.open(photo_path).convert("RGB")
    except Exception as e:
        raise FileNotFoundError(f"无法打开照片: {photo_path}") from e
    photo = photo.resize((w, h), Image.Resampling.LANCZOS)
    img.paste(photo, (x, y))


def fill_template(
    template_path: str,
    config_path: str,
    photo_path: str,
    data: dict,
    output_path: str,
    font_path: str | None = None,
) -> None:
    """
    data: { "更新日期": "...", "姓名": "...", ... }，键与 layout_config 中字段名一致。
    使用配置中的 value_bbox_rel（相对坐标）在模板上绘制文字；照片按 photo 配置粘贴。
    """
    template_path = Path(template_path)
    config_path = Path(config_path)
    if not template_path.exists():
        raise FileNotFoundError(f"模板不存在: {template_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"配置不存在: {config_path}")

    config = load_config(str(config_path))
    img = Image.open(template_path).convert("RGB")
    tw, th = img.size

    # 更新日期（单独字段）
    ud = config.get("update_date", {})
    if isinstance(ud, dict) and data.get("更新日期"):
        vbr = ud.get("value_bbox_rel")
        if vbr and len(vbr) >= 4:
            draw_text_on_image(
                img,
                str(data["更新日期"]),
                vbr,
                ud.get("font_size", 12),
                font_path,
            )

    # 各字段：按配置 fields 顺序，有数据则绘制
    fields = config.get("fields", {})
    for name, field in fields.items():
        value = data.get(name)
        if value is None or str(value).strip() == "":
            continue
        if not isinstance(field, dict):
            continue
        vbr = field.get("value_bbox_rel")
        pt = field.get("font_size", 12)
        draw_text_on_image(img, str(value).strip(), vbr, pt, font_path)

    # 照片
    photo_cfg = config.get("photo", {})
    if photo_cfg and photo_path and Path(photo_path).exists():
        paste_photo(img, photo_path, photo_cfg, tw, th)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95)
    print(f"已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="学籍报告空白模板填充")
    parser.add_argument("--template", "-t", required=True, help="空白模板图片路径，如 templete.png")
    parser.add_argument("--photo", "-p", required=True, help="学生照片路径，如 photo.png")
    parser.add_argument("--config", "-c", required=True, help="布局配置 JSON，如 layout_config.json")
    parser.add_argument("--output", "-o", default=None, help="输出图片路径，默认 result.png")
    parser.add_argument("--data-json", default=None, help="字段数据 JSON 文件，键为字段名")
    parser.add_argument("--data", nargs="*", default=None, help='键值对，如 姓名=朱妍 性别=女（空格分隔）')
    parser.add_argument("--font", "-f", default=None, help="中文字体路径，如 simsun.ttc")
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

    if not data:
        print("请通过 --data 或 --data-json 提供字段数据。", file=sys.stderr)
        sys.exit(1)

    output = args.output or str(Path(args.template).parent / "result.png")
    try:
        fill_template(
            args.template,
            args.config,
            args.photo,
            data,
            output,
            font_path=args.font,
        )
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
