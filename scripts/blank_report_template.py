#!/usr/bin/env python3
"""
学籍在线验证报告 - 擦除敏感信息并保持背景一致

去掉：学生信息、日期、验证码、照片等。
擦除区域用「文档背景采样」平铺填充，与周围背景一致，不留下白色坑。

依赖: pip install Pillow
用法: python blank_report_template.py <输入图片> [输出图片]
      不传输出路径时，输出为 输入名_blank.png
"""

import sys
from pathlib import Path

from PIL import Image


def sample_background(img: Image.Image, margin: int = 20, patch_size: int = 60) -> Image.Image:
    """
    从图片边缘内侧采样一块纯背景（边框内的空白/水印区），用于后续填充。
    默认取左上角内侧 margin 开始的 patch_size x patch_size。
    """
    w, h = img.size
    # 取左上角内侧一块，避免取到边框花纹
    x1 = margin
    y1 = margin
    x2 = min(x1 + patch_size, w)
    y2 = min(y1 + patch_size, h)
    return img.crop((x1, y1, x2, y2)).copy()


def tile_patch_to_region(patch: Image.Image, width: int, height: int) -> Image.Image:
    """用小块背景平铺填满指定宽高，保持纹理一致。"""
    out = Image.new(patch.mode, (width, height))
    pw, ph = patch.size
    for y in range(0, height, ph):
        for x in range(0, width, pw):
            out.paste(patch, (x, y))
    return out


def fill_region_with_background(
    img: Image.Image,
    patch: Image.Image,
    x1: int, y1: int, x2: int, y2: int,
) -> None:
    """用采样的背景块平铺填充矩形区域，直接修改 img。"""
    w, h = x2 - x1, y2 - y1
    if w <= 0 or h <= 0:
        return
    tiled = tile_patch_to_region(patch, w, h)
    img.paste(tiled, (x1, y1))


def run(
    input_path: str,
    output_path: str | None = None,
    *,
    # 背景采样：距离边缘多少像素开始取，取多大一块
    sample_margin: int = 25,
    sample_patch_size: int = 80,
    # 擦除区域（相对整图宽高的比例，可依实际版面微调）
    # 日期区：标题下方一行
    date_left: float = 0.35,
    date_top: float = 0.07,
    date_right: float = 0.65,
    date_bottom: float = 0.115,
    # 照片区：右上
    photo_left: float = 0.52,
    photo_top: float = 0.12,
    photo_right: float = 0.92,
    photo_bottom: float = 0.38,
    # 主体信息右栏（姓名、性别等右侧填写区）
    body_right_left: float = 0.42,
    body_right_top: float = 0.16,
    body_right_right: float = 0.92,
    body_right_bottom: float = 0.62,
    # 「在线验证码」后的文字信息（验证码数字/字符）
    verify_code_left: float = 0.28,
    verify_code_top: float = 0.66,
    verify_code_right: float = 0.58,
    verify_code_bottom: float = 0.72,
    # 二维码图片区域（通常位于验证码文字右侧）
    qrcode_left: float = 0.58,
    qrcode_top: float = 0.66,
    qrcode_right: float = 0.88,
    qrcode_bottom: float = 0.88,
) -> None:
    path_in = Path(input_path)
    if not path_in.exists():
        raise FileNotFoundError(f"输入图片不存在: {path_in}")
    path_out = Path(output_path) if output_path else path_in.parent / f"{path_in.stem}_blank{path_in.suffix}"

    img = Image.open(path_in).convert("RGB")
    w, h = img.size

    # 采样背景（与文档背景一致）
    patch = sample_background(img, margin=sample_margin, patch_size=sample_patch_size)

    # 擦除区域转为像素坐标
    def box(l, t, r, b):
        return (
            int(l * w), int(t * h), int(r * w), int(b * h)
        )

    regions = [
        ("日期", box(date_left, date_top, date_right, date_bottom)),
        ("照片", box(photo_left, photo_top, photo_right, photo_bottom)),
        ("主体信息右栏", box(body_right_left, body_right_top, body_right_right, body_right_bottom)),
        ("在线验证码后的文字", box(verify_code_left, verify_code_top, verify_code_right, verify_code_bottom)),
        ("二维码图片", box(qrcode_left, qrcode_top, qrcode_right, qrcode_bottom)),
    ]

    for name, (x1, y1, x2, y2) in regions:
        fill_region_with_background(img, patch, x1, y1, x2, y2)
        print(f"  已用背景填充: {name} ({x1},{y1})-({x2},{y2})")

    img.save(path_out, quality=95)
    print(f"已保存: {path_out}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        print("示例: python blank_report_template.py report.png")
        print("      python blank_report_template.py report.png out_blank.png")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    run(input_path, output_path)


if __name__ == "__main__":
    main()
