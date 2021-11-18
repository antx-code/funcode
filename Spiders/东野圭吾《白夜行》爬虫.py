#-*-coding:utf8-*-
'''
Method 1 to stroe the function of white
'''
from lxml import html
import requests

white_url = 'http://www.dongyeguiwu.com/books/baiyexing/53.html/'

def get_source(url):
    '''
    Get the source code which we want to spider html
    '''
    head = {'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/56.0.2924.76 Chrome/56.0.2924.76 Safari/537.36'}
    sou_html = requests.get(url,headers=head)
    sou_html.encoding='utf-8'
    return sou_html.content

def get_content(source):
    '''
    get the content from the source code page
    :param source:
    :return:
    '''
    selector = html.document_fromstring(source)
    content = selector.xpath('//div[@class="readtext"]')[0]
    num = content.xpath('h4/text()')
    every_content = content.xpath('p/text()')
    write_file(num)
    for each in every_content:
        write_file(each)

def write_file(con):
    '''
    Save the content to the file which we named as white.txt
    :param content_field:
    :return:
    '''
    with open('white.txt','a',encoding='utf-8') as f:
        cons = str(con)
        f.writelines(cons)


if __name__ == '__main__':
    w = [1,2,3,4,5,6,7]
    for i in w:
        newurl = white_url + str(i)
        source = get_source(newurl)
        all_content = get_content(source)




'''
Method 2 to stroe the function of white
'''
# import lxml.html
#
# html = '''
# <!DOCTYPE html>
# <html>
# <head lang="en">
#     <meta charset="UTF-8">
#     <title>测试-常规用法</title>
# </head>
# <body>
# <div id="content">
#     <ul id="useful">
#         <li class="thisiswhatIwant">这是第一条信息</li>
#         <li class="thisiswhatIwant">这是第二条信息</li>
#         <li>这是第三条信息</li>
#     </ul>
#     <ul id="useless">
#         <li>不需要的信息1</li>
#         <li>不需要的信息2</li>
#         <li>不需要的信息3</li>
#     </ul>
#
#     <div id="url">
#         <a href="http://jikexueyuan.com">极客学院</a>
#         <a href="http://jikexueyuan.com/course/" title="极客学院课程库">点我打开课程库</a>
#     </div>
# </div>
#
# </body>
# </html>
# '''
#
# selector = lxml.html.fromstring(html)
# content_0 = selector.xpath('//ul[@id="useful"]')[0]
# # content = content_0.xpath('li/text()')
# content = selector.xpath('//ul[@id="useful"]/li/text()')
# # content = selector.xpath('//li[@class="thisiswhatIwant"]/text()')
# # content = selector.xpath('/html/body/div/ul[@id="useful"]/li[@class="thisiswhatIwant"]/text()')
# # print(content)
# for each in content:
#     print(each)


# w = [1,2,3,4,5,6,7]
# for i in w:
#     newurl = white_url + str(i)
#     source_code = requests.get(newurl).text
#     selector = html.document_fromstring(source_code)
#     content = selector.xpath('//div[@class="readtext"]')[0]
#     num = content.xpath('h4/text()')
#     every_content = content.xpath('p/text()')
#     print(num)
#     for each in every_content:
#         print(each)
#
