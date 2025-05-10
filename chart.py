# import matplotlib.pyplot as plt
# import numpy as np

# # Dữ liệu
# algorithms = ['BFS', 'A*', 'Beam', 'Backtracking', 'AND-OR', 'Q-Learning']
# levels = ['Level 1', 'Level 2', 'Level 3']

# time = [
#     [0.8, 1.2, 1.4],    # BFS
#     [1.0, 1.5, 1.4],    # A*
#     [0.9, 1.7, 2.0],    # Beam
#     [0.6, 0.77, 1.3],   # Backtracking
#     [2.0, 1.7, 4.4],    # AND-OR
#     [2160, 5700, 8200]  # Q-Learning (ms)
# ]

# visited = [
#     [157, 231, 245],
#     [131, 201, 228],
#     [142, 217, 243],
#     [146, 150, 240],
#     [146, 150, 240],
#     [49306, 85325, 107184]
# ]

# generated = [
#     [322, 470, 495],
#     [138, 211, 233],
#     [294, 445, 492],
#     [260, 241, 425],
#     [260, 241, 425],
#     [92180, 264895, 384658]
# ]

# path_len = [
#     [53, 73, 114],
#     [53, 73, 114],
#     [53, 73, 114],
#     [77, 117, 132],
#     [77, 117, 132],
#     [53, 73, 114]
# ]

# # Màu phân biệt Level
# colors = ['#4E79A7', '#F28E2B', '#E15759']

# # Hàm vẽ biểu đồ đẹp + chi tiết
# def plot_grouped_bar(data, title, ylabel, use_log=False):
#     x = np.arange(len(algorithms))
#     width = 0.25
#     fig, ax = plt.subplots(figsize=(14, 6))

#     # Vẽ 3 cột mỗi nhóm
#     values_lvl1 = [d[0] for d in data]
#     values_lvl2 = [d[1] for d in data]
#     values_lvl3 = [d[2] for d in data]

#     bars1 = ax.bar(x - width, values_lvl1, width, label='Level 1', color=colors[0])
#     bars2 = ax.bar(x,         values_lvl2, width, label='Level 2', color=colors[1])
#     bars3 = ax.bar(x + width, values_lvl3, width, label='Level 3', color=colors[2])

#     # Gán label lên từng cột
#     def annotate_bars(bars):
#         for bar in bars:
#             height = bar.get_height()
#             ax.annotate(f'{height:.0f}',
#                         xy=(bar.get_x() + bar.get_width() / 2, height),
#                         xytext=(0, 3),  # Đẩy lên 3 pixels
#                         textcoords="offset points",
#                         ha='center', va='bottom',
#                         fontsize=9)

#     annotate_bars(bars1)
#     annotate_bars(bars2)
#     annotate_bars(bars3)

#     # Tùy chỉnh biểu đồ
#     ax.set_ylabel(ylabel, fontsize=12)
#     ax.set_title(title, fontsize=15, fontweight='bold')
#     ax.set_xticks(x)
#     ax.set_xticklabels(algorithms, fontsize=11)
#     ax.legend(fontsize=10)

#     # Bật lưới
#     ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
#     if use_log:
#         ax.set_yscale("log")

#     plt.xticks(rotation=10)
#     plt.tight_layout()
#     plt.show()

# # Vẽ từng biểu đồ với tùy chọn log cho dữ liệu lệch nhiều
# plot_grouped_bar(time, "⏱ Time to Solve (ms)", "Time (ms)", use_log=True)
# plot_grouped_bar(visited, "🧭 Visited Nodes", "Nodes", use_log=True)
# plot_grouped_bar(generated, "🧠 Generated Nodes", "Nodes", use_log=True)
# plot_grouped_bar(path_len, "📏 Path Length", "Steps", use_log=False)
import matplotlib.pyplot as plt
import numpy as np

# Dữ liệu
algorithms = ['BFS', 'A*', 'Beam', 'Backtracking', 'AND-OR', 'Q-Learning']

time = [
    [0.8, 1.2, 1.4], [1.0, 1.5, 1.4], [0.9, 1.7, 2.0],
    [0.6, 0.77, 1.3], [2.0, 1.7, 4.4], [2160, 5700, 8200]
]
visited = [
    [157, 231, 245], [131, 201, 228], [142, 217, 243],
    [146, 150, 240], [146, 150, 240], [49306, 85325, 107184]
]
generated = [
    [322, 470, 495], [138, 211, 233], [294, 445, 492],
    [260, 241, 425], [260, 241, 425], [92180, 264895, 384658]
]
path_len = [
    [53, 73, 114], [53, 73, 114], [53, 73, 114],
    [77, 117, 132], [77, 117, 132], [53, 73, 114]
]

# Màu đẹp theo level
colors = ['#4E79A7', '#F28E2B', '#E15759']

# Tạo figure lớn chứa 4 biểu đồ con
fig, axs = plt.subplots(2, 2, figsize=(16, 10))
titles = ["⏱ Time to Solve (ms)", "🧭 Visited Nodes", "🧠 Generated Nodes", "📏 Path Length"]
ylabels = ["Time (ms)", "Nodes", "Nodes", "Steps"]
datasets = [time, visited, generated, path_len]
use_logs = [True, True, True, False]

def plot_subchart(ax, data, title, ylabel, use_log):
    x = np.arange(len(algorithms))
    width = 0.25

    val1 = [d[0] for d in data]
    val2 = [d[1] for d in data]
    val3 = [d[2] for d in data]

    bars1 = ax.bar(x - width, val1, width, label="Level 1", color=colors[0])
    bars2 = ax.bar(x,         val2, width, label="Level 2", color=colors[1])
    bars3 = ax.bar(x + width, val3, width, label="Level 3", color=colors[2])

    # Annotate số
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms, fontsize=10, rotation=10)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    if use_log:
        ax.set_yscale("log")
    ax.legend(fontsize=9)

# Vẽ từng biểu đồ con
for i, ax in enumerate(axs.flat):
    plot_subchart(ax, datasets[i], titles[i], ylabels[i], use_logs[i])

# Tối ưu bố cục
plt.suptitle("So sánh thuật toán AI qua 3 cấp độ", fontsize=16, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Lưu ảnh chất lượng cao
plt.savefig("algorithm_comparison.png", dpi=300)

# Hiển thị
plt.show()
