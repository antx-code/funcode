
# poco airtest
import asyncio
import uvloop
from airtest.core.api import *
from airtest.aircv import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import logging
from copy import deepcopy
import os
from poker_cards import *
from comser.funcs import *
from poc import poker_dia
sys.path.append("..")
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
uvloop.install()
__author__ = "antx"
auto_setup(__file__)
lgr = logging.getLogger("airtest")
lgr.setLevel(logging.INFO)

# ST.THRESHOLD_STRICT = 0.9

CONF = config['CORP_IMG']
CORP_PLAYER = ['LOCAL', 'PLAYER1', 'PLAYER2']
# CORP_POKER = ['HEAD', 'MID', 'TAIL', 'DROP', 'HAND']
CORP_POKER = ['HEAD', 'MID', 'TAIL', 'DROP']

POKER_RELA = {
    'LOCAL': 'local',
    'PLAYER1': 'player1',
    'PLAYER2': 'player2',
    'HEAD': 'head',
    'MID': 'mid',
    'TAIL': 'tail',
    'DROP': 'drop',
    # 'HAND': 'hand'
}

init_device('Android')
mx4 = connect_device('Android://127.0.0.1:5037/emulator-5554?cap_method=javacap&touch_method=adb')
poco_mx4 = AndroidUiautomationPoco(mx4, use_airtest_input=True, screenshot_each_action=False)

now_path = os.getcwd()

print(f'now path: {now_path}')

class RunIt():
    def __init__(self, poco_device):
        """
        initial the app that you want to run.
        """
        self.poco = poco_device
        print('********* connect *********')

########################################################################

    def room_in(self, room_id: int):                                            # 进入游戏房间并初始化数据结构, 进入房间
        self.poco.click([0.302, 0.953])                                         # 点击"约局"
        self.poco.click([0.428, 0.347])                                         # room id 输入框
        text(str(room_id))                                                      # 输入房间号
        self.poco.click([0.471, 0.418])                                         # 点击屏幕
        self.poco.click([0.471, 0.418])                                         # 点击"进入房间"
        # self.poco.click([0.453, 0.842])                                       # 点击"空位"
        while not exists(Template(r"pics/roomin/6.png")):
            # self.poco.click([0.453, 0.842])                                   # 点击"空位"
            touch(Template(r'pics/roomin/10.png'))                              # 点击"空位"
            if exists(Template(r"pics/roomin/8.png")):
                self.poco.click([0.051, 0.413])
                break
            if exists(Template(r"pics/roomin/6.png")):
                self.poco.click([0.508, 0.622])                                 # 点击"带分进入"
                break
            if exists(Template(r'pics/roomin/9.png')):
                self.poco.click([0.503, 0.587])                                 # 点击"确定"
        # self.poco.click([0.528, 0.654])                                       # 点击"准备"
        touch(Template(r'pics/roomin/7.png'))
        logger.info(f'已成功进入牌局房间{room_id}，并进入准备，等待游戏...')

    def room_normal_out(self, room_id):
        self.poco.click([0.505, 0.472])                                         # 点击"确定"
        self.poco.click([0.041, 0.06])                                          # 点击"返回"
        self.poco.click([0.505, 0.956])                                         # 点击"小飞机"
        # self.poco.click([0.302, 0.953])                                       # 点击"约局"
        logger.info(f'已成功退出牌局房间{room_id}')

    def room_stop_out(self, room_id):                                           # 收到停止指令后退出房间, 退出
        self.poco.click([0.071, 0.056])                                         # 点击"设置"
        self.poco.click([0.118, 0.293])                                         # 点击"退出牌局"
        try:
            if exists(Template(r'pics/roomout/5.png')):                         # 如果存在退出提示，则点击"确定"
                self.poco.click([0.353, 0.589])
        except Exception as e:
            self.poco.click([0.353, 0.589])
        self.poco.click([0.505, 0.956])                                         # 点击"小飞机"
        # self.poco.click([0.302, 0.953])                                       # 点击"约局"
        logger.info(f'已成功退出牌局房间{room_id}')

########################################################################

    def mkpicsdir(self, task_id: str):
        try:                                                                    # 创建相应截图保存目录
            os.mkdir(f'{now_path}/pics/playing/{task_id}')
            for player in CORP_PLAYER:
                os.mkdir(f'{now_path}/pics/playing/{task_id}/{player}')
                for dao_poker in CORP_POKER:
                    os.mkdir(f'{now_path}/pics/playing/{task_id}/{player}/{dao_poker}')
        except Exception as e:
            pass

    async def corp_analysis(self, screen, scope, filename):                      # 对截图图片裁剪并分析获取牌面信息
        try:
            ci = aircv.crop_image(screen, scope)
            aircv.imwrite(filename, ci)
        except Exception as e:
            return -99
        poker_record = await asyncio.create_task(poker_dia(filename))           # 对每个给定的牌面截图图片进行识别
        return poker_record

    async def corp_poker_update(self, task_id, room_id, record, CONF_BASE, screen, player, dao_poker, record_player, record_dao_poker):
        for inx, dk in enumerate(CONF_BASE):                                    # 对每个位置进行图像分割， 并保存进相应的文件夹
            filename = f'{now_path}/pics/playing/{task_id}/{player}/{dao_poker}/{inx}.png'
            poker_record = await asyncio.create_task(self.corp_analysis(screen, dk, filename))
            if poker_record == -99:
                continue

            # if not poker_record or (record[record_player][record_dao_poker][inx] and not poker_record):
            #     continue
            record[record_player][record_dao_poker][inx] = poker_record         # 更新相应位置识别后的牌面信息
            logger.info(f"{record_player}-{record_dao_poker}-{inx}: {poker_record}")
            # logger.info(f'record: {record}')

            # 测试时注销，生产时启用
            set_living_status_redis(task_id, {'records': record})
            # await asyncio.create_task(push_record2serv(task_id, room_id, 'capturing', record))

    async def div_players(self, task_id, room_id, record, CONF_BASE, screen, player):
        tasks = []                                                              # 异步同时对每个player的每个位置牌面进行识别分配
        for dao_poker in CORP_POKER:
            record_player = POKER_RELA[player]
            record_dao_poker = POKER_RELA[dao_poker]
            if not CONF_BASE[dao_poker]:
                continue
            tasks.append(self.corp_poker_update(task_id, room_id, record, CONF_BASE[dao_poker], screen, player, dao_poker, record_player, record_dao_poker))
        await asyncio.gather(*tasks)

    async def poker_play(self, task_id: str, room_id: str):                     # 游戏记录, 牌局开始
        record = deepcopy(init_poker)
        SIG = 'P2' if not exists(Template(r'pics/playing/3.png')) else 'P3'     # 判断是两个玩家还是三个玩家
        if SIG == 'P2':
            CORP_PLAYER.remove('PLAYER2')
            del POKER_RELA['PLAYER2']

        self.mkpicsdir(task_id)                                                 # 创建相应截图保存目录

        while True:
            if exists(Template(r'pics/playing/6.png')) or exists(Template(r'pics/playing/7.png')) or exists(Template(r'pics/playing/8.png')):
                record = deepcopy(init_poker)

            # 测试时注销，生产时启用
            status = get_living_status(task_id)
            print(f'实时status: {status}')
            if status == 'stopped' or status == 'finished':
                return -1

            # try:
            #     if exists(Template(r'pics/playing/1.png')):                   # 判断是否在托管
            #         touch(Template(r'pics/playing/2.png'))
            #         continue
            # except Exception as e:
            #     self.poco.click([0.56, 0.697])
            #     continue
            self.poco.click([0.56, 0.697])

            # if exists(Template(r'pics/playing/4.png')):                       # 爆牌
            #     continue
            start = time.time()
            screen = mx4.snapshot()                                             # 对屏幕进行完整截图
            logger.info('完成截图，准备分析...')
            tasks = []
            for player in CORP_PLAYER:                                          # 对一次截图的每个位置进行图像分割并识别
                if player != 'LOCAL':
                    CONF_BASE = CONF[player][SIG]
                else:
                    CONF_BASE = CONF[player]
                tasks.append(self.div_players(task_id, room_id, record, CONF_BASE, screen, player))
            await asyncio.gather(*tasks)

            end = time.time()
            logger.info('已完成所有操作...')
            logger.info(f'共耗时: {end - start}s.')

            logger.info(f'screenshot analysis done.')
            if exists(Template(r'pics/roomout/6.png')):                         # 判断牌局是否已经自然结束
                return -2

########################################################################

    async def dia(self):                                    # dia入口
        while True:
            start = time.time()
            task_id, room_id = get_playing_room_taskid()    # 获取最新的游戏信息及room
            print(f'task_id: {task_id}, room_id: {room_id}')

            if task_id:
                status = get_living_status(task_id)
                print(f'{task_id} status: {status}')
                if status == 'pending' or status == 'connecting':
                    set_living_status_redis(task_id, {'status': 'connecting'})
                    runit.room_in(room_id)
                    set_living_status_redis(task_id, {'status': 'capturing'})
                if status == 'stopped' or status == 'finished':
                    del_redis_record(task_id)
                    continue
                if status == 'capturing':
                    result = await asyncio.create_task(self.poker_play(task_id, room_id))
                    set_living_status_redis(task_id, {'status': 'finished'})
                    if result == -1:
                        self.room_stop_out(room_id)
                    else:
                        self.room_normal_out(room_id)

            end = time.time()
            logger.info('已完成所有操作...')
            logger.info(f'共耗时: {end - start}s.')

if __name__ == '__main__':
    runit = RunIt(poco_mx4)
    # room_id = 778017

    # 实际生产用
    asyncio.run(runit.dia())
    runit.dia()

    # 开发测试用
    # runit.room_in(room_id)
    # asyncio.run(runit.poker_play(room_id, room_id))
    # runit.room_stop_out(room_id)
