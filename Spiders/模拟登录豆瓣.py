import requests
import re


"""
Method 1 to get the source code.
Use cookies to login the web site which is 'douban.com' and print it's source code

"""


url = 'https://www.douban.com/people/oldsoulafu/'
session = requests.Session()
cookie = {'Cookie':'ll="118239"; bid=Hgj_2-AOA2A; ps=y; __utmt=1; __utma=30149280.1486463609.1490349543.1490349543.1490506414.2; __utmb=30149280.2.9.1490506414; __utmc=30149280; __utmz=30149280.1490349543.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.1486463609.1490349543; ue="wkaifeng2007@163.com"; dbcl2="75154261:cbL9fYIrmqw"; ck=yHxW; push_noty_num=0; push_doumail_num=0'}
htmls = session.get(url,cookies=cookie).content.decode()
print(htmls)



"""

Method 2 to get the source code.

"""


post_url = 'https://www.douban.com'
login_url = 'https://accounts.douban.com/login'
head = {'captcha_urlUser-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/56.0.2924.76 Chrome/56.0.2924.76 Safari/537.36'}
session = requests.Session()
html = requests.get(login_url,headers = head).text


def get_cpa_url():
    """

    Get the cpa code which we will use to login.

    :param login_html:
    :return:
    """
    login_url_codes = html
    cpa_pic_url = re.findall('image" src="(.*?)" alt',login_url_codes,re.S)
    # cpa = cpa_pic_url[0]
    # return cpa
    for each in cpa_pic_url:
        return each


def download_cpa_pic(cpa_url):
    """

    Download the picture which we can see the cpa code.

    :param cpa_url:
    :return:
    """
    with open('cpa_pic.png', 'wb') as f:
        f.write(requests.get(cpa_url).content)


def get_post_id():
    """

    Get the necessary id which we will post to the web server.

    :param login_urls:
    :return:
    """
    html_source = html
    post_id = re.findall('captcha?id=(.*?):en',html_source)
    return post_id


def post_data_have_cap(email,password,code,id):
    """

    If the login website have captcha, then post the necessary info to the web server to login.

    :param code:
    :return:
    """
    data = {'form_email': email, 'form_password': password, 'captcha-solution': code,'captcha-id':id,'login':'登录'}
    result = session.post(post_url,headers=head,data=data)
    return result


def post_data_no_cap(email,password):
    """
    
    If the login website have not the captcha, then post the necessary info to the web server to login.
    
    :return: 
    """
    datas = {'redir':'https://www.douban.com','form_email':email,'form_password':password,'login':'登录'}
    results = session.post(post_url,headers=head,data=datas)
    return results


def print_source_code():
    """

    Print the destination html's source code.

    :return:
    """
    print_html = session.get('https://www.douban.com/people/oldsoulafu/',headers=head).text
    print(print_html)


if __name__ =='__main__':
    cpa_urls = get_cpa_url()
    input_email = input('请输入帐号:')
    input_password = input('请输入密码:')
    if cpa_urls != None:
        download_cpa_pic(cpa_urls)
        input_code = input('请输入验证码:')
        ids = get_post_id()
        post_data_have_cap(input_email,input_password,input_code,ids)
        print_source_code()
    else:
        post_data_no_cap(input_email,input_password)
        print_source_code()
