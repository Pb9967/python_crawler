import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from snownlp import SnowNLP
from matplotlib import font_manager

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

# 情感分析
def analyze_sentiment(text):
    if pd.isna(text) or text.strip() == '':  # 检查文本是否为空
        return '中性'  # 或者选择其他默认值
    s = SnowNLP(text)
    sentiment = s.sentiments  # 返回情感倾向值（0-1之间）
    if sentiment > 0.65:  # 正向阈值
        return '正面'
    elif sentiment < 0.35:  # 负向阈值
        return '负面'
    else:
        return '中性'

df['情感'] = df['影评内容'].apply(analyze_sentiment)

# 统计各电影的情感分布
sentiment_stats = df.groupby(['电影名称', '情感']).size().unstack(fill_value=0)
sentiment_stats['正面比例'] = sentiment_stats['正面'] / (sentiment_stats['正面'] + sentiment_stats['负面'] + sentiment_stats['中性'])
sentiment_stats['负面比例'] = sentiment_stats['负面'] / (sentiment_stats['正面'] + sentiment_stats['负面'] + sentiment_stats['中性'])
sentiment_stats['中性比例'] = sentiment_stats['中性'] / (sentiment_stats['正面'] + sentiment_stats['负面'] + sentiment_stats['中性'])

# 截断电影名称
truncated_names = [name if len(name) <= 5 else name[:5] + "..." for name in sentiment_stats.index]
# 绘制情感分布柱状图
plt.figure(figsize=(16, 9))  # 增加图表宽度
for i, movie in enumerate(sentiment_stats.index):
    plt.bar([i-0.2, i, i+0.2],
            [sentiment_stats.loc[movie, '正面比例'],
             sentiment_stats.loc[movie, '负面比例'],
             sentiment_stats.loc[movie, '中性比例']],
            width=0.2,
            label=['正面', '负面', '中性'],
            color=['green', 'red', 'blue'])

plt.title("各电影情感分布比例", fontproperties=font_prop)
plt.xlabel("电影名称", fontproperties=font_prop)
plt.ylabel("比例", fontproperties=font_prop)
plt.xticks(range(len(sentiment_stats.index)), truncated_names, rotation=45)  # 使用截断后的电影名称并旋转标签
plt.legend(labels=['正面', '负面', '中性'], prop=font_prop)
plt.tight_layout()
plt.show()
