import websocket
import _thread as thread
import time
import threading
from core.Automator import Automator
from pcr_config import fast_screencut_delay

lock = threading.Lock()


class ReceiveFromMinicap:
    def __init__(self, lport):
        # 当前最后接收到的1帧数据
        self.receive_data = bytes()
        # 接收标志位（每次接收1帧都会重置）
        self.receive_flag = 0
        # 关闭接收线程
        self.receive_close = 0
        # 这里设置websocket
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp('ws://localhost:{}/minicap'.format(lport),
                                         # 这三个回调函数见下面
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_error=self.on_error)
        self.ws.on_open = self.on_open

    def on_open(ws):
        def run(*args):
            # 只要不设置关闭线程位，就一直循环
            while rfm.receive_close == 0:
                # 此处的sleep为接收图像的间隔
                time.sleep(fast_screencut_delay)
                rfm.receive_img()
            time.sleep(1)
            # 恢复receive_close
            rfm.receive_close = 0
            # 关闭ws
            rfm.ws.close()
            print("截图线程关闭...")

        thread.start_new_thread(run, ())

    # 接收信息回调函数，此处message为接收的信息
    def on_message(ws, message):
        if message is not None:
            if rfm.receive_flag is 1:
                # 如果不是bytes，那就是图像
                if isinstance(message, (bytes, bytearray)):
                    lock.acquire()
                    rfm.receive_data = message
                    lock.release()
                else:
                    print(message)

                lock.acquire()  # 操作前加锁
                rfm.receive_flag = 0
                lock.release()

    # 错误回调函数
    def on_error(ws, error):
        print(error)

    # 关闭ws的回调函数
    def on_close(ws):
        print("### closed ###")

    # 开始接收1帧画面
    def receive_img(self):
        lock.acquire()  # 操作前加锁
        self.receive_data = bytes()
        self.receive_flag = 1
        lock.release()  # 完成操作解锁

        while self.receive_flag is 0:
            time.sleep(0.1)
        return self.receive_data

    # ws线程类
    class ReceiveThread(threading.Thread):
        def __init__(self, ws):
            super().__init__()
            self.ws = ws

        def run(self) -> None:
            self.ws.run_forever()


if __name__ == '__main__':
    a = Automator("emulator-5554")
    # 这个Automator只是需要他的端口而已
    rfm = ReceiveFromMinicap(a.lport)

    # 启动线程
    socket_thread = rfm.ReceiveThread(rfm.ws)
    socket_thread.start()

    time.sleep(5)

    for i in range(50):
        with open("test/testMC.jpg", "wb") as f:
            f.write(rfm.receive_data)
        time.sleep(1)

    rfm.receive_close = 1
    socket_thread.join()
