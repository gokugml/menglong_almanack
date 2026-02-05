#!/usr/bin/env python3
"""
图片字幕识别和拼接工具
功能：
1. 识别图片中的字幕位置
2. 保留第一张图的全部画面
3. 其他图片仅保留字幕部分
4. 按顺序拼接所有字幕到第一张图底部
"""

import os
from PIL import Image, ImageFilter, ImageOps
import numpy as np
from pathlib import Path


def detect_text_blocks_simple(img_array, start_row, end_row):
    """
    简单但可靠地检测文字块，通过行标准差分析

    参数：
        img_array: 图片数组
        start_row: 开始行
        end_row: 结束行

    返回：
        文字块列表，每个元素是 (block_start, block_end)
    """
    if end_row <= start_row:
        return []

    row_std = np.std(img_array[start_row:end_row], axis=1)

    # 使用较低的阈值，确保不会漏掉文字
    threshold = np.mean(row_std) * 0.8
    text_rows = row_std > threshold

    # 找到文字行的起始和结束
    text_indices = np.where(text_rows)[0]

    if len(text_indices) == 0:
        return []

    # 找到所有连续的文字块
    blocks = []
    block_start = text_indices[0]

    for i in range(1, len(text_indices)):
        # 如果间隔超过20行，认为是不同的块
        if text_indices[i] - text_indices[i-1] > 20:
            blocks.append((start_row + block_start, start_row + text_indices[i-1] + 1))
            block_start = text_indices[i]

    # 添加最后一个块
    blocks.append((start_row + block_start, start_row + text_indices[-1] + 1))

    return blocks


def detect_subtitle_region(image_path, bottom_pixels=150, subtitle_lang='chinese', extra_space_ratio=0.1):
    """
    检测图片中字幕的位置 - 只扫描图片最底部固定像素区域

    参数：
        image_path: 图片路径
        bottom_pixels: 从底部开始检测的像素数（默认150像素）
        subtitle_lang: 字幕语言选择 ('chinese', 'english', 'both')
                      - 'chinese': 只保留中文字幕
                      - 'english': 只保留英文字幕
                      - 'both': 保留全部字幕
        extra_space_ratio: 字幕区域上下额外保留的空间比例（默认10%）

    返回：
        字幕区域的 (top, height) 坐标
    """
    img = Image.open(image_path)
    width, height = img.size

    # 转换为灰度图
    gray = img.convert('L')

    # 只分析底部固定像素区域（默认150像素，确保只获取字幕）
    bottom_height = min(bottom_pixels, int(height * 0.2))  # 最多不超过图片高度的20%
    bottom_region = gray.crop((0, height - bottom_height, width, height))

    # 转换为numpy数组进行分析
    img_array = np.array(bottom_region)

    # 计算每一行的标准差（文字区域标准差较大）
    row_std = np.std(img_array, axis=1)

    # 使用更高的阈值，只检测明显的字幕文字
    threshold = np.mean(row_std) + np.std(row_std) * 0.5
    text_rows = row_std > threshold

    # 找到连续的文字区域
    if np.any(text_rows):
        text_indices = np.where(text_rows)[0]

        # 从底部开始，找到最底部的连续文字块
        # 这样可以避免误检测画面中的其他文字
        last_text_row = text_indices[-1]

        # 从最后一个文字行向上查找，找到连续的文字块
        subtitle_bottom = last_text_row + 1
        subtitle_top = last_text_row

        # 向上扫描，找到连续的文字行，但限制最大高度
        max_subtitle_height = 100  # 字幕最大高度不超过100像素

        for i in range(len(text_indices) - 1, -1, -1):
            # 如果当前行与上一个检测到的行之间间隔太大（>8行），停止
            if subtitle_top - text_indices[i] > 8:
                break
            # 如果字幕高度超过限制，停止向上扫描
            if subtitle_bottom - text_indices[i] > max_subtitle_height:
                break
            subtitle_top = text_indices[i]

        # 如果需要分离中英文字幕
        if subtitle_lang in ['chinese', 'english']:
            # 在检测到的字幕区域内查找文字块
            blocks = detect_text_blocks_simple(img_array, subtitle_top, subtitle_bottom)

            if len(blocks) >= 2:
                # 找到了多个文字块，可能是双语字幕
                if subtitle_lang == 'chinese':
                    # 保留第一个块（中文通常在上面）
                    subtitle_top = blocks[0][0]
                    subtitle_bottom = blocks[0][1]
                else:  # english
                    # 保留最后一个块（英文通常在下面）
                    subtitle_top = blocks[-1][0]
                    subtitle_bottom = blocks[-1][1]
            elif len(blocks) == 1:
                # 只有一个块，使用整个块
                subtitle_top = blocks[0][0]
                subtitle_bottom = blocks[0][1]

        # 添加上下额外空间（字幕区域的10%）
        subtitle_height = subtitle_bottom - subtitle_top
        extra_space = int(subtitle_height * extra_space_ratio)

        subtitle_top = max(0, subtitle_top - extra_space)
        subtitle_bottom = min(bottom_height, subtitle_bottom + extra_space)

        # 转换为原图坐标
        actual_top = height - bottom_height + subtitle_top
        actual_height = subtitle_bottom - subtitle_top

        return actual_top, actual_height
    else:
        # 如果没检测到，返回底部15%作为默认字幕区域
        default_height = int(height * 0.15)
        return height - default_height, default_height


def get_sorted_images(folder_path):
    """
    获取文件夹中所有图片并按文件名排序

    参数：
        folder_path: 文件夹路径

    返回：
        排序后的图片文件路径列表
    """
    folder = Path(folder_path)
    image_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}

    image_files = [
        f for f in folder.iterdir()
        if f.suffix in image_extensions and f.is_file()
    ]

    # 按文件名排序
    image_files.sort(key=lambda x: x.name)

    return image_files


def stitch_subtitles(input_folder, output_path='stitched_result.png', subtitle_lang='chinese', save_preview=True):
    """
    拼接图片字幕

    参数：
        input_folder: 输入图片文件夹路径
        output_path: 输出图片路径
        subtitle_lang: 字幕语言选择 ('chinese', 'english', 'both')
        save_preview: 是否保存每张图的字幕预览
    """
    print(f"正在处理文件夹: {input_folder}")
    print(f"字幕语言设置: {subtitle_lang}")

    # 创建预览文件夹
    preview_folder = None
    if save_preview:
        preview_folder = Path(input_folder.rstrip('/') + '_subtitle_preview')
        preview_folder.mkdir(exist_ok=True)
        print(f"字幕预览将保存到: {preview_folder}")

    # 获取所有图片
    image_files = get_sorted_images(input_folder)

    if not image_files:
        print("错误：未找到图片文件")
        return

    if len(image_files) < 2:
        print("错误：至少需要2张图片")
        return

    print(f"找到 {len(image_files)} 张图片\n")

    # 读取第一张图片（保留完整画面）
    first_image = Image.open(image_files[0])
    print(f"第一张图片: {image_files[0].name} - 尺寸: {first_image.size}")
    print("  → 保留完整画面，不提取字幕\n")

    width = first_image.width

    # 收集所有字幕区域（从第二张开始）
    subtitle_images = []

    # 处理每张图片（从第二张开始）
    for i, img_path in enumerate(image_files[1:], start=2):
        print(f"处理第 {i} 张图片: {img_path.name}")

        # 检测字幕区域
        subtitle_top, subtitle_height = detect_subtitle_region(img_path, subtitle_lang=subtitle_lang)
        print(f"  检测到字幕位置: top={subtitle_top}, height={subtitle_height}")

        # 读取图片并裁切字幕区域
        img = Image.open(img_path)

        # 确保宽度一致
        if img.width != width:
            print(f"  警告：图片宽度不一致，调整为 {width}")
            img = img.resize((width, int(img.height * width / img.width)), Image.Resampling.LANCZOS)
            # 重新计算字幕位置
            subtitle_top = int(subtitle_top * width / img.width)

        # 裁切字幕区域
        subtitle_region = img.crop((0, subtitle_top, width, subtitle_top + subtitle_height))
        subtitle_images.append(subtitle_region)

        print(f"  字幕区域尺寸: {subtitle_region.size}")

        # 保存字幕预览
        if save_preview and preview_folder:
            preview_path = preview_folder / f"{i:03d}_{img_path.stem}_subtitle.png"
            subtitle_region.save(preview_path)
            print(f"  ✓ 预览已保存: {preview_path.name}")

    # 计算最终图片的总高度
    total_height = first_image.height + sum(sub.height for sub in subtitle_images)

    print(f"\n创建最终图片，尺寸: {width} x {total_height}")

    # 创建新图片
    result = Image.new('RGB', (width, total_height))

    # 粘贴第一张完整图片
    result.paste(first_image, (0, 0))

    # 依次粘贴所有字幕区域（从第二张图开始）
    current_y = first_image.height
    for i, subtitle in enumerate(subtitle_images, start=2):
        result.paste(subtitle, (0, current_y))
        print(f"粘贴第 {i} 张图的字幕区域到位置: y={current_y}")
        current_y += subtitle.height

    # 保存结果
    result.save(output_path, quality=95)
    print(f"\n完成！结果已保存到: {output_path}")
    print(f"最终图片尺寸: {result.size}")


def main():
    # 询问用户输入文件夹路径
    print("=" * 60)
    print("图片字幕拼接工具")
    print("=" * 60)
    print()

    input_folder = input("请输入图片文件夹路径（默认：ted talk/）: ").strip()
    if not input_folder:
        input_folder = "ted talk/"

    # 移除路径末尾的斜杠（如果有）并添加标准斜杠
    input_folder = input_folder.rstrip('/') + '/'

    # 生成输出文件名（基于文件夹名）
    folder_name = input_folder.rstrip('/').split('/')[-1]
    output_file = f"{folder_name}_stitched.png"

    print()

    # 询问用户字幕语言选择
    print("请选择字幕语言（默认：中文）：")
    print("  1. 中文字幕（保留上半部分）")
    print("  2. 英文字幕（保留下半部分）")
    print("  3. 双语字幕（保留全部）")
    print()

    choice = input("请输入选项 [1/2/3，默认为1]: ").strip()

    # 根据用户选择设置语言参数
    subtitle_lang_map = {
        '1': 'chinese',
        '2': 'english',
        '3': 'both',
        '': 'chinese'  # 默认值
    }

    subtitle_lang = subtitle_lang_map.get(choice, 'chinese')

    lang_name_map = {
        'chinese': '中文',
        'english': '英文',
        'both': '双语'
    }

    print(f"\n已选择: {lang_name_map[subtitle_lang]}字幕")
    print("=" * 60)
    print()

    # 执行拼接
    stitch_subtitles(input_folder, output_file, subtitle_lang)


if __name__ == "__main__":
    main()
