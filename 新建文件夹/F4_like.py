import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from matplotlib import font_manager

# 设置中文和特殊字符字体
font_path = '字体/msyh.ttc'  # 微软雅黑字体路径
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'Microsoft YaHei'  # 设置全局字体为微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 数据加载
data = []
folder_path = "reviews_score"
movie_features = {}  # 用于存储电影特征

for file_name in os.listdir(folder_path):
    if file_name.endswith(".txt"):
        movie_name = file_name.replace(".txt", "")
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取电影特征信息（这里仅提取类型、导演等，具体根据文件格式调整）
            lines = content.split('\n')
            features = {}
            for line in lines:
                if line.startswith('类型:'):
                    features['类型'] = line.replace('类型:', '').strip()
                elif line.startswith('导演:'):
                    features['导演'] = line.replace('导演:', '').strip()
                elif line.startswith('主演:'):
                    features['主演'] = line.replace('主演:', '').strip()
                # 可以继续添加其他特征提取
            movie_features[movie_name] = features

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

# 将电影特征转换为适合计算相似度的格式
# 创建一个包含所有电影特征的DataFrame
feature_df = pd.DataFrame.from_dict(movie_features, orient='index')
# 填充缺失值
feature_df = feature_df.fillna('')
# 将特征合并为一个字符串
feature_df['combined_features'] = feature_df.apply(
    lambda row: ' '.join([str(row['类型']), str(row['导演']), str(row['主演'])]), axis=1)

# 使用TF-IDF向量化电影特征
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(feature_df['combined_features'])

# 计算余弦相似度
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# 获取所有电影名称
movie_names = feature_df.index.tolist()

# 获取相似电影的函数
def get_similar_movies(movie_name, cosine_sim=cosine_sim, movie_names=movie_names):
    # 获取电影的索引
    idx = movie_names.index(movie_name)
    # 获取该电影与其他电影的相似度
    sim_scores = list(enumerate(cosine_sim[idx]))
    # 按相似度降序排序
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # 获取最相似的10部电影（去掉自身）
    similar_movies = [movie_names[i] for i, _ in sim_scores[1:11]]
    return similar_movies

# 随机选择一部电影作为喜欢的电影
liked_movie = np.random.choice(movie_names)
print(f"您可能喜欢的电影是：{liked_movie}")
# liked_movie = input('输入您喜欢的电影名称: ')

# 获取推荐电影及其评分
similar_movies = get_similar_movies(liked_movie)
print("基于这部电影，推荐以下相似电影及其评分：")
i=1
for movie in similar_movies:
    # 获取电影的平均评分
    avg_score = df[df['电影名称'] == movie]['评分'].mean()
    print(f"{i}.{movie}: 评分 {avg_score:.2f}")
    i+=1
