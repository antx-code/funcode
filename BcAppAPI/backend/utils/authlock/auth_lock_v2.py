from redis import Redis
from loguru import logger
import tkinter as tk
import threading
import random
import string
from tkinter import scrolledtext, messagebox
import ctypes

letters = string.ascii_lowercase
random_str = ''.join(random.choice(letters) for i in range(20))


class RedisService():
    @logger.catch(level='ERROR')
    def __init__(self, passwd, redis_db):
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


class AuthLockGui(tk.Frame):
    @logger.catch(level='ERROR')
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('登录界面') # 设置窗口的标题
        self.master.geometry('500x400') # 设置窗口的大小
        self.pack()
        self.auth_quit()
        self.Receive = tk.LabelFrame(self.master, text="显示区", padx=10,
                                     pady=10) # 水平，垂直方向上的边距均为 10
        self.Receive.place(x=10, y=10)
        self.Receive_Window = scrolledtext.ScrolledText(self.Receive,
                                                        width=59,
                                                        height=10,
                                                        padx=10,
                                                        pady=10,
                                                        wrap=tk.WORD)
        self.Receive_Window.grid()

        self.redis_service = RedisService(passwd='antx-auth-lock', redis_db=1)
        self.salt = '9_0^9_1'
        self.skey = 'antx-au_^_th-@#_$_?!'

        self.nickname_var = tk.StringVar()
        self.expire_var = tk.IntVar()

    @logger.catch(level='ERROR')
    def generate_auth_code(self, nickname: str, expire_time: int):
        auth_code = 'steam_buff_auth_lock'
        nickname = f'{nickname}-{self.skey}-{self.salt}'
        check_result = self.redis_service.check_key(key_name=nickname)
        if check_result:
            return False
        return self.redis_service.set_dep_key(key_name=nickname,
                                              key_value=auth_code,
                                              expire_secs=(expire_time *
                                                           86400))

    @logger.catch(level='ERROR')
    def verify_auth_code(self, nickname: str):
        nickname = f'{nickname}-{self.skey}-{self.salt}'
        result = self.redis_service.get_key_expire_content(key_name=nickname)
        if result:
            return True
        return False

    @logger.catch(level='ERROR')
    def del_auth(self, nickname: str):
        nickname = f'{nickname}-{self.skey}-{self.salt}'
        result = self.redis_service.del_key(nickname)
        if result:
            return True
        return False

    @logger.catch(level='ERROR')
    def gauth(self):
        self.Receive_Window.insert('end', '开始授权......' + '\n')
        root = tk.Tk(className='新增授权') # 弹出框框名
        root.geometry('300x100') # 设置弹出框的大小 w x h
        tk.Label(root, text="授权用户名 :").place(x=10, y=5, anchor='nw')
        tk.Label(root, text="有效时长/天:").place(x=10, y=35, anchor='nw')

        nickname = tk.StringVar()
        expire = tk.IntVar()

        @logger.catch(level='ERROR')
        def gac():
            nk = nk_input.get()
            er = int(er_input.get())
            result = self.generate_auth_code(nickname=nk, expire_time=er)
            if result:
                messagebox.showinfo(title='授权成功', message='新增授权账户成功...')
                self.Receive_Window.insert(
                    'end', f'新增授权账户成功，用户名:{nk}，有效期限:{er}天......' + '\n')
                root.destroy()
            else:
                messagebox.showerror(title='授权失败', message='账户名已存在，请重新输入...')
                self.Receive_Window.insert(
                    'end', '新增授权账户失败，账户名已存在，请重新输入......' + '\n')
                root.destroy()

        nk_input = tk.Entry(root, textvariable=nickname, width=50)
        nk_input.pack(side='top', padx=100, pady=5)
        er_input = tk.Entry(root, textvariable=expire, width=50)
        er_input.pack(side='top', padx=100, pady=5)
        tk.Button(root, text='确认', command=gac).place(x=80, y=70)
        tk.Button(root, text='退出', command=root.destroy).place(x=180, y=70)

        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def vauth(self):
        self.Receive_Window.insert('end', '开始鉴权......' + '\n')
        root = tk.Tk(className='验证授权') # 弹出框框名
        root.geometry('300x100') # 设置弹出框的大小 w x h
        tk.Label(root, text="请输入用户名 :").place(x=10, y=5, anchor='nw')

        nickname = tk.StringVar()

        @logger.catch(level='ERROR')
        def gac():
            nk = nk_input.get()
            result = self.verify_auth_code(nickname=nk)
            if result:
                messagebox.showinfo(title='鉴权成功', message='用户名有效...')
                self.Receive_Window.insert('end', '鉴权成功，用户名有效......' + '\n')
                root.destroy()
            else:
                messagebox.showerror(title='鉴权失败',
                                     message='用户名无效或授权已过期，请重新授权...')
                self.Receive_Window.insert(
                    'end', '鉴权失败，用户名无效或授权已过期，请重新授权......' + '\n')
                root.destroy()

        nk_input = tk.Entry(root, textvariable=nickname, width=50)
        nk_input.pack(side='top', padx=100, pady=5)
        tk.Button(root, text='确认', command=gac).place(x=80, y=70)
        tk.Button(root, text='退出', command=root.destroy).place(x=180, y=70)

        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def dauth(self):
        self.Receive_Window.insert('end', '开始解除授权......' + '\n')
        root = tk.Tk(className='解除授权') # 弹出框框名
        root.geometry('300x100') # 设置弹出框的大小 w x h
        tk.Label(root, text="请输入用户名 :").place(x=10, y=5, anchor='nw')

        nickname = tk.StringVar()

        @logger.catch(level='ERROR')
        def gac():
            nk = nk_input.get()
            result = self.del_auth(nickname=nk)
            if result:
                messagebox.showinfo(title='取消授权成功', message='取消账户授权成功...')
                self.Receive_Window.insert('end', '取消授权成功......' + '\n')
                root.destroy()
            else:
                messagebox.showerror(title='取消授权失败',
                                     message='取消账户授权失败，请检查用户名...')
                self.Receive_Window.insert('end',
                                           '取消账户授权失败，请检查用户名......' + '\n')
                root.destroy()

        nk_input = tk.Entry(root, textvariable=nickname, width=50)
        nk_input.pack(side='top', padx=100, pady=5)
        tk.Button(root, text='确认', command=gac).place(x=80, y=70)
        tk.Button(root, text='退出', command=root.destroy).place(x=180, y=70)

        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def auth_quit(self):
        tk.Button(self.master, text='授权', command=self.gauth).place(x=25,
                                                                    y=300)
        tk.Button(self.master, text='鉴权', command=self.vauth).place(x=150,
                                                                    y=300)
        tk.Button(self.master, text='解除授权', command=self.dauth).place(x=280,
                                                                      y=300)
        tk.Button(self.master, text='退出',
                  command=self.master.destroy).place(x=420, y=300)


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
    app = AuthLockGui(master=root)
    app.master.title('Antx Auth Lock')
    app.master.maxsize(500, 400)
    app.mainloop()
