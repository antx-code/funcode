#-*-coding:utf8-*-

import requests
import json
import csv


# class TaobaoSpider():
#
#
#     def __init__(self):
#         '''
#
#         Initialize the fuctions which we will use in the spider.
#
#         '''
#         self.get_search_content()
#         self.get_ajax_html(self.get_search_content())
#         self.get_content(self.get_search_content())
#         self.write_file(self.get_content())

def get_ajax_html(search_content):

    '''

    From the destination html get the json url which the content we need.

    '''
    ajax_url = 'https://s.taobao.com/api?_ksTS=&ajax=true&m=customized&q=' + str(search_content)
    return ajax_url

def get_content(des_url):
    '''

    We will get the content which we want to search and we need that include the
    goods' name, store, price, city and its shopping url.

    :param des_url:
    :return:

    '''
    # head = {'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/56.0.2924.76 Chrome/56.0.2924.76 Safari/537.36'}
    content = requests.get(des_url).content.decode()
    # content = source_code.encoding = 'utf-8'
    all = json.loads(content)
    first = all['API.CustomizedApi']
    two = first['itemlist']
    three = two['auctions']
    dic = {}
    for each in three:
        dic['key'] = each
        four = dic['key']
        name = four['raw_title']
        price = four['view_price']
        store = four['nick']
        place = four['item_loc']
        good_url = four['comment_url']
        return name,price,store,place,good_url


def get_search_content():
    '''
    Input which you want to search.

    :param input_content:
    :return:

    '''
    print('Please input which you want to search:')
    search_contents = input()
    return search_contents

def write_file(all_content):
    '''

    Save the goods attr into a csv file which named write_file

    :param all_content:
    :return:

    '''

    with open('taobao.csv','a',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=['name','price','store','place','url'])
        writer.writeheader()
        for each in all_content:
            f.write(each)


if __name__ == '__main__':
    search = get_search_content()
    ajax = get_ajax_html(search)
    contents = get_content(ajax)
    write_file(contents)
#     taobao_spider = TaobaoSpider()



# url= 'https://s.taobao.com/api?_ksTS=&ajax=true&m=customized&q=香水'
# source = requests.get(url)
# content = source.content.decode()
# all = json.loads(content)

# print(all)
# dic = {}
# for each in three:
#     dic['key'] =each
#     four = dic['key']
#     # print(four)
#     name = four['raw_title']
#     price = four['view_price']
#     store = four['nick']
#     place = four['item_loc']
#     good_url = four['comment_url']
#     print(name)
#     print(price)
#     print(store)
#     print(place)
#     print(good_url)
#
# print(all['API.CustomizedApi'])
# for each in all:
#     name = each['API.CustomizedApi']['itemlist']['service']
#     print(name)
