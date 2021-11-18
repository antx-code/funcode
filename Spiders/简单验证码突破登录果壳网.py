import requests
import re


# source_code_url = 'http://www.guokr.com/settings/profile/'
login_url = 'https://account.guokr.com/sign_in/'
source_code_url = 'http://www.guokr.com/user/messages/'
head = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/56.0.2924.76 Chrome/56.0.2924.76 Safari/537.36'}


def get_captcha(login_html):
    """

    Get the captcha from the login html and save it into local file.

    :param login_html:
    :return:
    """
    source = requests.get(login_html).text
    captcha_url = re.findall('img src="(.*?)" id=',source)[0]
    with open('captcha.png','wb') as f:
        f.write(requests.get(captcha_url).content)


def post_data(csrf,user,passwd,captcha,rand):
    """

    Post the necessary to the web server which include the csrf_token, username, passwoed,
    captcha_code, captcha_rand and permanent.

    :param csrf:
    :param user:
    :param passwd:
    :param captcha:
    :return:
    """
    data = {'csrf_token': csrf, 'username': user, 'password': passwd, 'captcha': captcha,'captcha_rand': rand, 'permanent': 'y'}
    session = requests.Session()
    result = session.post(login_url,headers=head,data=data)
    return result


def csrf_token():
    """

    Get the csrf_token from the login html's source code.

    :return:
    """
    source = requests.get(login_url).text
    csrf = re.findall('csrf_token" type="hidden" value="(.*?)">',source,re.S)
    csrfs = csrf[0]
    return csrfs


def get_captcha_rand():
    """
    
    Get the necessary info which named captcha_rand.
    
    :return: 
    """
    source = requests.get(login_url).text
    rand = re.findall('captchaRand" value="(.*?)"><',source,re.S)
    cap_rand = rand[0]
    return cap_rand


def print_source_code(des_html):
    """

    Print the destination html's source code.

    :param des_html:
    :return:
    """
    print_html = requests.get(des_html).text
    print(print_html)


if __name__ == '__main__':
    get_captcha(login_url)
    csrf_codes = csrf_token()
    rands = get_captcha_rand()
    input_username = input('Please input your username:')
    input_password = input('Please input your password:')
    input_captcha = input('Please input captcha:')
    post_data(csrf_codes,input_username,input_password,input_captcha,rands)
    print_source_code(source_code_url)
