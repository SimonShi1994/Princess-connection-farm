"""
如果pip -r requirements.txt并不给力，
那你可以试试这个偏方 （
"""

import importlib
import subprocess
import sys


def is_installed(packetname):
    try:
        importlib.import_module(packetname)
        return True
    except:
        return False


USE_PIP = "pip"
USE_I = r"https://pypi.tuna.tsinghua.edu.cn/simple/"


def install(packetname, pipname=None, use_i=None, user=False):
    if pipname is None:
        pipname = packetname
    if use_i is None:
        use_i = USE_I
    Order = [USE_PIP, "install", pipname, "-i", use_i]
    if user:
        Order += ["--user"]
    subprocess.call(Order)

    if packetname is not None:
        if is_installed(packetname):
            print(packetname, "安装成功！")
        else:
            print(packetname, "安装失败！")


def check_call(line):
    try:
        subprocess.call([line], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False


if __name__ == "__main__":
    print("正在检查pip是否在环境变量中……")
    if check_call("pip3"):
        USE_PIP = "pip3"
    elif check_call("pip"):
        USE_PIP = "pip"
    else:
        print("PATH中找不到pip或者pip3！请手动输入其位置：")
        USE_PIP = input(">>> ")
        if not check_call(USE_PIP):
            print(USE_PIP, "无法调用！")
            exit()
    print("使用PIP：", USE_PIP)
    Ver = sys.version_info[1]
    print("--------------------主体部分----------------------")
    print("必须全部安装。")
    print("正在安装：数据与图像处理相关基本库……")
    install("numpy", "numpy==1.18.1", user=True)
    install("pandas", "pandas==1.1.0")
    install("matplotlib", "matplotlib==3.3.0")
    install("cv2", "opencv-python==4.1.1.26")
    install("PIL", "pillow==7.2.0")
    install("yaml", "pyyaml==5.1.2")
    print("正在安装：多进程相关库……")
    install("gevent", "gevent==20.6.2")
    print("正在安装：暂停相关库……")
    install("keyboard", "keyboard==0.13.5")
    print("正在安装：adb操作相关库……")
    install("adbutils", "adbutils==0.8.1")
    install("uiautomator2", "uiautomator2==2.10.0")
    print("正在安装：快速截图相关库……")
    install("websocket", "websocket-client==0.57.0")
    print("正在安装：系统状态库……")
    install("psutil", "psutil==5.7.2")
    print("正在安装：xls表格操作库……")
    install("xlrd", "xlrd==1.2.0")
    install("xlutils", "xlutils==2.0.0")
    print("--------------------app部分---------------------")
    print("不使用OCR可以不安装。")
    install("flask", "flask==1.1.2")
    install(None, "flask-marshmallow==0.13.0")
    install(None, "flask-cors==3.0.8")
    install("flasgger", "flasgger==0.9.5")
    print("--------------------OCR部分----------------------")
    print("不使用OCR可以不安装。")
    print("正在安装：本地OCR相关库……")
    print("如果不使用本地OCR，可以不用安装。")
    install("tensorflow", "tensorflow==2.1.0", user=True)
    install("muggle_ocr", "muggle-ocr==1.0.3", user=True)
    print("正在安装：网络OCR相关库……")
    print("如果不使用网络OCR，可以不用安装。")
    install("aip", "baidu-aip==2.2.18.0")
    print("正在安装：protobuf……")
    if Ver == 7:
        install(None, "protobuf==3.11.2", user=True)
    else:
        install(None, "protobuf", user=True)
    print("-------------------数据中心部分---------------------")
    print("不使用数据中心可以不安装。")
    print("正在安装：拼音库……")
    install("pypinyin", "pypinyin==0.40.0")
    print("正在安装：高级显示库……")
    install("rich", "rich==9.4.0")
    print("正在安装：优化相关库……")
    install("cvxpy", "cvxpy==1.1.7")
    install(None, "cvxopt==1.2.5.post1")
    print("正在安装：数据库相关库……")
    install("brotli")
    print("全部安装结束！")
    input("按下回车继续。")
