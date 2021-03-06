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
        self.master.title('????????????') # ?????????????????????
        self.master.geometry('500x400') # ?????????????????????
        self.pack()
        self.auth_quit()
        self.Receive = tk.LabelFrame(self.master, text="?????????", padx=10,
                                     pady=10) # ??????????????????????????????????????? 10
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
        self.Receive_Window.insert('end', '????????????......' + '\n')
        root = tk.Tk(className='????????????') # ???????????????
        root.geometry('300x100') # ???????????????????????? w x h
        tk.Label(root, text="??????????????? :").place(x=10, y=5, anchor='nw')
        tk.Label(root, text="????????????/???:").place(x=10, y=35, anchor='nw')

        nickname = tk.StringVar()
        expire = tk.IntVar()

        @logger.catch(level='ERROR')
        def gac():
            nk = nk_input.get()
            er = int(er_input.get())
            result = self.generate_auth_code(nickname=nk, expire_time=er)
            if result:
                messagebox.showinfo(title='????????????', message='????????????????????????...')
                self.Receive_Window.insert(
                    'end', f'????????????????????????????????????:{nk}???????????????:{er}???......' + '\n')
                root.destroy()
            else:
                messagebox.showerror(title='????????????', message='????????????????????????????????????...')
                self.Receive_Window.insert(
                    'end', '???????????????????????????????????????????????????????????????......' + '\n')
                root.destroy()

        nk_input = tk.Entry(root, textvariable=nickname, width=50)
        nk_input.pack(side='top', padx=100, pady=5)
        er_input = tk.Entry(root, textvariable=expire, width=50)
        er_input.pack(side='top', padx=100, pady=5)
        tk.Button(root, text='??????', command=gac).place(x=80, y=70)
        tk.Button(root, text='??????', command=root.destroy).place(x=180, y=70)

        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def vauth(self):
        self.Receive_Window.insert('end', '????????????......' + '\n')
        root = tk.Tk(className='????????????') # ???????????????
        root.geometry('300x100') # ???????????????????????? w x h
        tk.Label(root, text="?????????????????? :").place(x=10, y=5, anchor='nw')

        nickname = tk.StringVar()

        @logger.catch(level='ERROR')
        def gac():
            nk = nk_input.get()
            result = self.verify_auth_code(nickname=nk)
            if result:
                messagebox.showinfo(title='????????????', message='???????????????...')
                self.Receive_Window.insert('end', '??????????????????????????????......' + '\n')
                root.destroy()
            else:
                messagebox.showerror(title='????????????',
                                     message='???????????????????????????????????????????????????...')
                self.Receive_Window.insert(
                    'end', '??????????????????????????????????????????????????????????????????......' + '\n')
                root.destroy()

        nk_input = tk.Entry(root, textvariable=nickname, width=50)
        nk_input.pack(side='top', padx=100, pady=5)
        tk.Button(root, text='??????', command=gac).place(x=80, y=70)
        tk.Button(root, text='??????', command=root.destroy).place(x=180, y=70)

        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def dauth(self):
        self.Receive_Window.insert('end', '??????????????????......' + '\n')
        root = tk.Tk(className='????????????') # ???????????????
        root.geometry('300x100') # ???????????????????????? w x h
        tk.Label(root, text="?????????????????? :").place(x=10, y=5, anchor='nw')

        nickname = tk.StringVar()

        @logger.catch(level='ERROR')
        def gac():
            nk = nk_input.get()
            result = self.del_auth(nickname=nk)
            if result:
                messagebox.showinfo(title='??????????????????', message='????????????????????????...')
                self.Receive_Window.insert('end', '??????????????????......' + '\n')
                root.destroy()
            else:
                messagebox.showerror(title='??????????????????',
                                     message='?????????????????????????????????????????????...')
                self.Receive_Window.insert('end',
                                           '?????????????????????????????????????????????......' + '\n')
                root.destroy()

        nk_input = tk.Entry(root, textvariable=nickname, width=50)
        nk_input.pack(side='top', padx=100, pady=5)
        tk.Button(root, text='??????', command=gac).place(x=80, y=70)
        tk.Button(root, text='??????', command=root.destroy).place(x=180, y=70)

        self.Receive_Window.see('end')

    @logger.catch(level='ERROR')
    def auth_quit(self):
        tk.Button(self.master, text='??????', command=self.gauth).place(x=25,
                                                                    y=300)
        tk.Button(self.master, text='??????', command=self.vauth).place(x=150,
                                                                    y=300)
        tk.Button(self.master, text='????????????', command=self.dauth).place(x=280,
                                                                      y=300)
        tk.Button(self.master, text='??????',
                  command=self.master.destroy).place(x=420, y=300)


@logger.catch(level='ERROR')
def thread_it(func, *args): # ????????????????????????, ???????????????????????????????????????????????????????????????????????????
    # ????????????
    t = threading.Thread(target=func, args=args)
    # ????????????
    t.setDaemon(True)
    # ??????
    t.start()


if __name__ == '__main__':
    """

        ???pyinstaller -F Buff2Steam.py??????????????????????????? -w ?????????????????????hide_console()?????????????????????

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
