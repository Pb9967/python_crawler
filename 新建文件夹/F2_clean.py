import os
import re
import jieba
from collections import defaultdict

# 停用词表路径
stopwords_path = 'stopwords-master/hit_stopwords.txt'

# 读取停用词
def read_stopwords(stopwords_path):
    stopwords = set()
    with open(stopwords_path, 'r', encoding='utf-8') as file:
        for line in file:
            stopwords.add(line.strip())
    return stopwords

# 处理单个文件
def process_file(file_path, stopwords):
    data = defaultdict(list)
    scores = []
    reviews = []
    movie_details = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # 提取电影详情
        movie_details['电影名称'] = re.search(r'电影名称: (.+)', content).group(1)
        movie_details['导演'] = re.search(r'导演: (.+)', content).group(1)
        movie_details['类型'] = re.search(r'类型: (.+)', content).group(1)
        movie_details['上映时间'] = re.search(r'上映时间: (.+)', content).group(1)
        movie_details['国家/地区'] = re.search(r'国家/地区: (.+)', content).group(1)
        # 提取影评
        reviews_data = re.findall(r'review_\d+:评分：(\d+) 内容：(.+)', content)
        for score, review in reviews_data:
            scores.append(int(score))
            # 分词并去除停用词
            words = jieba.lcut(review)
            filtered_words = [word for word in words if word not in stopwords and word.strip() != '']
            data['影评'].append(' '.join(filtered_words))
    data['评分'] = scores
    data['电影详情'] = movie_details
    return data

# 处理文件夹内的所有文件
def process_folder(input_folder, output_folder, stopwords):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.txt'):
            file_path = os.path.join(input_folder, file_name)
            data = process_file(file_path, stopwords)
            # 写入处理后的数据
            output_path = os.path.join(output_folder, file_name)
            with open(output_path, 'w', encoding='utf-8') as file:
                # 写入电影详情
                file.write(f'电影名称: {data["电影详情"]["电影名称"]}\n')
                file.write(f'导演: {data["电影详情"]["导演"]}\n')
                file.write(f'类型: {data["电影详情"]["类型"]}\n')
                file.write(f'上映时间: {data["电影详情"]["上映时间"]}\n')
                file.write(f'国家/地区: {data["电影详情"]["国家/地区"]}\n\n')
                file.write("影评:\n")
                # 写入影评和评分
                for i in range(len(data['影评'])):
                    file.write(f'review_{i + 1}:评分：{data["评分"][i]} 内容：{data["影评"][i]}\n')
            print(f'文件处理完成：{file_name}')

# 主程序
if __name__ == "__main__":
    input_folder = 'reviews_score'  # 输入文件夹路径
    output_folder = 'clean'  # 输出文件夹路径
    stopwords = read_stopwords(stopwords_path)
    process_folder(input_folder, output_folder, stopwords)
    print("所有文件处理完成！")