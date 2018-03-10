#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os


#爬取页面
def getHTMLText(url):
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'   #模拟浏览器登陆
        headers = {'User-Agent': user_agent}
        
        r = requests.get(url, headers = headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ''


def get_info(url):
    html = getHTMLText(url)

    #创建 beautifulsoup 对象
    soup = BeautifulSoup(html,'lxml')

    items = soup.select('li.gl-item') 
    results = []

    #商品详情提取
    for item in items:
        item_url = 'http:' + item.find('div', class_='p-name').find('a')['href']
        name = (item.find('div', class_='p-name').find('em').string).strip()
        data_sku = item.find('div', class_='p-focus').find('a')['data-sku']
        price_url = 'http://p.3.cn/prices/mgets?skuIds=J_' + str(data_sku)
        price = requests.get(price_url).json()[0]['p']
        commit_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds=' + str(data_sku)
        comments = requests.get(commit_url).json()['CommentsCount'][0]['CommentCountStr']
        shop_name = item.find('div', class_='p-shop')['data-shop_name']
        results.append([name, item_url, data_sku, price, comments, shop_name])
    return results


#数据存储
def save_to_csv(results):
    path = 'E:/京东商品信息爬取/'
    if not os.path.exists(path):
        os.mkdir(path)
    with open(path + datetime.now().strftime('%Y-%m-%d %H-%M-%S') + '京东手机信息.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['商品', '链接', 'ID', '价格', '评论数', '店铺'])        
        writer.writerows(results)


def main():
    starttime = datetime.now()
    rooturl = 'https://list.jd.com/list.html?cat=9987,653,655'
    results = get_info(rooturl)

    #用时反馈
    endtime = datetime.now()
    time = (endtime - starttime).seconds
    print('本次爬取共计用时：%s s' % time)

    save_to_csv(results)