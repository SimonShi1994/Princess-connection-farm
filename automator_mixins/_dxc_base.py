import time

from automator_mixins._base import DEBUG_RECORD
from core.constant import DXC_ELEMENT, FIGHT_BTN, MAIN_BTN, DXC_NUM, JJC_BTN, DXC_ENTRANCE_DRAG, \
    JUQING_BTN, DXC_ENTRANCE
from core.cv import UIMatcher
from core.pcr_checker import ReturnValue
from ._fight_base import FightBaseMixin


class DXCBaseMixin(FightBaseMixin):
    """
    地下城基础插片
    包含地下城脚本的基本操作
    """

    def __init__(self):
        super().__init__()
        self.dxc_switch = 0  # 0开，1锁
        self.is_dixiacheng_end = 0  # 地下城是否结束，0未结束，1结束

    @DEBUG_RECORD
    def dxc_kkr(self, screen_shot=None):
        """
        处理跳脸
        :return:
        """
        if screen_shot is None:
            screen_shot = self.getscreen()
        # time.sleep(2)  # 等妈出现
        if self.is_exists(JUQING_BTN["caidanyuan"], screen=screen_shot):
            self.click_btn(JUQING_BTN["caidanyuan"], wait_self_before=True, until_appear=JUQING_BTN["tiaoguo_1"])  # 菜单
            self.click_btn(JUQING_BTN["tiaoguo_1"], until_appear=JUQING_BTN["tiaoguo_2"])  # 跳过
            self.click_btn(JUQING_BTN["tiaoguo_2"], until_disappear=JUQING_BTN["tiaoguo_2"])  # 蓝色跳过
            return True

        if self.is_exists(DXC_ELEMENT["dxc_kkr"], screen=screen_shot):
            self.chulijiaocheng(turnback=None)
            if self.is_exists(DXC_ELEMENT["dxc_in_shop"]):
                self.click(DXC_ELEMENT["dxc_in_shop"])
            else:
                # 应急处理：从主页返回
                self.lock_img(MAIN_BTN["liwu"], elseclick=MAIN_BTN["zhuye"], elsedelay=1)  # 回首页
                self.click(480, 505, post_delay=1)
                self.lock_img('img/dixiacheng.jpg', elseclick=(480, 505), elsedelay=1, alldelay=1)
                self.click(900, 138, post_delay=3)
                self.lock_img(DXC_ELEMENT["chetui"])  # 锁定撤退
            return True
        return False

    @DEBUG_RECORD
    def dxczuobiao(self, x, y, auto, speed, bianzu=0, duiwu=0, min_live=5):
        """
        新的地下城刷图函数
        :param x: 屏幕x坐标
        :param y: 屏幕y坐标
        :param auto: 是否开启自动
        :param speed: 是否开启加速
        :param bianzu: 使用编组号,为0时不切换，为-1时使用前五个角色
        :param duiwu: 使用队伍号，为0时不切换，为-1时使用前五个角色
        :param min_live: 至少该队存活min_live人时才刷图，否则不刷
        :return: 刷图情况.
            -2: 无法点中关卡
            -1: 出现未知的错误
            0：存活人数不足
            1：战胜
            2：战败
        """
        self.wait_for_stable(at=DXC_ELEMENT["map"], delay=1.5, threshold=0.1, max_retry=5)  # 等待小人走完
        # 点人
        state = self.lock_no_img(DXC_ELEMENT["dxc_shop_btn"], elseclick=(x, y), elsedelay=10, retry=2)
        if not state:
            raise Exception("无法点中地下城关卡！")
        # 点击挑战
        # UPDATE 第二次进入BOSS时不需要这一步
        state = self.lock_img({FIGHT_BTN["tiaozhan"]: 1, JJC_BTN["dwbz"]: 2}, timeout=20)
        if state == 1:
            self.click_btn(FIGHT_BTN["tiaozhan"], wait_self_before=True, timeout=20)
        # 换队
        if bianzu == -1 and duiwu == -1:
            self.set_fight_team_order()
        elif bianzu != 0 and duiwu != 0:
            if not self.set_fight_team(bianzu, duiwu):
                return 0
        # 换队结束
        # 检查存活人数
        time.sleep(2)
        live_count = self.get_fight_current_member_count()
        if live_count < min_live:
            return 0
        self.click_btn(FIGHT_BTN["zhandoukaishi"], wait_self_before=True)
        self.wait_for_loading(delay=1)
        self.set_fight_auto(auto, screen=self.last_screen)
        self.set_fight_speed(speed, max_level=2, screen=self.last_screen)
        mode = 0
        while mode == 0:
            # 等待战斗结束
            mode = self.get_fight_state(max_retry=15, check_hat=True)
            time.sleep(3)
        if mode == -1:
            return -1
        elif mode == 1:
            # 点击下一步
            self.click_btn(DXC_ELEMENT["xiayibu"])
            self.click_btn(DXC_ELEMENT["shouqubaochou_ok"], wait_self_before=True)
            # 处理跳脸：回到地下城界面
            self.dxc_kkr()
            return 1
        elif mode == 2:
            # 前往地下城
            self.click(DXC_ELEMENT["qianwangdixiacheng"], post_delay=3)
            return 2

    @DEBUG_RECORD
    def dxc_chetui(self):
        """
        地下城界面点击撤退，回到选城页面
        场景要求：处于地下城内小人界面，右下角有撤退
        """
        self.click(DXC_ELEMENT["chetui"])
        self.lock_img(DXC_ELEMENT["chetui_ok"], elseclick=DXC_ELEMENT["chetui"], elsedelay=8, timeout=30)
        self.click_btn(DXC_ELEMENT["chetui_ok"])

    @DEBUG_RECORD
    def enter_dxc(self, dxc_id):
        """
        进入地下城
        :param dxc_id: 地下城编号
        :return: 是否进入成功
        
        """

        def fun_click(*args, **kwargs):
            def fun():
                self.click(*args, **kwargs)

            return fun

        # 锁定主页
        self.lock_home()
        # 进入冒险
        self.lock_img(MAIN_BTN["dxc"], elseclick=MAIN_BTN["maoxian"], elsedelay=0.5)

        # 进入地下城
        state = self.click_btn(MAIN_BTN["dxc"], elsedelay=0.5,
                               until_appear={DXC_ELEMENT["dxc_choose_shop"]: 1, DXC_ELEMENT["dxc_shop_btn"]: 2},
                               side_check=self.juqing_kkr)
        if state == 1:
            self.wait_for_stable(delay=3, similarity=0.96)

            def CishuCheck():
                screen = self.last_screen
                p0 = self.img_prob(DXC_ELEMENT["0/1"], screen=screen)
                p1 = self.img_prob(DXC_ELEMENT["1/1"], screen=screen)
                if p0 > p1 and p0 > 0.8:
                    self.log.write_log("info", "地下城次数已经用完，放弃。")
                    raise ReturnValue("0/1")
                else:
                    pass

            FC = self.getFC().getscreen()
            # 开图跳脸防止
            FC.add_sidecheck(self.juqing_kkr)
            FC.exist(DXC_ELEMENT["sytzcs"], CishuCheck, rv=None)
            FC.exist(DXC_ELEMENT["quyuxuanzequeren_ok"], rv=True)
            FC.exist(DXC_ELEMENT["dxc_shop_btn"], rv="IN")
            drag = DXC_ENTRANCE_DRAG[dxc_id]

            def do_fun():
                if drag == "left":
                    self.click(10, 242)
                    # self.Drag_Left(origin=True)
                    time.sleep(1.5)
                elif drag == "right":
                    # self.Drag_Right(origin=True)
                    self.click(950, 242)
                    time.sleep(1.5)
                self.click(DXC_ENTRANCE[dxc_id])

            FC.add_intervalprocess(do_fun, interval=10)
            out = FC.lock()
            if out == "0/1":
                return False
            elif out != "IN":
                self.click_btn(DXC_ELEMENT["quyuxuanzequeren_ok"],
                               until_appear={DXC_ELEMENT["chetui"]: 1, DXC_ELEMENT["dxc_kkr"]: 2})
                time.sleep(2)
        self.lock_img(DXC_ELEMENT["chetui"], elsedelay=0.5, side_check=self.dxc_kkr, retry=5)  # 锁定撤退
        return True

    @DEBUG_RECORD
    def check_dxc_level(self, dxc_id):
        """
        人力OCR
        比较所有数字图片，选择阈值最高的那个。
        要求界面：地下城小人页面
        :param dxc_id: 地下城编号
        :return: 层数，整数。如果为-1则识别失败。
        """
        if dxc_id not in DXC_NUM:
            # 不在OCR库中
            return -1
        sc = self.getscreen()
        probs = {}
        for i, j in DXC_NUM[dxc_id].items():
            probs[i] = self.img_prob(j, screen=sc)

        best = max(probs, key=lambda x: probs[x])
        values = sorted(probs.values(), reverse=True)
        # 必须有差距，否则失败
        if values[0] - values[1] < 0.05 or values[0] < 0.8:
            return -1
        else:
            return best

    @DEBUG_RECORD
    def dixiachengzuobiao(self, x, y, auto, team=0):
        # 完整刷完地下城函数
        # 参数：
        # x：目标层数的x轴坐标
        # y：目标层数的y轴坐标
        # auto：取值为0/1,auto=0时不点击auto按钮，auto=1时点击auto按钮
        # team：取值为0/1/2，team=0时不换队，team=1时更换为队伍列表中的1队，team=2时更换为队伍列表中的2队
        if self.is_dixiacheng_end:
            return
        else:
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    break
                self.click(1, 1)
                time.sleep(1)
            time.sleep(1)
            while True:
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/chetui.jpg'):
                    break
                self.click(1, 1)
                time.sleep(1)
            self.click(1, 1)
            time.sleep(3)

            self.click(x, y)  # 层数
            time.sleep(2)
            self.click(833, 456)  # 挑战
            time.sleep(2)

            while True:  # 锁定战斗开始
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/zhandoukaishi.jpg'):
                    break

            if team != 0:  # 换队
                self.click(866, 91)  # 我的队伍
                time.sleep(2)
                if team == 1:
                    self.click(792, 172)  # 1队
                elif team == 2:
                    self.click(789, 290)  # 2队
                time.sleep(0.5)
                while True:  # 锁定战斗开始
                    screen_shot_ = self.getscreen()
                    if UIMatcher.img_where(screen_shot_, 'img/zhandoukaishi.jpg'):
                        break
                    time.sleep(0.5)

            self.click(837, 447)  # 战斗开始
            time.sleep(2)

            # while True:  # 战斗中快进
            #     screen_shot_ = self.getscreen()
            #     if UIMatcher.img_where(screen_shot_, 'img/caidan.jpg'):
            #         if auto == 1:
            #             time.sleep(0.5)
            #             self.d.click(912, 423)  # 点auto按钮
            #             time.sleep(1)
            #         break
            while True:  # 结束战斗返回
                screen_shot_ = self.getscreen()
                if UIMatcher.img_where(screen_shot_, 'img/shanghaibaogao.jpg'):
                    while True:
                        screen_shot = self.getscreen()
                        if UIMatcher.img_where(screen_shot, 'img/xiayibu.jpg'):
                            self.click(830, 503)
                            break
                        if UIMatcher.img_where(screen_shot, 'img/gotodixiacheng.jpg'):
                            self.is_dixiacheng_end = 1
                            self.click(830, 503)
                            break
                    self.click(830, 503)  # 点下一步 避免guochang可能失败
                    break
            time.sleep(3)
            self.click(1, 1)  # 取消显示结算动画
            time.sleep(1)
