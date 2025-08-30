"""
模块名称: FedGMH_ablation_study_pdf.py

该模块的目标：
    生成论文中消融研究的图片，
  
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
    "figure_size": (10, 6),
    "dpi": 1200,
    # "line_width": 1,
    "ci_alpha": 0.2,
    "font_settings": {
        "family": "Times New Roman",  # 使用通用字体
        "size": 14
    },
    # "color_palette": {
    #     "FedGMH": ["#D84A38", "#F0CFCD"],
    #     "GMH-o": ["#0A0AEB", "#CCCCF7"],
    #     "GMH-a": ["#E8B157", "#FAEED3"],
    #     "GMH-oa": ["#4C7E32", "#D5E3D0"]
    # },
    "color_palette": {
        "FedGMH": ["#D84A38", "#E8A197"],  # 原背景色 #F0CFCD → #E8A197 (加深)
        "GMH-o": ["#0A0AEB", "#9C9CF5"],   # 原背景色 #CCCCF7 → #9C9CF5 (加深)
        "GMH-a": ["#E8B157", "#E0C98A"],   # 原背景色 #FAEED3 → #E0C98A (加深)
        "GMH-oa": ["#4C7E32", "#A8C298"]   # 原背景色 #D5E3D0 → #A8C298 (加深)
    },
    "grid_settings": {
        "visible": True,  # 显示网格
        "linestyle": ':',  # 虚线样式 (可选项: '-', '--', '-.', ':')
        "alpha": 0.4,  # 透明度
    },
    # 添加线型配置
    "line_styles": {
        "GMH-o": "--",  # 虚线
        "GMH-a": "-.",  # 点划线
        "GMH-oa": ":",  # 点线
        "FedGMH": "-"  # 实线
    },
}

# ================= 关键设置：确保PDF可编辑 =================
# 设置PDF字体类型为42（可编辑字体）
plt.rcParams['pdf.fonttype'] = 42
# 设置PostScript字体类型为42（兼容性）
plt.rcParams['ps.fonttype'] = 42
# 确保使用矢量格式而非位图
plt.rcParams['image.composite_image'] = False


# ================= 数据处理 =================
def load_algorithm_data(root_folder):
    """
    加载包含多个算法文件夹的根目录
    每个算法文件夹包含5个CSV文件
    """
    algorithm_data = {}

    # 指定要处理的算法文件夹列表
    target_algorithms = ["GMH-o", "GMH-a", "GMH-oa", "FedGMH"]

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
            matrix = np.array(all_runs)
            algorithm_data[algo_dir] = {
                "mean": matrix.mean(axis=0),
                "std": matrix.std(axis=0),
                "raw_data": matrix  # 保留原始数据供后续分析
            }

    return algorithm_data


# ================= 绘图函数 =================
def plot_with_confidence_interval(data_dict, output_path):
    plt.figure(figsize=PLOT_CONFIG["figure_size"])
    plt.rc('font', family='SimSun', size=12)  # 使用宋体支持中文显示
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    # 生成全局轮数坐标
    x = np.arange(301)

    # 按指定顺序绘制曲线
    plot_order = [
        "GMH-o",
        "GMH-a",
        "GMH-oa",
        "FedGMH"
    ]

    for algo_name in plot_order:
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
        line_width = 2 if algo_name == "FedGMH" else 1
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

    # ===== 网格配置核心代码 =====
    grid_config = PLOT_CONFIG["grid_settings"]
    plt.grid(
        visible=grid_config["visible"],
        linestyle=grid_config["linestyle"],
        alpha=grid_config["alpha"],
    )

    # 标签设置
    plt.xlabel("全局轮次", fontsize=14, labelpad=10, fontfamily='SimSun')
    plt.ylabel("准确率", fontsize=14, labelpad=10, fontfamily='SimSun')

    # 图例设置
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
            text.set_color("#D84A38")

    # 保存为PDF（可编辑）
    plt.savefig(output_path,
                format='pdf',  # 修改为PDF格式
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
    plot_with_confidence_interval(processed_data, "./file/ablation_study.pdf")  # 修改为PDF扩展名
