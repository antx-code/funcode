# poco airtest
from airtest.core.api import *
from airtest.aircv import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import logging
from copy import deepcopy
from poker_cards import *
from comser.funcs import *
from poc import poker_dia
from corp_analysis import cac
from snow_flake import IdWorker
sys.path.append("..")
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
uvloop.install()

__author__ = "antx"
auto_setup(__file__)
lgr = logging.getLogger("airtest")
lgr.setLevel(logging.INFO)

CONF = config['CORP_IMG']
CORP_PLAYER = ['LOCAL', 'PLAYER1', 'PLAYER2']
CORP_POKER = ['HEAD', 'MID', 'TAIL', 'DROP', 'HAND']

POKER_RELA = {
    'LOCAL': 'local',
    'PLAYER1': 'player1',
    'PLAYER2': 'player2',
    'HEAD': 'head',
    'MID': 'mid',
    'TAIL': 'tail',
    'DROP': 'drop',
    'HAND': 'hand'
}

id_worker = IdWorker(0, 0)

init_device('Android')
mx4 = connect_device('Android://127.0.0.1:5037/emulator-5554?cap_method=javacap&touch_method=adb')

poco_mx4 = AndroidUiautomationPoco(mx4, use_airtest_input=True, screenshot_each_action=False)

# 固定横屏模式
mx4._current_orientation = 1

logger.debug(f'{mx4._current_orientation}')
r = poco_mx4.adb_client.shell('content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1')
logger.info(f'r->{r}')

now_path = os.getcwd()

print(f'now path: {now_path}')

class RunIt():
    def __init__(self, poco_device):
        """
        initial the app that you want to run.
        """
        self.poco = poco_device
        self.redis_service = redis_connection(redis_db=0, mode='local')
        print('********* connect *********')

########################################################################

    def room_in(self, room_id: int):                                            # 进入游戏房间并初始化数据结构, 进入房间
        self.poco.click([0.302, 0.953])                                         # 点击"约局"
        self.poco.click([0.428, 0.347])                                         # room id 输入框
        text(str(room_id))                                                      # 输入房间号
        self.poco.click([0.471, 0.418])                                         # 点击屏幕
        self.poco.click([0.471, 0.418])                                         # 点击"进入房间"
        # self.poco.click([0.453, 0.842])                                       # 点击"空位"

        # 正常正确逻辑
        # while not exists(Template(r"pics/roomin/6.png")):
        #     # self.poco.click([0.453, 0.842])                                   # 点击"空位"
        #
        #
        #     try:
        #         touch(Template(r'pics/roomin/10.png'))                          # 点击"空位"
        #     except Exception as e:
        #         self.poco.click([0.453, 0.842])                                 # 点击"空位"
        #     if exists(Template(r"pics/roomin/8.png")):
        #         self.poco.click([0.051, 0.413])
        #         break
        #     if exists(Template(r"pics/roomin/6.png")):
        #         self.poco.click([0.508, 0.698])                                 # 点击"带分进入"
        #         break
        #     if exists(Template(r'pics/roomin/9.png')):
        #         self.poco.click([0.508, 0.589])                                 # 点击"确定"
        #
        #     # if exists(Template(r'pics/roomin/7.png')):
        #     #     touch(Template(r'pics/roomin/7.png'))
        #     #     break

        # yuanhuihui's mac 临时逻辑
        self.poco.click([0.453, 0.842])
        time.sleep(0.5)
        self.poco.click([0.508, 0.698])
        time.sleep(0.5)


        self.poco.click([0.528, 0.654])                                       # 点击"准备"
        # touch(Template(r'pics/roomin/7.png'))
        logger.info(f'已成功进入牌局房间{room_id}，并进入准备，等待游戏...')
        time.sleep(3)

    def room_normal_out(self, room_id):
        self.poco.click([0.5, 0.64])                                         # 点击"确定"
        # self.poco.click([0.041, 0.06])                                          # 点击"返回"
        mx4.keyevent('BACK')
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

    async def poker_play(self, task_id: str, room_id: str):                     # 游戏记录, 牌局开始
        # record = deepcopy(init_poker)

        # 固定横屏模式
        mx4._current_orientation = 1
        r = poco_mx4.adb_client.shell('content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1')
        phonew, phoneh = mx4.get_current_resolution()  # 获取手机分辨率
        logger.info(f'手机分辨率: {phonew}*{phoneh}')

        # SIG表示是双人游戏还是三/多人游戏
        # corp_analysis文件中的pin表示是横屏还是竖屏

        SIG = 'TPG' if not exists(Template(r'pics/playing/3.png')) else 'MPG'     # 判断是两个玩家还是三个玩家
        if SIG == 'TPG':
            CORP_PLAYER.remove('PLAYER2')
            del POKER_RELA['PLAYER2']

        logger.error(f'SIG: {SIG}')

        self.mkpicsdir(task_id)                                                 # 创建相应截图保存目录

        while True:
            start = time.time()
            # if exists(Template(r'pics/playing/9.png')) and exists(Template(r'pics/playing/7.png')):                            # or exists(Template(r'pics/playing/7.png'))
            record = deepcopy(init_poker)                                       # 必须1s内分析完才可以这样

            # 测试时注销，生产时启用
            status = get_living_status(task_id)
            print(f'实时status: {status}')
            if status == 'stopped' or status == 'finished':
                return -1

            self.poco.click([0.525, 0.638])
            self.poco.click([0.649, 0.847])
            snap_file = f'{now_path}/pics/snapshot/{task_id}/{id_worker.get_id()}.png'
            screen = mx4.snapshot(quality=99)                                             # 对屏幕进行完整截图
            logger.info('screenshot done, waiting ayalysis...')
            if not exists(Template(r"pics/playing/4.png")):
                await asyncio.create_task(cac(task_id, screen, record, SIG, phonew, phoneh))
                # 测试时注销，生产时启用
                set_living_status_redis(task_id, {'records': record})
                logger.debug({'records': record})
                logger.info(f'screenshot analysis done.')
            else:
                if exists(Template(r'pics/roomout/6.png')):                         # 判断牌局是否已经自然结束
                    return -2

            end = time.time()
            logger.info('已完成所有操作...')
            logger.info(f'共耗时: {end - start}s.')

########################################################################

    async def dia(self):                                                        # dia入口
        while True:
            start = time.time()
            task_id, room_id = get_playing_room_taskid()                        # 获取最新的游戏信息及room
            print(f'task_id: {task_id}, room_id: {room_id}')

            if task_id:
                status = get_living_status(task_id)
                print(f'{task_id} status: {status}')
                if status == 'pending' or status == 'connecting':
                    # 测试时注销，生产时启用
                    set_living_status_redis(task_id, {'status': 'connecting'})
                    runit.room_in(room_id)
                    # 测试时注销，生产时启用
                    set_living_status_redis(task_id, {'status': 'capturing'})
                if status == 'stopped' or status == 'finished':
                    # 测试时注销，生产时启用
                    del_redis_record(task_id)
                    continue
                if status == 'capturing':
                    if not exists(Template(r'pics/roomin/10.png')):
                        result = await asyncio.create_task(self.poker_play(task_id, room_id))
                        # 测试时注销，生产时启用
                        set_living_status_redis(task_id, {'status': 'finished'})
                        if result == -1:
                            self.room_stop_out(room_id)
                        else:
                            self.room_normal_out(room_id)

            end = time.time()
            logger.info('已完成所有操作...')
            logger.info(f'共耗时: {end - start}s.')

if __name__ == '__main__':
    # phonew, phoneh = mx4.get_current_resolution()  # 获取手机分辨率
    # logger.info(f'手机分辨率: {phonew}*{phoneh}')

    runit = RunIt(poco_mx4)
    # room_id = 764742

    # 实际生产用
    asyncio.run(runit.dia())

    # 开发测试用
    # runit.room_in(room_id)
    # asyncio.run(runit.poker_play(room_id, room_id))
    # runit.room_stop_out(room_id)
    # runit.room_normal_out(room_id)
