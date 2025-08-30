"""
模块名称: eps_script.py

该模块的目标：
    学习matplotlib
  
作者: ych
修改历史:
    1. 2025/8/29 - 创建文件
"""
import matplotlib.pyplot as plt

# 生成图表
plt.plot([1, 2, 3], [4, 5, 6], label='Data Line')
plt.xlabel('X Axis', fontsize=12)
plt.ylabel('Y Axis', fontsize=12)

# 导出为 EPS（文字/图形可编辑）
plt.savefig("./file/output.eps", format='eps', bbox_inches='tight')
plt.savefig("./file/output.pdf")  # 文字保留可编辑属性
