import pandas as pd
import steam.webauth as wa
import re
from decimal import Decimal
import time
from random import randint as randt

COMMUNITY_URL = 'https://steamcommunity.com'
CREATE_BUY_ORDER = '/market/createbuyorder/'
GAME_DIC = {'STEAM':'753','CS':'730','DOTA':'570'}
SEARCH_URL = f'https://steamcommunity.com/market/search?q='

def read_excel(xl_name):
    frame = pd.read_excel(xl_name)
    good_names = frame['名称']
    good_nums = frame['购买数量']
    good_prices = frame['购买价格']
    game_names = frame['游戏类型']
    return good_names, good_nums, good_prices, game_names

def login_auth(username,passwd):
    user = wa.WebAuth(username,passwd)
    session = user.login(twofactor_code=input('请输入 2FA Code:'),language='schinese')
    return session

def zh2en(session,g_name):
    resp = session.get(SEARCH_URL + g_name).content.decode('utf-8')
    en_g_name = re.findall('data-hash-name="(.*?)">',resp)[0]
    print(f'物品英文名称:{en_g_name}')
    return en_g_name


def post_auto_buy(session,g_name, g_price, g_num, game):
    auto_buy_url = COMMUNITY_URL + CREATE_BUY_ORDER
    headers = {'Referer': f'https://steamcommunity.com/market/listings/{game}/{g_name}'}
    post_data = {
        "sessionid": session.cookies.get_dict()['sessionid'],
        "currency": 23,
        "appid": game,
        "market_hash_name": g_name,
        "price_total": str(Decimal(g_price) * Decimal(g_num) * 100),
        "quantity": g_num,
    }
    resp = session.post(auto_buy_url, data=post_data, headers=headers).json()
    return resp

if __name__ == '__main__':
    session = login_auth(input('请输入Steam账号：'), input('请输入Steam密码：'))
    good_names, good_nums, good_prices, game_names = read_excel('表格1.xls')
    print(f'******共有{len(good_names)}件商品待挂单******')
    for i in range(len(good_names)):
        print(f'准备挂单第{i+1}件,游戏类型:「{game_names[i]}」,商品名称:「{good_names[i]}」,挂单价格:「¥{good_prices[i]}」,挂单数量:「{good_nums[i]}」')
        en_g_name = zh2en(session,good_names[i]).encode('utf-8')
        resp = post_auto_buy(session,en_g_name,str(good_prices[i]),int(good_nums[i]),GAME_DIC[game_names[i]])
        if resp:
            if resp["success"] == 1:
                print(f'第{i+1}件商品挂单成功')
            elif resp["success"] == 42:
                print(f'第{i+1}件商品挂单失败，请检查您的订单是否已创建，即将跳过，请稍后重试...')
                time.sleep(5)
                continue
            elif resp["success"] == 29:
                print(f'第{i+1}件商品挂单失败，已对该物品提交有效的订购单。在提交新的订单之前，您需要取消该订单，或等待交易完成。即将跳过...')
                time.sleep(5)
                continue
            else:
                print(f'数据填充出错，{resp["message"]}也有可能是您的余额不足，准备退出程序...')
                time.sleep(5)
                break
            time.sleep(randt(4,9))
        else:
            print(f'数据填充出错，请检查表格数据是否正确，5秒后准备退出...')
            time.sleep(5)
            break
    print('******所有订单已完成******')
    print('3秒后准备退出程序...')
    time.sleep(3)

    # en_g_name = zh2en(session, good_names[4]).encode('utf-8')
    # resp = post_auto_buy(session, en_g_name, "38.4", 3, GAME_DIC[game_names[4]])
    # print(resp)
