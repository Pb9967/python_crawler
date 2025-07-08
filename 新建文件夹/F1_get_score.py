import requests
import time
from lxml import html
from parsel import Selector
import os

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'}

def crawl_douban_movie_details(movie_id):
    # 电影详情页URL
    detail_url = f'https://movie.douban.com/subject/{movie_id}'
    try:
        with requests.get(detail_url, headers=header, timeout=10) as response:
            response.raise_for_status()
            # 使用 response.content 和指定编码
            doc = html.fromstring(response.content.decode('utf-8'))
            # 获取电影名称
            movie_name = doc.xpath('//span[@property="v:itemreviewed"]/text()')
            movie_name = movie_name[0].strip() if movie_name else "未知电影"
            # 获取导演信息
            director = doc.xpath('//a[@rel="v:directedBy"]/text()')
            director = director[0].strip() if director else "未知导演"
            # 获取电影类型
            genres = doc.xpath('//span[@property="v:genre"]/text()')
            genres = ", ".join(genres) if genres else "未知类型"
            # 获取上映时间
            release_date = doc.xpath('//span[@property="v:initialReleaseDate"]/text()')
            release_date = release_date[0].strip() if release_date else "未知上映时间"
            # 获取制片国家/地区
            country = doc.xpath('//span[@class="pl"][text()="制片国家/地区:"]/following-sibling::text()[1]')
            country = country[0].strip() if country else "未知国家/地区"
            return {
                "电影名称": movie_name,
                "导演": director,
                "类型": genres,
                "上映时间": release_date,
                "国家/地区": country
            }
    except requests.exceptions.RequestException as e:
        print(f"获取电影详情页错误: {e}")
        return {
            "电影名称": "未知电影",
            "导演": "未知导演",
            "类型": "未知类型",
            "上映时间": "未知上映时间",
            "国家/地区": "未知国家/地区"
        }

def crawl_douban_reviews(movie_id, pages=6):
    # 评论页URL
    base_url = f'https://movie.douban.com/subject/{movie_id}/comments'
    reviews_data = []
    scores_data = []
    # 获取电影详情
    movie_details = crawl_douban_movie_details(movie_id)
    for page in range(0, pages):
        url = f'{base_url}?start={page * 20}&limit=20&status=P&sort=new_score'
        try:
            with requests.get(url, headers=header, timeout=10) as response:
                response.raise_for_status()
                # 使用 response.content 和指定编码
                selector = Selector(text=response.content.decode('utf-8'))
                comments = selector.css('.comment-item')
                for comment in comments:
                    score = comment.css('.comment-info .rating::attr(class)').get()
                    if score:
                        # 处理评分的类名，提取评分值
                        score_parts = score.split()
                        if len(score_parts) >= 1:
                            allstar_part = score_parts[0]
                            if allstar_part.startswith('allstar'):
                                score_value = int(allstar_part.replace('allstar', ''))
                                if score_value >= 10 and score_value <=50:  # 假设评分是 1-5 星，对应 10-50
                                    score_value = score_value // 10
                            else:
                                score_value = None
                        else:
                            score_value = None
                        scores_data.append(score_value)
                    else:
                        scores_data.append(None)
                    short = comment.css('.short::text').get()
                    if short:
                        short = short.strip()
                        if short not in reviews_data:
                            reviews_data.append(short)
            time.sleep(1)  # 添加延迟
        except requests.exceptions.RequestException as e:
            print(f"获取评论页 {page + 1} 错误: {e}")
            continue
    return {**movie_details, "影评": reviews_data, "评分": scores_data}

def write_reviews(movie_id, movie_data):
    if not os.path.exists('reviews_score'):
        os.makedirs('reviews_score')
    with open(rf'reviews_score\{movie_data["电影名称"]}.txt', 'w', encoding='utf-8', errors='ignore') as file:
        file.write(f'电影名称: {movie_data["电影名称"]}\n')
        file.write(f'电影ID: {movie_id}\n')
        file.write(f'导演: {movie_data["导演"]}\n')
        file.write(f'类型: {movie_data["类型"]}\n')
        file.write(f'上映时间: {movie_data["上映时间"]}\n')
        file.write(f'国家/地区: {movie_data["国家/地区"]}\n\n')
        file.write("影评:\n")
        i = 1
        for review, score in zip(movie_data["影评"], movie_data["评分"]):
            file.write(f'\nreview_{i}:')
            if score is not None:
                file.write(f'评分：{score*2}')
            file.write(f' 内容：{review}\n')
            i += 1
    print(rf'影评数据保存至"reviews_score\{movie_data["电影名称"]}.txt"')

if __name__ == "__main__":
    # 输入多个电影ID，用逗号分隔
    movie_ids = input("请输入多个电影ID，用逗号分隔: ").split(',')
    movie_ids = [id.strip() for id in movie_ids]
    for movie_id in movie_ids:
        print(rf'正在提取电影ID为{movie_id}的影评数据......')
        movie_data = crawl_douban_reviews(movie_id)
        write_reviews(movie_id, movie_data)
