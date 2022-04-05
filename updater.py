import os
import shutil
import time
import zipfile

import requests
from requests.adapters import HTTPAdapter

from core.pcr_config import trace_tree
from main_new import script_version


class Pcr_Downloader:
    file_name = 'Princess-connection-farm.zip'
    opt = ['users', 'tasks', 'batches', 'xls', 'log', 'error_screenshot', 'schedules', 'groups', 'config.ini',
           'rec', 'switches', 'customtask', 'debug_imgs', 'ocrfix', 'outputs', 'PCRError', 'idcard.json']
    # update_list = ['adb', 'api', 'automator_mixins', 'core', 'docs', 'equip', 'img', 'pcrdata', 'scenes', 'webclient',
    #                '.gitignore', 'app.py']
    download_url_dict = {
        'github_url': f'https://github.com/SimonShi1994/Princess-connection-farm/archive/{trace_tree}.zip',
        'github_us1_url': f'https://gh.con.sh/https://github.com/SimonShi1994/Princess-connection-farm/archive/{trace_tree}'
                          f'.zip',
        'github_us2_url': f'https://gh.api.99988866.xyz/https://github.com/SimonShi1994/Princess-connection-farm/archive'
                          f'/{trace_tree}.zip ',
        'github_jp1_url': f'https://download.fastgit.org/SimonShi1994/Princess-connection-farm/archive/{trace_tree}.zip',
        'github_jp2_url': f'https://github.xiu2.xyz/https://github.com/SimonShi1994/Princess-connection-farm/archive'
                          f'/{trace_tree}'
                          f'.zip ',
        'github_kr_url': f'https://ghproxy.com/https://github.com/SimonShi1994/Princess-connection-farm/archive/'
                         f'{trace_tree}.zip',
        'github_hk_url': f'https://pd.zwc365.com/seturl/https://github.com/SimonShi1994/Princess-connection-farm/archive'
                         f'/{trace_tree}.zip ',
        'github_cn_url1': f'https://ghproxy.com/https://github.com/SimonShi1994/Princess-connection-farm/archive'
                          f'/{trace_tree}.zip ',
        'github_cn_url2': f'https://g.0x6.xyz/https://github.com/SimonShi1994/Princess-connection-farm/archive'
                          f'/{trace_tree}.zip ',
        'github_cn_url3': f'https://gitee.com/klctiy/Princess-connection-farm/repository/archive/'
                          f'/{trace_tree}.zip '
    }
    download_url_list = ['_', 'github_url', 'github_us1_url', 'github_us2_url', 'github_jp1_url', 'github_jp2_url',
                         'github_kr_url', 'github_hk_url', 'github_cn_url1', 'github_cn_url2', 'github_cn_url3']
    req = requests.session()

    def introduction(self):
        try:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=5))
            s.mount('https://', HTTPAdapter(max_retries=5))
            # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')  # 改变标准输出的默认编码
            api_url = f"https://api.github.com/repos/SimonShi1994/Princess-connection-farm/commits/{trace_tree}"
            all_info = s.get(api_url)
            if all_info.status_code == 403:
                update_info = "最新版本为 {请求频繁，当前无法连接到github！请休息2分钟后再试}"
            elif all_info.status_code == 200:
                all_info = all_info.json()
                new_time = all_info["commit"].get("committer").get("date")
                new_messages = all_info["commit"].get("message")
                update_info = f"{trace_tree}分支最新版本为 {new_time} -> 更新内容为 {new_messages}"
            else:
                update_info = "最新版本为 {当前无法连接到github！}"
        except:
            update_info = "最新版本为 {当前无法连接到github！}"
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('Github项目 Princess connection 公主连结农场脚本 更新工具 v2.2 \n'
              'Write By Yuki_Asuuna\nUpdate By CyiceK')
        print('请将本程序放在git clone的文件夹下')
        print('本程序仅供普通用户使用，原项目开发人员还是老老实实用git吧^_^')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print(f'当前检测版本分支为{trace_tree}')
        print(f'当前检测目前版本为{script_version}')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print(f'当前检测目前最新版本为：{update_info}')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

    def abortion(self):
        os.system('pause')
        exit(-1)

    def __init__(self):
        self.introduction()
        cmd, update_way = self.select_connect()
        cmd = int(cmd)
        self.update_way = int(update_way)
        dst_url = self.download_url_dict[self.download_url_list[cmd]]
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
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
                    try:
                        self.r = self.req.get(dst_url, stream=True)
                    except Exception as e:
                        print('找不到目标资源，可能原链接已经失效！用下面的链接手动下载吧')
                        print('手动下载后把压缩包扔到同目录再跑更新后任选一线路也能更新哦')
                        print(dst_url)
                        os.system('pause')
                        exit(0)
        else:
            print('找不到目标资源，可能原链接已经失效！用下面的链接手动下载吧')
            print('手动下载后把压缩包扔到同目录再跑更新后任选一线路也能更新哦')
            print(dst_url)
            os.system('pause')
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

        if os.path.exists('Princess-connection-farm-master'):
            print('删除当前目录下的文件夹Princess-connection-farm-master')
            shutil.rmtree('Princess-connection-farm-master')  # 用shutil模块删除文件夹

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
            if fn in self.opt:  # 如果是用户文件
                try:
                    print('迁移文件[%s]-->[Princess-connection-farm]' % fn)
                    if fn == 'config.ini':
                        print('>>>config由于特殊性，请自行对比更新目录下config_old，自行替换更新')
                        shutil.copy('config.ini', dst + '/config_old.ini')
                    else:
                        if os.path.isfile(fn):
                            shutil.copy(fn, dst + '/' + fn)
                        elif os.path.isdir(fn):
                            shutil.copytree(fn, dst + '/' + fn)
                except Exception as e:
                    print(e, '在迁移当前文件的过程中发生了意外的错误，程序终止！')
                    self.abortion()
        print('迁移完成！最新版本在当前目录下的[Princess-connection-farm]文件夹下.')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        time.sleep(1)

    def update_user_option(self):
        # 用户所的配置文件
        if not os.path.exists('config.ini'):
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print('找不到与用户配置相关的信息...用户信息更新失败！')
            self.remove_zip()
            self.abortion()

        print('正在更新...')
        dst = os.getcwd().replace('\\', '/')
        for fn in os.listdir(dst + '/Princess-connection-farm'):  # 遍历Princess-connection-farm文件夹
            # print(file,type(file))
            # fn为目录下所有文件的文件名
            if fn not in self.opt:  # 如果不是是用户文件
                try:
                    print('正在同步覆盖中[%s]' % fn)
                    if fn == 'config.ini':
                        print('>>>config由于特殊性，请自行对比目录下config_old，自行替换变量更新')
                        shutil.copy('config.ini', '/config_old.ini')
                    else:
                        if fn == 'updater.py':
                            print('不覆盖本更新文件')
                            continue

                        if os.path.isfile(fn):
                            shutil.copy(dst + '/Princess-connection-farm/' + fn,
                                        os.getcwd().replace('\\', '/') + '/')
                        elif os.path.isdir(fn):
                            if os.path.exists(os.getcwd().replace('\\', '/') + '/' + fn):
                                shutil.rmtree(os.getcwd().replace('\\', '/') + '/' + fn)
                            shutil.copytree(dst + '/Princess-connection-farm/' + fn,
                                            os.getcwd().replace('\\', '/') + '/' + fn)
                except Exception as e:
                    print(e, '在更新的过程中发生了意外的错误，程序终止！')
                    self.abortion()
        print('更新完成')
        if os.path.exists('Princess-connection-farm'):
            print('删除当前目录下的文件夹Princess-connection-farm')
            shutil.rmtree('Princess-connection-farm')  # 用shutil模块删除文件夹
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
              '中国香港镜像\n8.github中国节点1\n9.github中国节点2\n10.gitee码云镜像')
        cmd = input('请选择下载线路：')
        print('----更新方式----')
        print('1.在本目录下新建文件夹更新\n2.覆盖常规更新[请自行做好相应的备份！]')
        update_way = input('请选择更新方式：')
        if '1' <= cmd <= 'A' and '1' <= update_way <= '2':
            print('下载中>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            os.system("taskkill /im adb.exe /f")
            return cmd, update_way
        else:
            print('输入数字有误')
            print(cmd, update_way)
            return self.select_connect()

    def sel_update_way(self):
        if self.update_way == 1:
            a.move_user_option()
        elif self.update_way == 2:
            a.update_user_option()


if __name__ == '__main__':
    a = Pcr_Downloader()
    if not os.path.exists(a.file_name):
        a.download()
    a.unzip()
    a.sel_update_way()
    a.remove_zip()
    os.system('pause')
