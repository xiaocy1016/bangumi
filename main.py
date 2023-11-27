import json
import time

import chardet
import requests
from lxml import etree
import traceback

#  基础信息
BANGUMI_URL = "https://bangumi.tv"  # BANGUMI网址
ANIME_URL = BANGUMI_URL + "/anime/browser?sort=rank"  # 动画列表网址
ANIME_PAGE = 963  # 动画总页数
RESTORE_FILE = "./data"  # 存储位置


#  解析动画列表页面获取动画id
def analysis_anime_list_html(html):
    html = etree.HTML(html)
    a_elements = html.xpath('//ul[@id="browserItemList"]/li/a')
    href_attributes = [a.get('href') for a in a_elements]
    return href_attributes


def get_anime_list():
    headers = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
      'Cookie': 'chii_sec_id=oqbp7MCFIz7CZ6aGYBWAP%2Bv3Cvk6bYD4Qp4NUg; chii_theme=light; _ga=GA1.1.1267503224.1700546721; chii_sid=wjs4uj; __utma=1.1267503224.1700546721.1700552787.1700619312.4; __utmc=1; __utmz=1.1700619312.4.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; __utmb=1.3.10.1700619312; _ga_1109JLGMHN=GS1.1.1700619312.4.1.1700619337.0.0.0',
      'Referer': 'https://bangumi.tv/anime',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'same-origin',
      'Sec-Fetch-User': '?1',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
      'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Windows"'
    }
    anime_list = []
    total_page = ANIME_PAGE
    # total_page = 1
    page = 1
    while page <= total_page:
        print("now the page: ", page)
        payload = {"page": page}
        try:
            response = requests.request("GET", ANIME_URL, headers=headers, params=payload)
            anime_list.extend(analysis_anime_list_html(response.text))
            page = page + 1
        except Exception as e:
            traceback.print_exc()
            time.sleep(60)
        finally:
            time.sleep(1)
    return anime_list


#  解析动画详情页面获取动画信息
def analysis_anime_info_html(html):
    html = etree.HTML(html)  # ??HTML???DOM???
    anime_info = {}

    #  动画名称
    name_html = html.xpath('// *[ @ id = "headerSubject"] / h1 / a')
    name = name_html[0].text
    anime_info["name"] = name

    #  动画基础信息
    infobox_html = html.xpath('//div[@class="infobox_container"]/ul/li')
    info_box = {}
    for child in infobox_html:
        tip = child.xpath('span')[0].text
        if len(child.xpath('a/text()')) > 0:
            value = child.xpath('a/text()')
        else:
            value = child.xpath('span/following-sibling::text()')[0]
        info_box[tip] = value
    anime_info["info_box"] = info_box

    #  用户态度
    tip_id = html.xpath('//div[@id="subjectPanelCollect"]/span[@class="tip_i"]/a')
    attitude = []
    for child in tip_id:
        attitude.append(child.text)
    anime_info["attitude"] = attitude

    #  动画标签
    html_label = html.xpath('//div[@class="subject_tag_section"]/div[@class="inner"]/a')
    # html_label = html.xpath('//div[@class="subject_tag_section"]')
    anime_labels = []
    for child in html_label:
        label_html = child.xpath('span')
        if len(label_html) == 0:
            continue
        number_html = child.xpath('small')
        if len(number_html) == 0:
            continue
        anime_labels.append({"label": label_html[0].text, "number": number_html[0].text})
    anime_info["label"] = anime_labels

    #  动画评分
    scores = {}
    score_html = html.xpath('//div[@class="global_score"]/span[@class="number"]')
    scores['global_score'] = score_html[0].text

    #  动画评分详情
    score_chart_html = html.xpath('//ul[@class="horizontalChart"]/li')
    score_chart = []
    for child in score_chart_html:
        label_html = child.xpath('a/span[@class="label"]')
        label = label_html[0].text
        count_html = child.xpath('a/span[@class="count"]')
        count = count_html[0].text
        score_chart.append({"label": label, "count": count})
    scores["score_chart"] = score_chart
    anime_info["score"] = scores

    #  动画概览
    summary = html.xpath('//div[@id="subject_summary"]/text()')
    anime_info["summary"] = summary

    #  角色介绍
    user_intros = []
    user_intros_html = html.xpath('//ul[@id="browserItemList"]/li/div[@class="userContainer"]')
    for child in user_intros_html:
        user_intro = {"job": child.xpath('div/span/small/span/text()')[0], "name": child.xpath('strong/a/@title')[0],
                      "cv": child.xpath('div/span/a/text()')}
        user_intros.append(user_intro)
    anime_info["user_intros"] = user_intros

    #  吐槽部分
    anime_info["complaints"] = html.xpath('//p[@class="comment"]/text()')

    #  评论部分
    anime_info["comments"] = html.xpath('//div[@class="item clearit"]/div[@class="entry"]/div[@class="content"]/text()')
    return anime_info


def get_anime_info(anime_url):
    payload = {}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'chii_sec_id=oqbp7MCFIz7CZ6aGYBWAP%2Bv3Cvk6bYD4Qp4NUg; chii_theme=light; _ga=GA1.1.1267503224.1700546721; chii_sid=wjs4uj; __utma=1.1267503224.1700546721.1700552787.1700619312.4; __utmc=1; __utmz=1.1700619312.4.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; __utmb=1.5.10.1700619312; _ga_1109JLGMHN=GS1.1.1700619312.4.1.1700620115.0.0.0',
        'Referer': 'https://bangumi.tv/anime/browser',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    url = BANGUMI_URL + anime_url
    anime_info = {}
    try:
        response = requests.request("GET", url=url, headers=headers, data=payload)
        encoding = chardet.detect(response.content)['encoding']
        response.encoding = encoding
        anime_info = analysis_anime_info_html(response.text)
    except Exception as e:
        traceback.print_exc()
        time.sleep(60)
    finally:
        time.sleep(1)
    return anime_info


def bangumi_anime_spider():
    anime_list = get_anime_list()
    for i, anime_url in enumerate(anime_list):
        print(i, anime_url)
        anime_info = get_anime_info(anime_url)
        if anime_info:
            save_path = RESTORE_FILE + anime_url + ".json"
            with open(save_path, 'w', encoding='utf-8') as json_file:
                json.dump(anime_info, json_file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("中文输出没问题")
    print("こんにちは、世界！(Konnichiwa, Sekai!)")
    # get_anime_info("/subject/253")
    bangumi_anime_spider()


# 2650 /subject/10435
# 2651 /subject/180775
# 2652 /subject/281272
# 2653 /subject/74901
# 2654 /subject/69942
# 2655 /subject/120369
# 2656 /subject/159365
# 2657 /subject/121108
# 2658 /subject/10160
# 2659 /subject/130452
# 2660 /subject/14738




# Traceback (most recent call last):
#   File "E:\school\nju\研一上\云计算\bangumi\main.py", line 167, in get_anime_info
#     anime_info = analysis_anime_info_html(response.text)
#   File "E:\school\nju\研一上\云计算\bangumi\main.py", line 68, in analysis_anime_info_html
#     name = name_html[0].text
# IndexError: list index out of range