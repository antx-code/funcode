# from tkinter import *
import tkinter as tk
import threading
import steam.webauth as wa
from requests import Session
import re
import time
from Naked.toolshed.shell import muterun_js
import json
import subprocess
import random
import string
from tkinter import scrolledtext, messagebox
from redis import Redis
import ctypes
from loguru import logger
from random import randint as rant

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 Aoyou/VnN1RG0qQ1hkKz0iT1h0WW39_ebQ7Og6EiMFYYb9HbCN9c3PheedkDIN'}
letters = string.ascii_lowercase
random_str = ''.join(random.choice(letters) for i in range(20))

# def hide_console():
# 	whnd = ctypes.windll.kernel32.GetConsoleWindow()
# 	if whnd!= 0:
# 		ctypes.windll.user32.ShowWindow(whnd, 0)

class RedisService():
    @logger.catch(level='ERROR')
    def __init__(self, passwd, redis_db):
        # self.redis_client = Redis(host='', password=passwd, db=redis_db)   # passwd ='antx-auth-lock'
        self.redis_client = Redis(db=redis_db)

    @logger.catch(level='ERROR')
    def set_dep_key(self, key_name, key_value, expire_secs=None):
        """
        Set a duplicate redis key, which include content and expire time.
        :param key_name: The duplicate redis key that you want to be saved.
        :param key_value: The duplicate content of the redis key
        :param expire_secs: The expire time of the redis key and value. It's default value is None
        :return: A bool value of the operate.
        """
        self.redis_client.set(key_name, key_value, ex=expire_secs)
        return True

    @logger.catch(level='ERROR')
    def get_key_expire_content(self, key_name):
        """
        Get the expire redis key's content.
        :param key_name: The redis key that you want to query.
        :return: A string of the expire content.
        """
        result = self.redis_client.get(key_name)
        if result:
            return result.decode()
        else:
            return False

    @logger.catch(level='ERROR')
    def del_key(self, key_name):
        """
        Delete the expire key.
        :param key_name: The target key name that you want to delete.
        :return: 1 for success or 0 for failed.
        """
        return self.redis_client.delete(key_name)

    @logger.catch(level='ERROR')
    def check_key(self, key_name):
        """
        Check the key is exist in redis or not.
        :param key_name: The key that you want to check.
        :return: If the key is exist in redis, it will return True, otherwise will return False.
        """
        if self.redis_client.exists(key_name):
            return True
        return False

class Buff2SteamGui(tk.Frame):
    @logger.catch(level='ERROR')
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('登录界面')   # 设置窗口的标题
        self.master.geometry('500x400') # 设置窗口的大小
        self.pack()
        self.auth_quit()
        self.Receive = tk.LabelFrame(self.master, text="显示区", padx=10, pady=10) # 水平，垂直方向上的边距均为 10
        self.Receive.place(x=10, y=10)
        self.Receive_Window = scrolledtext.ScrolledText(self.Receive, width=59, height=10, padx=10, pady=10,
                                                        wrap=tk.WORD)
        self.Receive_Window.grid()
        self.usr_name_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.auth2fa = tk.StringVar()
        self.redis_service = RedisService(passwd='antx-auth-lock', redis_db=1)
        self.salt = '95_0^9_01'
        self.skey = 'antx-au_^_th-@#_$_?!'

    @logger.catch(level='ERROR')
    def buff163_login_auth(self):
        self.Receive_Window.insert('end', '准备登录buff163......' + '\n')
        muterun_js('buff_login.js', arguments=random_str)
        time.sleep(1)
        self.Receive_Window.insert('end', 'Buff163登录完成......' + '\n')
        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def monitor_buff(self, timer: int = 3600):
        with open(f'{random_str}_cookie.json', 'r+') as f:
            js_cook = json.loads(f.readline())
            cookie = ''
            for each in js_cook:
                cookie = cookie + f'{each["name"]}={each["value"]};'
            cookie = cookie[:-1]
        cookies = {'Cookie': cookie}
        buff_session = Session()
        steam_trade_list = []
        monitor_trade_id_list = []
        while True:
            resp = buff_session.get(url='https://buff.163.com/api/market/steam_trade', headers=header,
                                    cookies=cookies).content.decode('utf-8')
            if len(json.loads(resp)['data']) > 0:
                data = json.loads(resp)['data']
                break
            time.sleep(timer)   # 每1小时检测一次
        logger.info(f'buff163 data -> {data}')
        self.Receive_Window.insert('end', f'buff163 data -> {data}' + '\n')
        for each_data in data:
            steam_trade_list.append(
                {
                    'steam_trade_id': each_data['tradeofferid'],
                    'join_steam_date': each_data['bot_extra_info'],
                    'game_id': each_data['appid'],
                    'verify_code': each_data['verify_code'].split(' ')[1],
                    'trade_item_info': each_data['items_to_trade']
                }
            )
            monitor_trade_id_list.append(each_data['tradeofferid'])
            self.Receive_Window.see('end')
        return steam_trade_list, monitor_trade_id_list

    @logger.catch(level='ERROR')
    def steam_login_auth(self, username, passwd, auth2fa):
        user = wa.WebAuth(username, passwd)
        steam_session = user.login(twofactor_code=auth2fa, language='schinese')
        return steam_session

    @logger.catch(level='ERROR')
    def deal_exchange(self, steam_session, steam_trade_list, all_trade_ids):
        for each_deal in steam_trade_list:
            trade_id = each_deal['steam_trade_id']
            if trade_id in all_trade_ids:
                self.Receive_Window.insert('end', 'id 已存在, 跳过......' + '\n')
                continue
            steam_order_url = f'https://steamcommunity.com/tradeoffer/{trade_id}'
            steam_trade_url = f'https://steamcommunity.com/tradeoffer/{trade_id}/accept'

            while True:
                try:
                    resp = steam_session.get(steam_order_url).text
                    partner_id = self.text_between(resp, "var g_ulTradePartnerSteamID = '", "';")
                    break
                except Exception as e:
                    time.sleep(10)
                    continue
            session_id = steam_session.cookies.get_dict()['sessionid']
            #buff_ex_date = each_deal['join_steam_date']

            #buyer_join_date = re.findall('trade_partner_member_since trade_partner_info_text ">(.*?)</div>', resp)[0]
            #buyer_join_date_list = re.findall('(.*?)年(.*?)月(.*?)日', buyer_join_date)[0]
            #steam_ex_date = f'{buyer_join_date_list[0]}-{int(buyer_join_date_list[1]):02d}-{int(buyer_join_date_list[2]) + 1:02d}'
            #self.Receive_Window.insert('end', f'steam_ex_date -> {steam_ex_date}' + '\n')
            #self.Receive_Window.insert('end', f'buff_ex_date -> {buff_ex_date}' + '\n')
            #if steam_ex_date in buff_ex_date:
            self.Receive_Window.insert('end', '新订单是来自于buff163的订单，订单有效......' + '\n')
            post_data = {
                'sessionid': session_id,
                'serverid': '1',
                'tradeofferid': trade_id,
                'partner': partner_id,
                'captcha': ''
            }
            headers = {'Referer': steam_order_url}
            while True:
                response = steam_session.post(url=steam_trade_url, data=post_data, headers=headers).json()
                if 'tradeid' in response.keys():
                    break
                time.sleep(rant(10, 15))
            # response = steam_session.post(url=steam_trade_url, data=post_data, headers=headers).json()
            if response.get('needs_mobile_confirmation', False):
                return 1
            return 0
            #else:
            #    return -1
        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def text_between(self, text: str, begin: str, end: str) -> str:
        start = text.index(begin) + len(begin)
        end = text.index(end, start)
        return text[start:end]

    @logger.catch(level='ERROR')
    def verify_auth_code(self, nickname: str):
        nickname = f'{nickname}-{self.skey}-{self.salt}'
        result = self.redis_service.get_key_expire_content(key_name=nickname)
        if result:
            return True
        return False

    @logger.catch(level='ERROR')
    def vauth(self):
        self.Receive_Window.insert('end', '开始鉴权......' + '\n')
        root = tk.Tk(className='验证授权')  # 弹出框框名
        root.geometry('300x100')    # 设置弹出框的大小 w x h
        tk.Label(root, text="请输入用户名 :").place(x=10, y=5, anchor='nw')

        nickname = tk.StringVar()

        def gac():
            nk = nk_input.get()
            result = self.verify_auth_code(nickname=nk)
            if result:
                messagebox.showinfo(title='鉴权成功', message='用户名有效...')
                self.Receive_Window.insert('end', '鉴权成功，用户名有效......' + '\n')
                root.destroy()
                self.buff163_login_auth()
                self.login_promt()
            else:
                messagebox.showerror(title='鉴权失败', message='用户名无效或授权已过期，请重新授权...')
                self.Receive_Window.insert('end', '鉴权失败，用户名无效或授权已过期，请重新授权......' + '\n')
                root.destroy()

        nk_input = tk.Entry(root, textvariable=nickname, width=50)
        nk_input.pack(side='top', padx=100, pady=5)
        tk.Button(root, text='确认', command=gac).place(x=80, y=70)
        tk.Button(root, text='退出', command=root.destroy).place(x=180, y=70)

        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def auth_quit(self):
        tk.Button(self.master, text='鉴权授权', command=self.vauth).place(x=150, y=350)
        tk.Button(self.master, text='退出', command=self.master.destroy).place(x=290, y=350)

    @logger.catch(level='ERROR')
    def login_promt(self):
        # 输入框的提示语
        tk.Label(self.master, text="用户名:").place(x=75, y=250, anchor='nw')
        tk.Label(self.master, text="密码  :").place(x=75, y=280, anchor='nw')
        tk.Label(self.master, text="二次验证码  :").place(x=75, y=310, anchor='nw')

        usr_name_var = tk.StringVar()
        password_var = tk.StringVar()
        auth = tk.StringVar()

        def res():
            nk = nk_input.get()
            pd = pd_input.get()
            auth = auth_input.get()
            self.Receive_Window.insert('end', f'username: {nk}' + '\n')
            self.Receive_Window.insert('end', f'password: {pd}' + '\n')
            self.Receive_Window.insert('end', f'fa2code: {auth}' + '\n')
            if not nk or not pd or not auth:
                messagebox.showerror(title='登录错误', message='验证失败，请输入有效值...')
                self.Receive_Window.insert('end', '验证失败，请输入有效值......' + '\n')
            else:
                try:
                    steam_session = self.steam_login_auth(nk, pd, auth)
                    if steam_session:
                        while True:
                            try:
                                self.main_monitor(steam_session=steam_session)  # 通过多线程解决调用函数处理时间过长导致窗体卡死问题
                                break
                            except Exception as e:
                                time.sleep(10)
                                continue
                except Exception as e:
                    messagebox.showerror(title='登录错误', message='验证失败，请重新输入正确的账号密码和二次验证码...')
                    self.Receive_Window.insert('end', '验证失败，请重新输入正确的账号密码和二次验证码......' + '\n')

        nk_input = tk.Entry(self.master, textvariable=usr_name_var)
        nk_input.place(x=150, y=250, anchor='nw')
        pd_input = tk.Entry(self.master, textvariable=password_var, show='*')
        pd_input.place(x=150, y=280, anchor='nw')
        auth_input = tk.Entry(self.master, textvariable=auth)
        auth_input.place(x=150, y=310, anchor='nw')

        tk.Button(self.master, text='登录Steam', command=lambda: thread_it(res)).place(x=150, y=350)
        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def main_monitor(self, steam_session):
        self.Receive_Window.insert('end', '成功登录Steam，准备开始监测......' + '\n')
        expire_time = time.strftime('%Y-%m-%d', time.localtime(time.time() + 691200))
        all_trade_ids = []
        while True:
            steam_trade_list, monitor_trade_id_list = self.monitor_buff(timer=3600)
            self.Receive_Window.insert('end', '监测到新订单, 30s后开始确认交易......' + '\n')
            time.sleep(10)
            self.Receive_Window.insert('end', '监测到新订单, 20s后开始确认交易......' + '\n')
            time.sleep(10)
            self.Receive_Window.insert('end', '监测到新订单, 10s后开始确认交易......' + '\n')
            time.sleep(10)
            self.Receive_Window.insert('end', '开始确认交易......' + '\n')
            result = self.deal_exchange(steam_session, steam_trade_list, all_trade_ids)
            if result == -1:
                self.Receive_Window.insert('end', '不是来自buff的有效订单，订单作废，继续监测......' + '\n')
                # for each in monitor_trade_id_list:
                #     all_trade_ids.remove(each)
                # continue
            elif result == 0:
                self.Receive_Window.insert('end', '确认buff订单出错，请查看订单......' + '\n')
                messagebox.showerror(title='登录错误', message='确认buff订单出错，请查看订单...')
                break
            else:
                self.Receive_Window.insert('end', '成功确认buff订单......' + '\n')
            # for each in monitor_trade_id_list:
            #     if each in all_trade_ids:
            #         continue
            #     else:
            #         all_trade_ids.append(each)
            today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            if today == expire_time:
                subprocess.run(f'rm {random_str}_cookie.json', shell=True)
                self.Receive_Window.insert('end', 'Buff163登录有效期已过，准备登出......' + '\n')
                messagebox.showerror(title='登录错误', message='Buff163登录有效期已过，准备登出...')
                break
            time.sleep(rant(10, 15))
        self.Receive_Window.see('end')
        self.master.destroy()

@logger.catch(level='ERROR')
def thread_it(func, *args): # 传入函数名和参数, 通过多线程解决调用函数处理时间过长导致窗体卡死问题
    # 创建线程
    t = threading.Thread(target=func, args=args)
    # 守护线程
    t.setDaemon(True)
    # 启动
    t.start()

if __name__ == '__main__':
    """
    
    当pyinstaller -F Buff2Steam.py时想要隐藏控制台但 -w 无效时，可使用hide_console()方法，或者使用
    
    import win32console
    import win32gui
    
    win = win32console.GetConsoleWindow()  # For closing command window
    win32gui.ShowWindow(win, 0)
    
    """

    # hide_console()
    root = tk.Tk()
    app = Buff2SteamGui(master=root)
    app.master.title('Buff2Steam Auto Config')
    app.master.maxsize(1000, 400)
    app.mainloop()
