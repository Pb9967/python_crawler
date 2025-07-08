import os
import requests
from lxml import html
from parsel import Selector

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'}

def crawl_douban_movie_cast(movie_id):
    # 电影详情页URL
    detail_url = f'https://movie.douban.com/subject/{movie_id}'
    try:
        with requests.get(detail_url, headers=header, timeout=10) as response:
            response.raise_for_status()
            # 使用 response.content 和指定编码
            doc = html.fromstring(response.content.decode('utf-8'))
            # 获取主演信息
            cast = doc.xpath('//a[@rel="v:starring"]/text()')
            cast = ", ".join(cast) if cast else "未知主演"
            return cast
    except requests.exceptions.RequestException as e:
        print(f"获取电影详情页错误: {e}")
        return "未知主演"

def append_cast_to_file(file_path, cast):
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f'主演: {cast}\n')

if __name__ == "__main__":
    folder_path = 'reviews_score'  # 文件夹路径
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            # 提取电影ID
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # 假设文件中包含"电影ID: XXX"格式的内容
                import re
                match = re.search(r'电影ID: (\d+)', content)
                if match:
                    movie_id = match.group(1)
                    # 获取主演信息
                    cast = crawl_douban_movie_cast(movie_id)
                    # 将主演信息追加到文件中
                    append_cast_to_file(file_path, cast)
                    print(f'已将主演信息追加到文件: {file_name}')
                else:
                    print(f'无法找到电影ID: {file_name}')