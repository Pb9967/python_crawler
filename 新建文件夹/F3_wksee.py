import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from tabulate import tabulate

# 设置中文和特殊字符字体
font_path = '字体/msyh.ttc'  # 微软雅黑字体路径
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'Microsoft YaHei'  # 设置全局字体为微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 数据加载
data = []
folder_path = "clean"
for file_name in os.listdir(folder_path):
    if file_name.endswith(".txt"):
        movie_name = file_name.replace(".txt", "")
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 假设影评部分的格式为"review_X:评分：X 内容：影评内容"
            reviews = content.split("review_")
            for review in reviews[1:]:  # 跳过第一个空元素
                if "评分：" in review:
                    # 分割评分和内容
                    score_part, text_part = review.split(" 内容：", 1)
                    score = score_part.split("评分：")[1].strip()
                    text = text_part.strip()
                    data.append([movie_name, float(score), text])

# 创建DataFrame
df = pd.DataFrame(data, columns=["电影名称", "评分", "影评内容"])

# 基本统计分析
stats = df.groupby("电影名称")["评分"].agg(["min", "max", "mean", "count"])
stats['mean'] = stats['mean'].round(2)  # 保留两位小数

# 使用 tabulate 格式化输出
print(tabulate(stats, headers='keys', tablefmt='pretty', showindex=True))

# 绘制评分分布图
# 截断电影名称
truncated_names = [name if len(name) <= 10 else name[:10] + "..." for name in df["电影名称"].unique()]
name_map = {name: trunc_name for name, trunc_name in zip(df["电影名称"].unique(), truncated_names)}
df["截断名称"] = df["电影名称"].map(name_map)


# 创建一个图形和两个子图
fig, axs = plt.subplots(2, 1, figsize=(15, 10))  # 创建一个图形和两个子图

# 绘制评分分布图
sns.boxplot(x="截断名称", y="评分", data=df, ax=axs[0])
axs[0].set_title("各电影评分分布", fontproperties=font_prop)
axs[0].set_xlabel("电影名称", fontproperties=font_prop)
axs[0].set_ylabel("评分", fontproperties=font_prop)
axs[0].tick_params(axis='x', rotation=45)

# 绘制平均评分柱状图
mean_scores = df.groupby("电影名称")["评分"].mean().sort_values(ascending=False)
truncated_names = [name if len(name) <= 10 else name[:10] + "..." for name in mean_scores.index]
sns.barplot(x=truncated_names, y=mean_scores.values, ax=axs[1])
axs[1].set_title("各电影平均评分", fontproperties=font_prop)
axs[1].set_xlabel("电影名称", fontproperties=font_prop)
axs[1].set_ylabel("平均评分", fontproperties=font_prop)
axs[1].tick_params(axis='x', rotation=45)

plt.tight_layout()  # 自动调整布局
plt.show()