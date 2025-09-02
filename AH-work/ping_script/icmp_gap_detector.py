# -*- coding: utf-8 -*-
import re
from pathlib import Path
from typing import List, Optional, Tuple


# def detect_icmp_gaps(filename: str) -> None:
#     """检测ICMP序列号中的间隔并打印间断信息及上下文"""
#     # 检查文件存在性
#     file_path = Path(filename)
#     if not file_path.exists():
#         print(f"错误：文件 '{filename}' 不存在")
#         return
#
#     if not file_path.is_file():
#         print(f"错误：'{filename}' 不是文件")
#         return
#
#     last_icmp_seq: Optional[int] = None
#     known_seqs: set[int] = set()
#     line_buffer: List[str] = []
#
#     with file_path.open('r', encoding='utf-8', errors='ignore') as file:
#         lines: List[str] = file.readlines()
#         total_lines: int = len(lines)
#
#         for i, line in enumerate(lines):
#             # 使用正则表达式提取icmp_seq值
#             match: Optional[re.Match] = re.search(r'icmp_seq=(\d+)', line)
#             if not match:
#                 continue  # 跳过不包含icmp_seq的行
#
#             try:
#                 current_icmp_seq: int = int(match.group(1))
#
#                 # 检查序列号是否重复出现
#                 if current_icmp_seq in known_seqs:
#                     print(f"\033[1;33m警告：序列号 {current_icmp_seq} 重复出现\033[0m")
#                     continue
#
#                 known_seqs.add(current_icmp_seq)
#
#                 if last_icmp_seq is not None:
#                     # 检测序列号间断（忽略时间回溯）
#                     if current_icmp_seq > last_icmp_seq + 1:
#                         lost_pkts: int = current_icmp_seq - last_icmp_seq - 1
#
#                         # 输出间断信息（带颜色）
#                         print(f"\n在文件 '{filename}' 中发现序列号间断:")
#                         print(f"  前一行序列号: {last_icmp_seq}")
#                         print(f"  当前行序列号: {current_icmp_seq}")
#                         print("相关上下文内容:")
#
#                         # 生成上下文索引范围
#                         start_idx: int = max(0, i - 2)
#                         end_idx: int = min(total_lines, i + 3)
#
#                         # 输出上下文行（带行号）
#                         for j in range(start_idx, end_idx):
#                             prefix: str = ">>> " if j == i else "    "
#                             line_number: str = f"{j + 1:>4}: "
#
#                             if j in {i - 1, i}:
#                                 print(f"{prefix}{line_number}{lines[j].rstrip()}")
#                             else:
#                                 print(f"{prefix}{line_number}{lines[j].rstrip()}")
#
#                         print(f"  \033[1;31m丢失包数: {lost_pkts}个\033[0m")
#                         # 输出空行分隔
#                         print("\n" + "-" * 80)
#
#                 last_icmp_seq = current_icmp_seq
#             except ValueError:
#                 print(f"\033[1;31m错误：无效的序列号值 '{match.group(1)}' 在第 {i + 1} 行\033[0m")
#
#         if not known_seqs:
#             print(f"未在文件 '{filename}' 中找到任何有效的 ICMP 序列号")
def detect_icmp_gaps(filename: str) -> None:
    """检测ICMP序列号中的间隔并打印间断信息及上下文"""
    # 检查文件存在性
    file_path = Path(filename)
    if not file_path.exists():
        print(f"错误：文件 '{filename}' 不存在")
        return

    if not file_path.is_file():
        print(f"错误：'{filename}' 不是文件")
        return

    last_icmp_seq: Optional[int] = None
    known_seqs: set[int] = set()

    # 存储处理后的行：(原始行号, 行内容)
    valid_lines: List[Tuple[int, str]] = []

    with file_path.open('r', encoding='utf-8', errors='ignore') as file:
        # 读取所有行并过滤空行
        raw_lines: List[str] = file.readlines()
        for idx, line in enumerate(raw_lines):
            stripped = line.strip()
            if stripped:  # 跳过空行和只有空格的行
                valid_lines.append((idx, stripped))

    if not valid_lines:
        print(f"文件 '{filename}' 为空或只包含空白行")
        return

    total_lines: int = len(valid_lines)

    # 处理有效行
    for i in range(total_lines):
        raw_idx, line = valid_lines[i]
        # 使用正则表达式提取icmp_seq值
        match: Optional[re.Match] = re.search(r'icmp_seq=(\d+)', line)
        if not match:
            continue  # 跳过不包含icmp_seq的行

        try:
            current_icmp_seq: int = int(match.group(1))

            # 检查序列号是否重复出现
            if current_icmp_seq in known_seqs:
                print(f"\033[1;33m警告：序列号 {current_icmp_seq} 重复出现 (原始行号: {raw_idx + 1})\033[0m")
                continue

            known_seqs.add(current_icmp_seq)

            if last_icmp_seq is not None:
                # 检测序列号间断（忽略时间回溯）
                if current_icmp_seq > last_icmp_seq + 1:
                    lost_pkts: int = current_icmp_seq - last_icmp_seq - 1

                    # 输出间断信息（带颜色）
                    print(f"\n在文件 '{filename}' 中发现序列号间断:")
                    print(f"  前一行序列号: {last_icmp_seq} (原始行号: {raw_line_info[0] + 1})")
                    print(f"  当前行序列号: {current_icmp_seq} (原始行号: {raw_idx + 1})")
                    print(f"  有效行号: {raw_line_info[0] + 1} → {raw_idx + 1}")
                    print("相关上下文内容 (已过滤空行):")

                    # 生成上下文索引范围 - 使用过滤后的行号
                    start_idx: int = max(0, i - 2)
                    end_idx: int = min(total_lines, i + 3)

                    # 输出上下文行（带行号）
                    for j in range(start_idx, end_idx):
                        # 原始行号索引
                        ctx_raw_idx, ctx_line = valid_lines[j]
                        prefix: str = ">>> " if j == i or j == raw_line_info[1] else "    "

                        # 显示过滤后的行号（连续）和原始行号
                        # print(f"{prefix}行 {j + 1:>4} (原{ctx_raw_idx + 1:>4}): {ctx_line}")
                        print(f"{ctx_line}")
                    print(f"  \033[1;31m丢失包数: {lost_pkts}个\033[0m")
                    # 输出空行分隔
                    print("\n" + "-" * 80)

            # 保存当前行的信息供下一次比较使用
            last_icmp_seq = current_icmp_seq
            raw_line_info = (raw_idx, i)  # (原始行号, 有效行索引)

        except ValueError:
            print(f"\033[1;31m错误：无效的序列号值 '{match.group(1)}' 在第 {raw_idx + 1} 行\033[0m")

    if not known_seqs:
        print(f"未在文件 '{filename}' 中找到任何有效的 ICMP 序列号")
    else:
        print(f"\n分析完成，共处理 {total_lines} 个有效行（过滤掉空行后）")


# 使用示例
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("请通过命令行参数提供文件名。")
        print(r"用法: python icmp_gap_detector.py .\ping_file\8-27-d3.txt")
        sys.exit(1)

    # 支持多个文件处理
    for filename in sys.argv[1:]:
        detect_icmp_gaps(filename)
