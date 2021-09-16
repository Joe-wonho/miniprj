from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
client = MongoClient('localhost', 27017)
db = client.dbsparta
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
url = 'https://movie.naver.com/movie/running/current.naver'
data = requests.get(url,headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')
trs = soup.select('#content > div.article > div:nth-child(1) > div.lst_wrap > ul > li')
#genre = []
doc ={}
for tr in trs:
    doc = {}
    doc['img_url'] = tr.select_one('div > a > img')['src']
    doc['title'] = tr.select_one('div > a > img')['alt']
    doc['grade'] = tr.select_one('dl > dd.star > dl.info_star > dd > div > a > span.num').text
    doc['count'] = 0
    genre_list = tr.select('dl > dd:nth-child(3) > dl > dd:nth-child(2) > span.link_txt')
    for text in genre_list:
        list = []
        for i in text:
            #if type(i)=="<class 'bs4.element.Comment'>":
            if str(type(i))=="<class 'bs4.element.Tag'>":
                list.append(str(i).split('">')[1].split('<')[0])
        #genre.append(list)
    doc['genre'] = list
    db.movie_info.insert_one(doc)



