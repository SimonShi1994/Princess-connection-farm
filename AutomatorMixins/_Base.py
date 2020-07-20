import time
import uiautomator2 as u2
from cv import UIMatcher

class BaseMixin:
    def __init__(self, device: u2.Device):
        """
        device: 如果是 USB 连接，则为 adb devices 的返回结果；如果是模拟器，则为模拟器的控制 URL 。
        """
        self.device = device
        self.dWidth, self.dHeight = self.device.window_size()

    def click(self, x, y, pre_delay = 0, post_delay = 0):
        """ 点击坐标 """
        time.sleep(pre_delay)
        self.device.click(x, y)
        time.sleep(post_delay)

    def find_img(self, img, at=None, alldelay=0.5,
        ifclick=[], ifbefore=0.5, ifdelay=1,
        elseclick=[], elsedelay=0.5, retry=0):
        """
        前身：lockimg
        匹配图片并点击指定坐标

            Parameters:
                img (str): 要匹配的图片目录
                at (:tuple: `(int: 左上x, int: 左上y, int: 右下x, int: 右下y)`): 查找范围
                ifbefore (float): 识别成功后延迟点击时间
                ifclick (:list: ``): 在识别到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
                ifdelay: 上述点击后延迟的时间
                elseclick: 在找不到图片时要点击的坐标，列表，列表元素为坐标如(1,1)
                elsedelay: 上述点击后延迟的时间
                retry: elseclick最多点击次数, `0为无限次`

            Returns:
                success (bool): 是否在retry次内点击成功
        """
        # 2020-07-12 Add: 增加了ifclick,elseclick参数对Tuple的兼容性
        # 2020-07-14 Add: added retry
        if type(ifclick) is tuple:
            ifclick = [ifclick]
        if type(elseclick) is tuple:
            elseclick = [elseclick]

        inf_attempt = True if retry == 0 else False
        attempt = 0
        while inf_attempt or attempt < retry:
            screen_shot = self.device.screenshot(format="opencv")
            if UIMatcher.img_where(screen_shot, img, at=at):
                # 成功匹配图片
                for clicks in ifclick:
                    self.click(clicks[0], clicks[1], pre_delay=ifbefore, post_delay=ifdelay)
                break

            for clicks in elseclick:
                self.click(clicks[0], clicks[1], post_delay=elsedelay)
            time.sleep(alldelay)
            attempt += 1
        return True if inf_attempt or attempt < retry else False
