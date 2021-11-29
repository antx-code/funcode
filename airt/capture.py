# from loguru import logger
# poco airtest
from airtest.core.api import *
from airtest.cli.parser import cli_setup
from airtest.core.settings import Settings as ST
from airtest.aircv import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import time, random
import logging
import re
import json
import subprocess
from copy import deepcopy
import sys, os
from poc import ocr_poker
from poker_cards import *
from init import config
from funcs import *
sys.path.append("..")
__author__ = "antx"
auto_setup(__file__)
lgr = logging.getLogger("airtest")
lgr.setLevel(logging.INFO)

# ST.THRESHOLD_STRICT = 0.9

CONF = config['CORP_IMG']

init_device('Android')
mx4 = connect_device('Android://127.0.0.1:5037/emulator-5554?cap_method=javacap&touch_method=adb')
poco_mx4 = AndroidUiautomationPoco(mx4, use_airtest_input=True, screenshot_each_action=False)

# if not cli_setup():
#     auto_setup(__file__,
#                logdir=True,
#                devices=["Android://127.0.0.1:5037/emulator-5554?cap_method=JAVACAP&&ori_method=ADBORI&&touch_method=ADBTOUCH",]
#                )

# script content
print("start...")

now_path = os.getcwd()

print(f'now path: {now_path}')

class RunIt():
    # @logger.catch('ERROR')
    def __init__(self, poco_device):
        """
        initial the app that you want to run.
        """
        # self.poco = AndroidUiautomationPoco(poco_device, use_airtest_input=True, screenshot_each_action=False)
        self.poco = poco_device
        print('connect')

    # @logger.catch('ERROR')
    def login(self, device, username, password): # 登录
        """
        login the already register account.
        :param phone_number:
        :param phone_passwd:
        :return:
        """
        # self.poco(text='我').click()
        # self.poco(name='com.ss.android.ugc.aweme:id/ni').set_text()
        # time.sleep(2)
        # self.poco(name='com.ss.android.ugc.aweme:id/a3k').click()
        # time.sleep(2)
        # self.poco(name='com.ss.android.ugc.aweme:id/nd').set_text()
        # self.poco(name='com.ss.android.ugc.aweme:id/ng').click()
        # self.poco(text='确定').click()
        # time.sleep(3)
        pass

    # @logger.catch('ERROR')
    def room_in(self, room_id: int):        # 进入游戏房间并初始化数据结构, 进入房间
        self.poco.click([0.302, 0.953])     # 点击"约局"
        self.poco.click([0.428, 0.347])     # room id 输入框
        text(str(room_id))                  # 输入房间号
        self.poco.click([0.471, 0.418])     # 点击屏幕
        self.poco.click([0.471, 0.418])     # 点击"进入房间"
        # self.poco.click([0.453, 0.842])     # 点击"空位"
        while not exists(Template(r"pics/roomin/6.png")):
            self.poco.click([0.453, 0.842]) # 点击"空位"
            if exists(Template(r"pics/roomin/8.png")):
                self.poco.click([0.051, 0.413])
                break
            if exists(Template(r"pics/roomin/6.png")):
                self.poco.click([0.508, 0.622])  # 点击"带分进入"
                break
            if exists(Template(r'pics/roomin/9.png')):
                self.poco.click([0.503, 0.587]) # 点击"确定"
        # self.poco.click([0.528, 0.654])     # 点击"准备"
        touch(Template(r'pics/roomin/7.png'))
        logger.info(f'已成功进入牌局房间{room_id}，并进入准备，等待游戏...')

    # @logger.catch('ERROR')
    def record_play(self, task_id: str):                  # 游戏记录, 牌局开始
        resp = 0
        CORP_PLAYER = ['LOCAL', 'PLAYER1', 'PLAYER2']
        CORP_POKER = ['HEAD', 'MID', 'TAIL', 'DROP']
        SIG = 'P3'
        # # status = get_living_status(task_id)
        # # if status == 'stopped' or status == 'finished':
        # #     return False
        if not exists(Template(r'pics/playing/3.png')):
            SIG = 'P2'
        try:
            os.mkdir(f'{now_path}/pics/playing/{task_id}')
            for k in CORP_PLAYER:
                os.mkdir(f'{now_path}/pics/playing/{task_id}/{k}')
                for kk in CORP_POKER:
                    os.mkdir(f'{now_path}/pics/playing/{task_id}/{k}/{kk}')
        except Exception as e:
            pass
        while True:
            # status = get_living_status(task_id)
            # if status == 'stopped' or status == 'finished':
            #     return -1
            if exists(Template(r'pics/playing/1.png')):
                touch(Template(r'pics/playing/2.png'))
            screen = mx4.snapshot()

            for pk in CORP_PLAYER:
                if pk != 'LOCAL':
                    CONF_BASE = CONF[pk][SIG]
                else:
                    CONF_BASE = CONF[pk]
                for k in CORP_POKER:
                    if not CONF_BASE[k]:
                        continue
                    for inx, dk in enumerate(CONF_BASE[k]):
                        logger.info(f'{inx}: {dk}')
                        ci = aircv.crop_image(screen, dk)
                        filename = f'{now_path}/pics/playing/{task_id}/{pk}/{k}/{inx}.png'
                        aircv.imwrite(filename, ci)
                        aircv.imwrite(filename, ci)
                    ocr_poker(filename)

            logger.info(f'screenshot done.')
            if exists(Template(r'pics/roomout/6.png')):
                return -2

    # @logger.catch('ERROR')
    def room_normal_out(self, room_id):
        self.poco.click([0.505, 0.472])     # 点击"确定"
        self.poco.click([0.041, 0.06])      # 点击"返回"
        self.poco.click([0.505, 0.956])     # 点击"小飞机"
        # self.poco.click([0.302, 0.953])     # 点击"约局"
        logger.info(f'已成功退出牌局房间{room_id}')

    # @logger.catch('ERROR')
    def room_stop_out(self, room_id):       # 收到停止指令后退出房间, 退出
        self.poco.click([0.071, 0.056])     # 点击"设置"
        self.poco.click([0.118, 0.293])     # 点击"退出牌局"
        try:
            if exists(Template(r'pics/roomout/5.png')):    # 如果存在退出提示，则点击"确定"
                self.poco.click([0.353, 0.589])
        except Exception as e:
            self.poco.click([0.353, 0.589])
        self.poco.click([0.505, 0.956])     # 点击"小飞机"
        # self.poco.click([0.302, 0.953])     # 点击"约局"
        logger.info(f'已成功退出牌局房间{room_id}')

    # @logger.catch('ERROR')
    async def dia(self):                                    # dia入口
        while True:
            task_id, room_id = get_playing_room_taskid()    # 获取最新的游戏信息及room
            if task_id:
                status = get_living_status(task_id)
                if status == 'pending':
                    set_living_status_redis(task_id, {'status': 'connecting'})
                    runit.room_in(room_id)
                    set_living_status_redis(task_id, {'status': 'capturing'})
                if status == 'stopped' or status == 'finished':
                    runit.room_stop_out(room_id)
                if status == 'capturing':
                    result = runit.record_play(task_id)
                    set_living_status_redis(task_id, {'status': 'finished'})
                    if result == -1:
                        self.room_stop_out(room_id)
                    else:
                        self.room_normal_out(room_id)

if __name__ == '__main__':

    runit = RunIt(poco_mx4)
    room_id = 340098

    start = time.time()
    # runit.room_in(room_id)
    runit.record_play(room_id)
    # runit.room_stop_out(room_id)
    end = time.time()
    logger.info('已完成所有操作...')

    logger.info(f'共耗时: {end - start}s.')
