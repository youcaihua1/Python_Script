"""
模块名称: FedGMH_ten_algorithms_pdf.py

该模块的目标：
    生成论文中研究的图片，支持十条曲线对应十个算法。（这不是论文中的图片，使用了平均的计算方式）
  
作者: ych
修改历史:
    1. 2025/8/29 - 创建文件
"""
# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
import os
import csv

# ================= 配置参数 =================
PLOT_CONFIG = {
    "figure_size": (12, 8),  # 增大图像尺寸以容纳更多曲线
    "dpi": 1200,
    "ci_alpha": 0.2,
    "font_settings": {
        "family": "Times New Roman",
        "size": 14
    },
    # 为十个算法定义颜色配置
    "color_palette": {
        "Ditto": ["#1f77b4", "#aec7e8"],  # 蓝色系
        "FedAMP": ["#ff7f0e", "#ffbb78"],  # 橙色系
        "FedCP": ["#2ca02c", "#98df8a"],  # 绿色系
        "FedFomo": ["#d62728", "#ff9896"],  # 红色系
        "FedGH": ["#9467bd", "#c5b0d5"],  # 紫色系
        "FedPer": ["#8c564b", "#c49c94"],  # 棕色系
        "FedRep": ["#e377c2", "#f7b6d2"],  # 粉色系
        "FedROD": ["#7f7f7f", "#c7c7c7"],  # 灰色系
        "LG-FedAvg": ["#bcbd22", "#dbdb8d"],  # 黄绿色系
        "FedGMH": ["#17becf", "#9edae5"]  # 青色系
    },
    "grid_settings": {
        "visible": True,
        "linestyle": ':',
        "alpha": 0.4,
    },
    # 为十个算法定义线型配置
    "line_styles": {
        "Ditto": "-",  # 实线
        "FedAMP": "--",  # 虚线
        "FedCP": "-.",  # 点划线
        "FedFomo": ":",  # 点线
        "FedGH": (0, (5, 5)),  # 长虚线
        "FedPer": (0, (5, 1)),  # 长短交替虚线
        "FedRep": (0, (3, 1, 1, 1)),  # 点划线变体
        "FedROD": (0, (1, 1)),  # 密集点线
        "LG-FedAvg": (0, (5, 1, 5, 1, 1, 1)),  # 复杂虚线
        "FedGMH": "-"  # 实线，突出显示
    },
}

# ================= 关键设置：确保PDF可编辑 =================
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['image.composite_image'] = False


# ================= 数据处理 =================
def load_algorithm_data(root_folder):
    """
    加载包含多个算法文件夹的根目录
    每个算法文件夹包含多个CSV文件
    """
    algorithm_data = {}

    # 指定要处理的十个算法文件夹列表
    target_algorithms = [
        "Ditto", "FedAMP", "FedCP", "FedFomo", "FedGH",
        "FedPer", "FedRep", "FedROD", "LG-FedAvg", "FedGMH"
    ]

    # 遍历算法文件夹
    for algo_dir in os.listdir(root_folder):
        algo_path = os.path.join(root_folder, algo_dir)
        # 只处理目标算法文件夹
        if os.path.isdir(algo_path) and algo_dir in target_algorithms:
            all_runs = []

            # 加载该算法所有CSV文件
            for csv_file in os.listdir(algo_path):
                if csv_file.endswith(".csv"):
                    file_path = os.path.join(algo_path, csv_file)
                    with open(file_path, 'r') as f:
                        reader = csv.reader(f)
                        next(reader)  # 跳过标题行
                        accuracy = [float(row[0]) for row in reader]
                        all_runs.append(accuracy)

            # 转换为numpy数组并计算统计量
            if all_runs:  # 确保有数据
                matrix = np.array(all_runs)
                algorithm_data[algo_dir] = {
                    "mean": matrix.mean(axis=0),
                    "std": matrix.std(axis=0),
                    "raw_data": matrix  # 保留原始数据供后续分析
                }
            else:
                print(f"警告: 文件夹 {algo_dir} 中没有CSV文件")

    # 检查是否所有目标算法都有数据
    for algo in target_algorithms:
        if algo not in algorithm_data:
            print(f"警告: 未找到算法 {algo} 的数据")

    return algorithm_data


# ================= 绘图函数 =================
def plot_with_confidence_interval(data_dict, output_path):
    plt.figure(figsize=PLOT_CONFIG["figure_size"])
    plt.rc('font', family='SimSun', size=12)
    plt.rcParams['axes.unicode_minus'] = False

    # 生成全局轮数坐标
    x = np.arange(301)

    # 按指定顺序绘制曲线
    plot_order = [
        "Ditto", "FedAMP", "FedCP", "FedFomo", "FedGH",
        "FedPer", "FedRep", "FedROD", "LG-FedAvg", "FedGMH"
    ]

    for algo_name in plot_order:
        if algo_name not in data_dict:
            print(f"跳过 {algo_name}，无数据")
            continue

        # 获取颜色配置
        color = PLOT_CONFIG["color_palette"][algo_name]

        # 绘制置信区间
        plt.fill_between(x,
                         data_dict[algo_name]["mean"] - data_dict[algo_name]["std"],
                         data_dict[algo_name]["mean"] + data_dict[algo_name]["std"],
                         color=color[1],
                         alpha=PLOT_CONFIG["ci_alpha"])

        # 绘制均值曲线
        line_style = PLOT_CONFIG["line_styles"][algo_name]
        line_width = 2 if algo_name == "FedGMH" else 1.5  # FedGMH加粗显示
        plt.plot(x, data_dict[algo_name]["mean"],
                 color=color[0],
                 linestyle=line_style,
                 linewidth=line_width,
                 label=algo_name)

    # 坐标轴设置
    plt.xticks(np.arange(0, 301, 50))
    plt.yticks(np.arange(0, 0.81, 0.1))
    plt.xlim(0, 301)
    plt.ylim(0, 0.8)

    # 网格配置
    grid_config = PLOT_CONFIG["grid_settings"]
    plt.grid(
        visible=grid_config["visible"],
        linestyle=grid_config["linestyle"],
        alpha=grid_config["alpha"],
    )

    # 标签设置
    plt.xlabel("全局轮次", fontsize=14, labelpad=10, fontfamily='SimSun')
    plt.ylabel("准确率", fontsize=14, labelpad=10, fontfamily='SimSun')

    # 图例设置 - 调整为两列以适应更多算法
    legend = plt.legend(loc='lower right',
                        bbox_to_anchor=(1.0, 0.0),
                        ncol=2,
                        fontsize=10,
                        framealpha=0.9,
                        prop={'family': 'Times New Roman'})

    # 设置FedGMH图例项样式
    for text in legend.get_texts():
        if text.get_text() == "FedGMH":
            text.set_fontweight('bold')
            text.set_color("#17becf")

    # 保存为PDF（可编辑）
    plt.savefig(output_path,
                format='pdf',
                dpi=PLOT_CONFIG["dpi"],
                bbox_inches='tight',
                metadata={'Creator': 'Matplotlib', 'Producer': 'Matplotlib PDF Output'})
    plt.close()


# ================= 使用示例 =================
if __name__ == "__main__":
    # 1. 设置数据文件夹路径
    DATA_ROOT = "./csv_folder"

    # 2. 加载并处理数据
    processed_data = load_algorithm_data(DATA_ROOT)

    # 3. 生成图表（保存为PDF）
    plot_with_confidence_interval(processed_data, "./file/ten_algorithms.pdf")
