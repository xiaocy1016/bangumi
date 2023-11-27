import requests

from lxml import etree

url = "https://bangumi.tv/subject/381825"

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

response = requests.request("GET", url, headers=headers, data=payload)

content = response.text  # 获取HTML的内容
html = etree.HTML(content)  # 分析HTML，返回DOM根节点


t = html.xpath('//*[@id="headerSubject"]/h1/a/text()');
print(t)
