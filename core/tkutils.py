import threading
import tkinter


def OtherThread(fun, join=True):
    def newfun(*args, **kwargs):
        T = threading.Thread(target=fun, args=args, kwargs=kwargs)
        T.start()
        if join:
            T.join()

    return newfun


@OtherThread
def MessageBox(title="", desc="点击确定继续", geo=None):
    root = tkinter.Tk()
    root.title(title)  # 标题
    root.wm_attributes('-topmost', 1)
    root.geometry(geo)
    root.resizable(False, False)  # 固定窗体
    mylabel = tkinter.Label(root, text=desc)  # 建立文本标签
    mylabel.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)  # 设置文本标签的摆放位置
    mylabel.pack()
    create = tkinter.Button(root, text='确认', command=root.quit, bg="green")  # 创建按钮组件，点击按钮出现弹窗
    create.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER, width=100)  # 设置按钮组件的摆放位置
    create.pack()
    root.mainloop()


if __name__ == "__main__":
    MessageBox()
