import threading
import time
import tkinter


def OtherThread(join=False):
    def wrap(fun):
        def newfun(*args, **kwargs):
            T = threading.Thread(target=fun, args=args, kwargs=kwargs)
            T.start()
            if join:
                T.join()

        return newfun

    return wrap


def BaseMsgBox(title="", desc="点击确定继续", geo=None, timeout=0):
    root = tkinter.Tk()
    root.title(title)  # 标题
    root.wm_attributes('-topmost', 1)
    root.geometry(geo)
    root.resizable(False, False)  # 固定窗体
    mylabel = tkinter.Label(root, text=desc)  # 建立文本标签
    mylabel.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)  # 设置文本标签的摆放位置
    mylabel.pack()
    if timeout > 0:
        timelabel = tkinter.Label(root, text="")  # 计时器
        timelabel.pack()
        now = time.time()

        def updatetimer():
            diff = time.time() - now
            timelabel.configure(text=f"剩余{int(timeout - diff)}s")
            if timeout - diff <= 0:
                root.quit()
            else:
                root.after(100, updatetimer)

        updatetimer()
    create = tkinter.Button(root, text='确认', command=root.quit, bg="green")  # 创建按钮组件，点击按钮出现弹窗
    create.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER, width=100)  # 设置按钮组件的摆放位置
    create.pack()
    root.mainloop()


def TimeoutMsgBox(title="", desc="点击确定继续", geo=None, timeout=0, join=False):
    OtherThread(join)(BaseMsgBox)(title, desc, geo, timeout)
