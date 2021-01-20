import os
import shutil
import time
import zipfile

import requests


class Pcr_Downloader:
    file_name = 'Princess-connection-farm.zip'
    download_url_dict = {
        'github_url': 'https://github.com/SimonShi1994/Princess-connection-farm/archive/master.zip',
        'github_us1_url': 'https://gh.con.sh/https://github.com/SimonShi1994/Princess-connection-farm/archive/master'
                          '.zip',
        'github_us2_url': 'https://gh.api.99988866.xyz/https://github.com/SimonShi1994/Princess-connection-farm/archive'
                          '/master.zip ',
        'github_jp1_url': 'https://download.fastgit.org/SimonShi1994/Princess-connection-farm/archive/master.zip',
        'github_jp2_url': 'https://github.xiu2.xyz/https://github.com/SimonShi1994/Princess-connection-farm/archive'
                          '/master'
                          '.zip ',
        'github_kr_url': 'https://ghproxy.com/https://github.com/SimonShi1994/Princess-connection-farm/archive/master'
                         '.zip',
        'github_hk_url': 'https://pd.zwc365.com/seturl/https://github.com/SimonShi1994/Princess-connection-farm/archive'
                         '/master.zip ',
    }
    download_url_list = ['_', 'github_url', 'github_us1_url', 'github_us2_url', 'github_jp1_url', 'github_jp2_url',
                         'github_kr_url', 'github_hk_url']
    req = requests.session()

    def introduction(self):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('Github项目 Princess connection 公主连结农场脚本 更新工具 v2.0 \n'
              'Write By Yuki_Asuuna\nUpdate By CyiceK')
        print('请将本程序放在git clone的文件夹下')
        print('本程序仅供普通用户使用，原项目开发人员还是老老实实用git吧^_^')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    def abortion(self):
        os.system('pause')
        exit(-1)

    def __init__(self):
        self.introduction()
        cmd = self.select_connect()
        cmd = int(cmd)
        dst_url = self.download_url_dict[self.download_url_list[cmd]]
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/87.0.4280.141 Safari/537.36 '
            }
            self.r = self.req.get(dst_url, headers=headers)
        except:
            print('获取目标资源失败，请检查网络以及防火墙设置！\n')
            exit(-1)
        if self.r.status_code == 200:
            # self.download()
            print('成功读取目标链接！')
            print('读取文件大小中...')
            # 文件大小可能存在无法读取的情况
            while True:
                if 'Content-Length' in self.r.headers:
                    self.total_size = self.getsize()
                    print('文件大小为：%.2fMB' % (self.total_size / 1024 / 1024))
                    break
                else:
                    self.r = self.req.get(dst_url, stream=True)
        else:
            print('找不到目标资源，可能原链接已经失效！用下面的链接手动下载吧')
            print(dst_url)
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
        print('下载完成！')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    def view_bar(self, now, total):  # 显示进度条
        rate = now / total
        rate_num = int(rate * 100)
        number = int(50 * rate)
        r = '\r[%s%s]%d%%' % ("#" * number, " " * (50 - number), rate_num,)
        print("\r {}".format(r), end=" ")  # \r回到行的开头

    def unzip(self):

        if os.path.exists('Princess-connection-farm'):
            print('删除当前目录下的文件夹Princess-connection-farm')
            shutil.rmtree('Princess-connection-farm')  # 用shutil模块删除文件夹

        print('解压中...')
        if zipfile.is_zipfile(self.file_name):
            f = zipfile.ZipFile(self.file_name, 'r')
            for file in f.namelist():
                f.extract(file, os.getcwd())
            os.rename('Princess-connection-farm-master', 'Princess-connection-farm')  # 重命名文件夹
            print('解压完成！')
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        else:
            print('压缩文件损坏！退出更新程序...')
            self.abortion()

    def move_user_option(self):
        opt = ['users', 'tasks', 'batches', 'xls', 'log', 'error_screenshot', 'config.ini']
        # 用户所的配置文件
        if not os.path.exists('config.ini'):
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print('找不到与用户配置相关的信息...用户信息迁移失败！')
            print('如果你希望迁移你之前的帐号信息，请将本程序放到原pcrfarm文件夹中运行！')
            print('最新版本已保存在文件夹Princess-connection-farm内！（当然你可以选择删除它）')
            self.remove_zip()
            self.abortion()

        print('正在迁移先前用户配置信息...')
        dst = os.path.join(os.getcwd(), 'Princess-connection-farm')
        shutil.rmtree(dst + '/xls')
        for fn in os.listdir():  # 遍历当前文件夹
            # print(file,type(file))
            # fn为目录下所有文件的文件名
            if fn in opt:  # 如果是用户文件
                try:
                    print('迁移文件[%s]-->[Princess-connection-farm]' % fn)
                    if fn == 'config.ini':
                        print('>>>config由于特殊性，请自行对比更新目录下config_old，自行替换更新')
                        shutil.copy('config.ini', dst + '/config_old.ini')
                    else:
                        shutil.copytree(fn, dst+'/'+fn)
                except Exception as e:
                    print(e, '在迁移当前文件的过程中发生了意外的错误，程序终止！')
                    self.abortion()
        print('迁移完成！最新版本在当前目录下的[Princess-connection-farm]文件夹下.')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        time.sleep(1)

    def remove_zip(self):
        try:
            print('删除原压缩包...')
            time.sleep(1)
            os.remove(self.file_name)
            print('删除成功！')
        except:
            print('[未知错误]删除原压缩包失败！')

    def select_connect(self):
        print('----下载线路----')
        print('1.github官网\n2.github美国镜像1\n3.github美国镜像2\n4.github日本东京镜像1\n5.github日本东京镜像2\n6.github韩国首尔镜像\n7.github'
              '中国香港镜像')
        cmd = input('请选择下载线路：')
        if '1' <= cmd <= '7':
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            return cmd
        else:
            print('输入数字有误')
            return self.select_connect()


if __name__ == '__main__':
    a = Pcr_Downloader()
    a.download()
    a.unzip()
    a.move_user_option()
    a.remove_zip()
    os.system('pause')
