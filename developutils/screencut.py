import os
import sys
from tkinter import StringVar, Entry, Tk, Button, mainloop

import cv2
import matplotlib
from matplotlib import pyplot as plt

try:
    from core.Automator import Automator
except:
    sys.path.append("../")
    from core.Automator import Automator

def WindowMode(frame=None):
    if frame is None:
        try:
            matplotlib.use("Qt5Agg")
            print("Use Qt5Agg Frame")
            return
        except:
            pass
        try:
            matplotlib.use("Qt4Agg")
            print("Use Qt4Agg Frame")
            return
        except:
            pass
        try:
            matplotlib.use("TkAgg")
            print("Use TK Frame")
            return
        except:
            pass

        print("Can not find avalible frame! Please set frame manually")
        return
    else:
        try:
            matplotlib.use(frame)
            print(f"Use {frame} Frame")
            return
        except:
            print(f"{frame} Unavalible!")


def ImgCov(cvIMG):
    b, g, r = cv2.split(cvIMG)
    IMG = cv2.merge([r, g, b])
    return IMG


class ImgBox:
    def __init__(self, IMG=None, filepath=None, togrey=False, copy=True):
        # 可以传入一个cv2图像IMG，也可以导入一个filepath（如果IMG为None）
        if IMG is None:
            assert filepath is not None
            IMG = cv2.imread(filepath)
        if copy:
            self.IMG = IMG.copy()

        self.width = IMG.shape[1]
        self.height = IMG.shape[0]
        self.ndim = IMG.ndim
        if togrey and self.ndim == 3:
            self.self_gray()

    def self_gray(self):
        # 变灰度
        if self.ndim == 2:
            return self
        self.IMG = cv2.cvtColor(self.IMG, cv2.COLOR_BGR2GRAY)
        self.ndim = 2
        return self

    def self_bin(self, threshold="auto"):
        # 变二值
        if self.ndim == 3:
            self.self_gray()
        if threshold == "auto":
            self.IMG = cv2.adaptiveThreshold(self.IMG, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        else:
            self.IMG = (self.IMG > 255 * threshold).astype("uint8")
        return self

    def bin(self, threshold="auto"):
        return ImgBox(self.IMG).self_bin(threshold)

    def gray(self):
        return ImgBox(self.IMG).self_gray()

    def self_cut(self, x1, y1, x2, y2):
        # 自裁
        self.IMG = self.IMG[y1:y2 + 1, x1:x2 + 1]
        self.width = self.IMG.shape[1]
        self.height = self.IMG.shape[0]
        return self

    def cut(self, x1, y1, x2, y2):
        # 自己不变，返回剪裁后的图片
        return ImgBox(self.IMG).self_cut(x1, y1, x2, y2)

    def show(self, show=True, **kwargs):
        if self.ndim == 3:
            IMG = ImgCov(self.IMG)
            plt.imshow(IMG, **kwargs)
        else:
            IMG = self.IMG
            plt.imshow(IMG, cmap="gray", **kwargs)
        if show:
            plt.show()

    def save(self, filepath):
        if self.ndim == 3:
            IMG = ImgCov(self.IMG)
            plt.imsave(filepath, IMG)
        else:
            IMG = self.IMG
            plt.imsave(filepath, IMG, cmap="gray")

    def RotateClockWise90(self):
        trans_img = cv2.transpose(self.IMG)
        IMG = cv2.flip(trans_img, 0)
        self.width = IMG.shape[1]
        self.height = IMG.shape[0]
        self.IMG = IMG
        return self


class AutomatorDebuger(Automator):
    def __init__(self):
        super().__init__("debug")  # 设置为debug时，不会自动连接
        self._obj = {}

    @staticmethod
    def Init():
        os.system('cd .. & cd adb & adb connect 127.0.0.1:5554')  # 雷电模拟器
        os.system('python -m uiautomator2 init')

    def Connect(self, address="emulator-5554"):
        self.init_device(address)

    def Account(self, account):
        self.init_account(account)

    def Shot(self, file="test.bmp", show=True):
        self.d.screenshot(file)
        # AutoRotate
        img = ImgBox(filepath=file)
        if img.width < img.height:
            img.RotateClockWise90()
            print("自动旋转")
            img.save(file)
        if show:
            self.Show(file)

    def Show(self, file="test.bmp", at=None):
        img = ImgBox(filepath=file)
        self._obj = dict(txt=None, pnt=None, move=False, rec=None)
        if at is not None:
            img.self_cut(*at)

        def SaveFile():
            master = Tk()
            master.title("保存该区域的截图到文件")
            e = Entry(master, textvariable=StringVar(value="test.bmp"))
            e.pack()
            e.focus_set()

            def ok():
                x1, x2 = plt.xlim()
                y2, y1 = plt.ylim()
                x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
                addr = e.get()
                print(f"Save img at=({x1},{y1},{x2},{y2}) To {addr}")

                img.cut(x1, y1, x2, y2).save(addr)
                try:
                    img.cut(x1, y1, x2, y2).save(addr)
                except Exception as ee:
                    print(f"Error: {ee}")
                master.destroy()

            def cancel():
                master.destroy()

            b1 = Button(master, text="OK", width=10, command=ok)
            b2 = Button(master, text="CANCEL", width=10, command=cancel)
            b1.pack()
            b2.pack()
            mainloop()

        def OnClick(event):
            txt = self._obj["txt"]
            pnt = self._obj["pnt"]
            if event.button == 1 and not event.dblclick:
                # 单击，显示坐标,self.click
                try:
                    txt.remove()
                except:
                    pass
                try:
                    pnt.remove()
                except:
                    pass
                x = event.xdata
                y = event.ydata
                print(f"self.click({int(x)},{int(y)})")
                ax = plt.gca()
                txt = ax.text(plt.xlim()[0], plt.ylim()[0], "%d,%d" % (x, y), backgroundcolor="w")
                pnt = ax.scatter(x, y, 10, "red")
                ax.figure.canvas.draw()
                self._obj["txt"] = txt
                self._obj["pnt"] = pnt
            elif event.button == 1 and event.dblclick:
                # 双击，归位
                try:
                    txt.remove()
                except:
                    pass
                try:
                    pnt.remove()
                except:
                    pass
                plt.xlim([0, img.width])
                plt.ylim([img.height, 0])
                plt.gca().figure.canvas.draw()
            elif event.button == 2:
                # 中键，以当前的截图范围保存新的图片
                SaveFile()
            elif event.button == 3:
                # 右键，框选
                self._obj["x1"] = event.xdata
                self._obj["y1"] = event.ydata
                self._obj["move"] = True

        def OnMove(event):
            if self._obj["move"]:
                try:
                    self._obj["rec"].remove()
                except:
                    pass
                x1 = self._obj["x1"]
                y1 = self._obj["y1"]
                x2 = event.xdata
                y2 = event.ydata
                w = x2 - x1
                h = y2 - y1
                if w < 0:
                    w = -w
                    x1, x2 = x2, x1
                if h < 0:
                    h = -h
                    y1, y2 = y2, y1
                ax = plt.gca()
                self._obj["rec"] = ax.add_patch(plt.Rectangle((x1, y1), w, h, edgecolor="red", fill=False, linewidth=2))
                ax.figure.canvas.draw()

        def OnRelease(event):
            if self._obj["move"]:
                self._obj["move"] = False
                x1 = self._obj["x1"]
                y1 = self._obj["y1"]
                x2 = event.xdata
                y2 = event.ydata
                w = x2 - x1
                h = y2 - y1
                if w < 0:
                    w = -w
                    x1, x2 = x2, x1
                if h < 0:
                    h = -h
                    y1, y2 = y2, y1
                ax = plt.gca()
                try:
                    self._obj["rec"].remove()
                except:
                    pass
                x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
                plt.xlim([x1, x2])
                plt.ylim([y2, y1])
                ax.figure.canvas.draw()
                print(f"at=({x1},{y1},{x2},{y2})")

        img.show(False)
        ax = plt.gca()
        ax.figure.canvas.mpl_connect('button_press_event', OnClick)
        ax.figure.canvas.mpl_connect('motion_notify_event', OnMove)
        ax.figure.canvas.mpl_connect('button_release_event', OnRelease)
        plt.show(block=True)


if __name__ == "__main__":
    # WindowMode()  # 用窗口模式启动matplotlib，如果是pycharm打开需要用这个
    a = AutomatorDebuger()
    # a.Init()  # 初始化连接，打开安卓上的u2。只要运行一次即可。
    # a.Connect()  # 默认连接Connect(addr="emulator-5554")
    # a.Shot()  # 截图，存到"test.bmp"
    print("坐标小工具 By TheAutumnOfRice")
    print("help 查看帮助  exit 退出")
    while True:
        cmd = input("> ")
        cmds = cmd.split(" ")
        order = cmds[0]
        if order == "exit":
            break
        elif order == "help":
            print("坐标小工具帮助")
            print("init:  初始化与adb和u2的连接")
            print("connect [address]:  连接到address的device，默认emulator-5554")
            print("shot [file]: （需要connect）截图并保存到文件file并显示，默认test.bmp")
            print("show [file]: 打开文件file并显示，默认test.bmp")
            print("在图片显示界面：")
            print("单击左键： 显示当前点击位置的坐标")
            print("右键拖动： 框选小区域")
            print("单击中键： 把当前框选的小区域保存为新的图片")
            print("双击左键： 框选复位")
        elif order == "init":
            a.Init()
        elif order == "connect":
            if len(cmds) == 2:
                a.Connect(cmds[1])
            elif len(cmds) == 1:
                a.Connect()
            else:
                print("Wrong Order!")
        elif order == "shot":
            if len(cmds) == 2:
                a.Shot(cmds[1])
            elif len(cmds) == 1:
                a.Shot()
            else:
                print("Wrong Order!")
        elif order == "show":
            if len(cmds) == 2:
                a.Show(cmds[1])
            elif len(cmds) == 1:
                a.Show()
            else:
                print("Wrong Order!")
        else:
            print("Wrong Order!")
