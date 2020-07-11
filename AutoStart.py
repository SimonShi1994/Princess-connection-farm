# coding=utf-8
import os
import sys, getopt
import time


# 控制台路径
console_path = ""
# console_path = "D:\leidian\LDPlayer\\"
# 控制台执行器
console_executor = "dnconsole.exe"
# 启动命令
command = "launch"
# 参数组, 方便后期扩展
params = list()
# 每个模拟器的启动间隔, 默认5秒
duration = 5
# 启动模拟器数量, 默认一个
default_num = 1
# 最大重启次数
max_restart_num = 3
# 重启间隔
restart_duration = 3

def add_index_flag(num):
	for i in range(int(num)):
		params.append(("--index", str(i)))

def start(launch_command):
	if os.system(launch_command) != 0:
		print ("启动模拟器失败")
		# 最多重试三次
		for i in range(1, max_restart_num + 1):
			if os.system(launch_command) != 0:
				print ("第 {} 次重启失败".format(i))
				time.sleep(restart_duration)
				continue
			else:
				print ("第 {} 次重启成功".format(i))
				break
		else:
			print ("重启到达最大次数，退出程序")
			exit(1)
	else:
		print ("启动模拟器成功")

if __name__ == "__main__":
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hn:d:p:",["num=", "duration=", "path="])
	except Exception as e:
		print ('简单示例: python AutoStar.py -p D:\leidian\LDPlayer\ -n 1 -d 5')
		exit(1)
	for opt, arg in opts:
		if opt == '-h':
			print ("启动前请现在雷电多开器中创建好对应的模拟器副本 \n\
-p 指定 dnconsole.exe 的运行路径\n\
-n 指定多开模拟器数量\n\
-d 指定多开模拟器启动间隔\n\
-h 帮助\n\
简单示例: python AutoStar.py -p D:\leidian\LDPlayer\ -n 1 -d 5")
			exit(0)
		# 启动数量
		elif opt in ("-n", "--num"):
			add_index_flag(arg)
		# 启动间隔
		elif opt in ("-d", "--duration"):
			duration = int(arg)
		# 启动路径
		elif opt in ("-p"):
			console_path = arg
	index_list = list()
	param_list = list()

	# 拆分全局参数集合
	for param in params:
		if "--index" in param:
			index_list.append(param)
		else:
			param_list.append(param[0])
			param_list.append(param[1])

	# 没有传递启动数量时使用默认数量
	if not index_list:
		for i in range(default_num):
			index_list.append(("--index", str(i)))

	print(index_list)
	for index in index_list:
		launch_command = "{}{} {} {} {}".format(
				console_path, console_executor, command,
				 ' '.join(index), 
				 ' '.join(param_list)
			)
		print (launch_command)

		start(launch_command)
		if duration:
			time.sleep(duration)

	# TODO 封装 main.py 的启动逻辑直接启动脚本