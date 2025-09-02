"""
模块名称: remove_empty_lines.py

该模块的目标：
    移除文件的空白行
  
作者: ych
修改历史:
    1. 2025/9/1 - 创建文件
"""
import sys


def remove_empty_lines(input_file, output_file):
    """
    读取输入文件，移除所有空行和仅含空白字符的行，保存到输出文件

    参数:
        input_file (str): 源文件路径
        output_file (str): 目标文件路径
    """
    try:
        with open(input_file, 'r') as f_in:
            # 读取所有行，同时保留行尾换行符
            lines = f_in.readlines()

        with open(output_file, 'w') as f_out:
            # 写入非空行 (只包含空白字符的行视为空行)
            for line in lines:
                if line.strip():  # 检查是否非空行
                    f_out.write(line)

        print(f"成功处理: 已移除空行并保存到 {output_file}")

    except FileNotFoundError:
        print(f"错误: 文件 '{input_file}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python script.py <输入文件路径> <输出文件路径>")
        print("示例: python script.py ./file/1.txt ./file/2.txt")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    remove_empty_lines(input_path, output_path)
