import requests
import threading
import re
import os
import time
import zipfile
import shutil

class Pcr_Downloader:
    file_name = 'Princess-connection-farm.zip'
    dst_url = 'https://github.com/SimonShi1994/Princess-connection-farm/archive/master.zip'

    def introduction(self):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('Github项目 Princess connection 公主连结农场脚本 更新工具 v1.0 By Yuki_Asuuna')
        print('请将本程序放在git clone的文件夹下')
        print('本程序仅供普通用户使用，原项目开发人员还是老老实实用git吧^_^')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    def abortion(self):
        os.system('pause')
        exit(-1)

    def __init__(self):
        self.introduction()
        try:
            self.r = requests.get(self.dst_url)
        except:
            print('获取目标资源失败，请检查网络以及防火墙设置！\n')
            exit(-1)
        if self.r.status_code == 200:
            # self.download()
            print('成功读取目标链接！\n')
            print('读取文件大小中...\n')
            # 文件大小可能存在无法读取的情况
            while True:
                if 'Content-Length' in self.r.headers:
                    self.total_size = self.getsize()
                    print('文件大小为：%.2fMB' % (self.total_size / 1024 / 1024))
                    break
                else:
                    self.r = requests.get(self.dst_url, stream=True)
        else:
            print('找不到目标资源，可能原链接已经失效！\n')
            exit(0)

    def getsize(self):
        self.file_total = self.r.headers['Content-Length']  # 获取下载文件大小
        return int(self.file_total)

    def download(self):
        with open(self.file_name, "wb") as fp:
            dl = 0
            for chunk in self.r.iter_content(chunk_size=1024):  # 边下载边存盘
                if chunk:
                    fp.write(chunk)
                    dl += len(chunk)
                    self.view_bar(dl, self.total_size)
        print('下载完成！\n')

    def view_bar(self, now, total):  # 显示进度条
        rate = now / total
        rate_num = int(rate * 100)
        number = int(50 * rate)
        r = '\r[%s%s]%d%%' % ("#" * number, " " * (50 - number), rate_num,)
        print("\r {}".format(r), end=" ")  # \r回到行的开头

    def unzip(self):

        if os.path.exists('Princess-connection-farm'):
            print('删除当前目录下的文件夹Princess-connection-farm\n')
            shutil.rmtree('Princess-connection-farm')#用shutil模块删除文件夹

        print('解压中...\n')
        if zipfile.is_zipfile(self.file_name):
            f = zipfile.ZipFile(self.file_name, 'r')
            for file in f.namelist():
                f.extract(file, os.getcwd())
            os.rename('Princess-connection-farm-master', 'Princess-connection-farm')  # 重命名文件夹
            print('解压完成！\n')
        else:
            print('压缩文件损坏！退出更新程序...\n')
            self.abortion()

    def move_user_option(self):
        opt = ['zhanghao.txt', 'zhanghao_init.txt', 'zhanghao2.txt', 'baiduocr.txt', '40_1.txt', '40_2.txt',
               '40_huizhang.txt']
        # 用户所的配置文件
        if not os.path.exists('zhanghao.txt'):
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print('找不到与用户配置相关的信息...用户信息迁移失败！')
            print('如果你希望迁移你之前的帐号信息，请将本程序放到原pcrfarm文件夹中运行！')
            print('最新版本已保存在文件夹Princess-connection-farm内！（当然你可以选择删除它）')
            self.remove_zip()
            self.abortion()

        print('正在迁移先前用户配置信息...')
        dst=os.path.join(os.getcwd(),'Princess-connection-farm')
        for fn in os.listdir():  # 遍历当前文件夹
            #print(file,type(file))
            #fn为目录下所有文件的文件名
            if fn in opt:  # 如果是用户文件
                try:
                    print('迁移文件[%s]-->[Princess-connection-farm]'%(fn))
                    shutil.copy(fn,dst)
                except:
                    print('在迁移当前文件的过程中发生了意外的错误，程序终止！')
                    self.abortion()
        print('迁移完成！最新版本在当前目录下的[Princess-connection-farm]文件夹下.')
        time.sleep(1)

    def remove_zip(self):
        try:
            print('删除原压缩包...')
            time.sleep(1)
            os.remove(self.file_name)
            print('删除成功！')
        except:
            print('[未知错误]删除原压缩包失败！')

if __name__ == '__main__':
    a = Pcr_Downloader()
    a.download()
    a.unzip()
    a.move_user_option()
    a.remove_zip()
    os.system('pause')