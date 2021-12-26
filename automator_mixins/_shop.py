import time
from automator_mixins._tools import ToolsMixin
from DataCenter import LoadPCRData


class ShopMixin(ToolsMixin):

    def buy_press(self):
        self.click(791, 435)
        # 点击购买
        time.sleep(1)
        self.click(591, 468)
        # 购买确认
        time.sleep(1.5)
        self.click(477, 473)
        # 买完提示
        time.sleep(2)

    def tick_frag(self, fraglist=None):
        if fraglist is None:
            print("无该类型碎片")
            return
        drag_count = 0
        buy_count = 0
        fc = [82, 150, 255]
        bc = [231, 277, 222]
        xcor = 705
        ycor = 437
        while True:

            if drag_count > 3:
                if self.check_color(fc, bc, xcor, ycor, color_type="rgb"):
                    if buy_count > 0:
                        self.buy_press()
                        return
                return

            for frag_ in fraglist[:]:
                imgpath_ = self.get_frag_img_path(charname=frag_)
                a = self.click_frag(imgpath=imgpath_)
                if a == 0:
                    buy_count += 1
                    fraglist.remove(frag_)
                    print(fraglist)
                    if len(fraglist) == 0:
                        self.buy_press()
                        return
                    else:
                        continue
                else:
                    self.dragdown()
                    drag_count = drag_count + 1
                    continue

    def get_frag_img_path(self, charname):
        data = LoadPCRData()
        a = str(data.get_id(name=charname))
        b = str("3" + a[0:4])
        imgpath = "img/shop/frags/" + b + ".bmp"
        return imgpath

    def click_frag(self, imgpath):
        # 寻找单个碎片，确认碎片图片中心点
        r_list = self.img_where_all(img=imgpath, at=(241, 105, 925, 392))
        # 根据偏移，点击勾选碎片
        if len(r_list) > 2:
            x_arg = int(r_list[0]) + 57
            y_arg = int(r_list[1]) - 16
            self.click(x_arg, y_arg)
            return 0
        else:
            return 2

    def dragdown(self):
        obj = self.d.touch.down(584, 377)
        time.sleep(0.1)
        obj.move(584, 110)
        time.sleep(0.8)
        obj.up(584, 110)
        time.sleep(3)

    def buy_all_frag(self, dxc_fraglist=None, jjc_fraglist=None, pjjc_fraglist=None, clan_fraglist=None):
        self.lock_home()
        # 进入商店
        self.click(617, 435)
        time.sleep(2)
        # 地下城碎片
        self.click(359, 65)
        time.sleep(2)
        self.tick_frag(fraglist=dxc_fraglist)
        print("地下城购买完毕")
        time.sleep(2)
        # JJC碎片
        self.click(454, 65)
        time.sleep(2)
        self.tick_frag(fraglist=jjc_fraglist)
        print("JJC购买完毕")
        time.sleep(2)
        # PJJC碎片
        self.click(543, 65)
        time.sleep(2)
        self.tick_frag(fraglist=pjjc_fraglist)
        print("PJJC购买完毕")
        time.sleep(2)
        # 行会碎片
        self.click(640, 65)
        time.sleep(2)
        self.tick_frag(fraglist=clan_fraglist)
        print("行会购买完毕")
        self.lock_home()
