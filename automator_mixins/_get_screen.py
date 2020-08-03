import websocket
import _thread as thread
import time
import threading
from core.Automator import Automator
from pcr_config import fast_screencut_delay

lock = threading.Lock()


class ReceiveFromMinicat:
    def __init__(self,lport):
        # 当前最后接收到的1帧数据
        self.receive_data = bytes()
        # 接收标志位（每次接收1帧都会重置）
        self.receive_flag = 0
        # 关闭接收线程
        self.receive_close = 0
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp('ws://localhost:{}/minicap'.format(lport),
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_error=self.on_error)
        self.ws.on_open = self.on_open

    def on_open(ws):
        def run(*args):
            while rfm.receive_close == 0:
                # 此处的sleep为刷新图的时间
                time.sleep(fast_screencut_delay)
                rfm.receive_img()
            time.sleep(1)
            rfm.receive_close = 0
            rfm.ws.close()
            print("截图线程关闭...")

        thread.start_new_thread(run, ())

    def on_message(ws, message):
        if message is not None:
            if rfm.receive_flag is 1:

                if isinstance(message, (bytes, bytearray)):
                    lock.acquire()
                    rfm.receive_data = message
                    lock.release()
                else:
                    print(message)

                lock.acquire()  # 操作前加锁
                rfm.receive_flag = 0;
                rfm.receive_data
                lock.release()

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print("### closed ###")

    class ReceiveThread(threading.Thread):
        def __init__(self, ws):
            super().__init__()
            self.ws = ws

        def run(self) -> None:
            self.ws.run_forever()

    # 开始接收1帧画面
    def receive_img(self):
        lock.acquire()  # 操作前加锁
        self.receive_data = bytes()
        self.receive_flag = 1
        lock.release()  # 完成操作解锁

        while self.receive_flag is 0:
            time.sleep(0.1)
        return self.receive_data


if __name__ == '__main__':
    a = Automator("emulator-5554")
    # 这个Automator只是需要他的端口而已
    rfm = ReceiveFromMinicat(a.lport)

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
