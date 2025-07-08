import os
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import font_manager
from collections import Counter

# 设置中文和特殊字符字体
font_path = '字体/msyh.ttc'  # 微软雅黑字体路径
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'Microsoft YaHei'  # 设置全局字体为微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def generate_word_cloud(movie_name, reviews):
    # 合并所有影评文本
    text = ' '.join(reviews)
    # 分词
    words = jieba.lcut(text)
    # 统计词频
    word_counts = Counter(words)
    # 生成词云
    wc = WordCloud(
        font_path=font_path,
        background_color='white',
        width=800,
        height=400,
        max_words=200
    )
    wc.generate_from_frequencies(word_counts)
    # 绘制词云图
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'{movie_name}影评词云图', fontproperties=font_prop)
    plt.tight_layout()
    plt.show()

def main():
    folder_path = "clean"
    movie_name = '你的名字。 君の名は。.txt'
    # movie_name = input("电影文件：")
    file_path = os.path.join(folder_path, f"{movie_name}")
    if not os.path.exists(file_path):
        print(f"错误：未找到电影 {movie_name} 的数据文件。")
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 提取影评内容
        reviews = []
        lines = content.split('\n')
        for line in lines:
            if line.startswith('review_'):
                if ' 内容：' in line:
                    review = line.split(' 内容：')[1]
                    reviews.append(review)
        if not reviews:
            print("错误：文件中未找到影评数据。")
            return
        generate_word_cloud(movie_name, reviews)

if __name__ == "__main__":
    main()