from noneprompt import InputPrompt, CheckboxPrompt, Choice, ListPrompt, ConfirmPrompt
import os, zipfile, uuid, shutil, json
from enum import Enum, unique

from core.usercentre import AutomatorRecorder

'''
# 跑什么？
- 清日常
- 农场

'''

@unique
class AccountGroupMode(Enum):
  SINGLE_ACCOUNT = 0
  SAME_GROUP = 1
  MAIN_SUB_GROUP = 2
  ONE_TO_ONE_GROUP = 3


class GuideGroup():
  MAIN = "main"
  SUB = "sub"
  ALL = "all"

class GuideTask():
  SETTINGS = "settings"
  DAILY = "daily"
  DAILY_SUB = "daily_sub"
  QUEST = "quest"
  EVENT = "event"

def find_all_files(base):
    for root, _, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname

def get_daily_tplt() -> dict:
  tasks = [ {"type":"r13","buy_mana":False},
            {"type":"r10-n","team_order":"1-1","tu_order":[2,3,4]},
            {"type":"r12-n","team_order":"1-1","tu_order":[2]},
            {"type":"j1"},
            {"type":"j2"},
            {"type":"hd06","tu_order":[1,3,5],"code":"current","entrance_ind":"auto"},
            {"type":"hd04","team_order":"none","code":"current","entrance_ind":"auto"},
            {"type":"hd09","code":"current","entrance_ind":"auto"},
            {"type":"r5"},
            {"type":"r4"},
            {"type":"r8","qianghuashi":False},
            {"type":"r8-xd","buy_exp":True,"buy_equip":True},
            {"type":"r11"},
            {"type":"t5"} 
          ]
  return {"tasks": tasks}

def get_daily_sub_tplt() -> dict:
  tasks = [ 
            {"type":"t5"} 
          ]
  return {"tasks": tasks}

def get_farm_tplt() -> dict:
  tasks = [ 
            {"type":"t5"}
          ]
  return {"tasks": tasks}

def get_farm_sub_tplt() -> dict:
  tasks = [ 
            {"type":"h6","sortflag":1},
            {"type":"h1", "once_times":"1"} 
          ]
  return {"tasks": tasks}


def get_quest_tplt() -> dict:
  tasks = [
    {"type":"s9-t","mode":0,"from_":"new","to":"max","buy_tili":0,
    "xianding":True,"lose_action":"skip","win_without_threestar_is_lose":True,
    "team_order":"none","zhiyuan_mode":0},
    {"type":"s9-t","mode":1,"from_":"new","to":"max","buy_tili":0,
    "xianding":True,"lose_action":"skip","win_without_threestar_is_lose":True,
    "team_order":"none","zhiyuan_mode":0},
    {"type":"s9-t","mode":2,"from_":"new","to":"max","buy_tili":0,
    "xianding":True,"lose_action":"skip","win_without_threestar_is_lose":True,
    "team_order":"none","zhiyuan_mode":0}
    ]
  return {"tasks": tasks}

def get_event_tplt() -> dict:
  tasks = [
    {"type":"hd01","team_order":"zhanli","get_zhiyuan":False,"if_full":1,"code":"current","entrance_ind":"1"},
    {"type":"hd03","boss_type":"N","once":True,"team_order":"zhanli","code":"current","entrance_ind":"1"},
    {"type":"hd02","team_order":"zhanli","get_zhiyuan":False,"if_full":1,"code":"current","entrance_ind":"1"},
    {"type":"hd03","boss_type":"H","once":True,"team_order":"zhanli","code":"current","entrance_ind":"1"},
    {"type":"hd03","boss_type":"VH","once":True,"team_order":"zhanli","code":"current","entrance_ind":"1"}
    ]
  return {"tasks": tasks}

def get_settings_tplt() -> dict:
  tasks = [ 
            {"type":"t10"}
          ]
  return {"tasks": tasks}

def get_sub_schedule_tplt(name: str, batch: str) -> dict:
  return {
   "type": "asap",
   "name": name,
   "batchfile": batch,
   "condition": {},
   "record": 0
  }


if __name__ == "__main__":

  print("Princess connection 公主连结农场脚本v2.8.20240422")
  print("快速配置向导")

  is_backup_needed = False

  for dir in ['users', 'batches', 'groups', 'schedules', 'tasks']:
    # exists and not empty
    if os.path.exists(dir) and os.listdir(dir):
      is_backup_needed = ConfirmPrompt("检测到已有账号信息或计划配置，是否需要备份?", default_choice=True).prompt()
      break

  if is_backup_needed:
    zip_name = f"backup_{str(uuid.uuid4())[:8]}.zip"
    with zipfile.ZipFile(zip_name, 'w') as zip_file:
      for dir in ['users', 'batches', 'groups', 'schedules', 'tasks']:
        for fp in find_all_files(dir):
          zip_file.write(fp)
    print(f"原有文件已备份至{zip_name}")

  for dir in ['users', 'batches', 'groups', 'schedules', 'tasks']:
    if os.path.exists(dir):
      shutil.rmtree(dir)

  is_run_for_farm: bool = ListPrompt(
      "跑什么?",
      choices=[
          Choice("清日常", data=False),
          Choice("农场", data=True),
      ],
  ).prompt().data

  '''

  # 有多账号么？
  - 有
  - 没有
  '''

  is_multi_account: bool = ListPrompt(
      "有多账号么?",
      choices=[
          Choice("有", data=True),
          Choice("没有", data=False),
      ],
  ).prompt().data

  '''


  # 如何指派任务？

  - 所有账号运行同一套任务
  - 主号/小号(农场号)安排不同任务
  - 每个号各自安排任务

  '''

  # single account is the special case of same_group
  group_mode: AccountGroupMode = AccountGroupMode.SAME_GROUP

  if is_multi_account:
    group_mode = ListPrompt(
        "如何指派任务?",
        choices=[
            Choice("所有账号运行同一套任务", data=AccountGroupMode.SAME_GROUP),
            Choice("主号/小号(农场号)安排不同任务", data=AccountGroupMode.MAIN_SUB_GROUP),
            Choice("每个号各自安排任务", data=AccountGroupMode.ONE_TO_ONE_GROUP),
        ],
    ).prompt().data


  print("------ 账号登记 ------")

  is_on_registeration = True

  account_list = []
  password_list = []
  bili_id_list = []
  is_main_list = []

  while is_on_registeration:

    account = InputPrompt(f"请输入账号[{len(account_list)+1}]用户名(留空退出账户登记)").prompt()
    
    if not account and ConfirmPrompt("确定退出账号登记?", default_choice=True).prompt():
      is_on_registeration = False
      continue

    is_valid_password = False
    while not is_valid_password:
      password = InputPrompt(f"请输入账号[{len(account_list)+1}]密码", is_password=True,
                              validator=lambda x: x, error_message="密码不能为空！请重新输入").prompt()
      password_again = InputPrompt(f"请再次输入账号[{len(account_list)+1}]密码", is_password=True,
                                  validator=lambda x: x, error_message="密码不能为空！请重新输入").prompt()
      if password != password_again:
        print("两次输入的密码不一致，请重新输入！")
      else:
        is_valid_password = True


    bili_id = InputPrompt(f"请输入账号[{len(account_list)+1}]B站ID(不知道可留空)").prompt()

    print(bili_id)

    if is_multi_account and group_mode == AccountGroupMode.MAIN_SUB_GROUP:
      is_main_list.append(
        ListPrompt(
      f"账号[{len(account_list)+1}]({account})是否为主号?",
      choices=[
          Choice("主号", data=True),
          Choice("小号(农场号)", data=False),
          ]).prompt().data
      )
    else:
      is_main_list.append(True)

    account_list.append(account)
    password_list.append(password)  
    bili_id_list.append(bili_id)
    
    # Not needed for single account
    if not is_multi_account:
      break

  '''

  ------ 账号登记 ------

  # 请输入账号[1]用户名(留空退出账户登记)
  # 请输入账号[1]密码
  # 请输入账号[1]B站ID(不知道可留空)

  # 请输入账号[N]用户名
  # 请输入账号[N]密码
  # 请输入账号[N]B站ID(不知道可留空)


  '''

  if not len(account_list):
      print("ERROR: 你没有登记任何账号！向导将停止运行")
      exit

  print("------ 账号登记完毕 ------")

  # print(account_list)
  # print(password_list)
  # print(bili_id_list)

  # input("1234")

  '''

  ------ 推荐任务模板 ------
  '''
  print("我们准备了一套推荐任务模板\n[daily=日常, quest=主线推图, event=活动推图, settings=配置初始化]")
  is_using_default_tplt = ConfirmPrompt("是否使用推荐的任务模板? 如不使用，仅写入settings模板。\n", default_choice=True).prompt()

  if os.path.exists("rec"):
    if ConfirmPrompt("为避免运行错误，需要删除当日运行记录，是否继续？", default_choice=True).prompt():
      shutil.rmtree("rec")
    else:
      print("向导已停止运行")
      exit


  print("------ 配置生成中 ------")

  # Actually AutomatorRecorder will do this ...
  for dir in ['users', 'batches', 'groups', 'schedules', 'tasks']:
    os.makedirs(dir)

  # generate user
  for i in range(len(account_list)):
    a = AutomatorRecorder(account_list[i])
    d = dict(account=account_list[i], password=password_list[i])
    if bili_id_list[i]:
        d['biliname'] = bili_id_list[i]
    a.setuser(d)
  
  # generate groups
  if group_mode == AccountGroupMode.MAIN_SUB_GROUP or group_mode == AccountGroupMode.SAME_GROUP:
    main_list = []
    sub_list = []
    for i in range(len(account_list)):
      if is_main_list[i]:
        main_list.append(account_list[i])
      else:
        sub_list.append(account_list[i])
    AutomatorRecorder.setgroup(GuideGroup.MAIN, main_list)
    if not sub_list:
      AutomatorRecorder.setgroup(GuideGroup.SUB, sub_list)

  AutomatorRecorder.setgroup("all", account_list)

  # generate tasks
  if is_using_default_tplt:
    if group_mode != AccountGroupMode.ONE_TO_ONE_GROUP:
      AutomatorRecorder.settask(GuideTask.DAILY, get_farm_tplt() if is_run_for_farm else get_daily_tplt())
      AutomatorRecorder.settask(GuideTask.QUEST, get_quest_tplt())
      AutomatorRecorder.settask(GuideTask.EVENT, get_event_tplt())
      if group_mode == AccountGroupMode.MAIN_SUB_GROUP:
        AutomatorRecorder.settask(GuideTask.DAILY_SUB, get_farm_sub_tplt() if is_run_for_farm else get_daily_sub_tplt())
    else:
      for i in range(len(account_list)):
        AutomatorRecorder.settask(f"{GuideTask.DAILY}_{i+1}", get_farm_tplt() if is_run_for_farm else get_daily_tplt())
        AutomatorRecorder.settask(f"{GuideTask.QUEST}_{i+1}", get_quest_tplt())
        AutomatorRecorder.settask(f"{GuideTask.EVENT}_{i+1}", get_event_tplt())

  AutomatorRecorder.settask("settings", get_settings_tplt())

  # generate batches

  if is_multi_account and group_mode == AccountGroupMode.ONE_TO_ONE_GROUP:
    for i in range(len(account_list)):
      batch_dict_daily = {"batch": [{"account": account_list[i], "taskfile": f"{GuideTask.DAILY}_{i+1}", "priority": 3}]}
      batch_dict_quest = {"batch": [{"account": account_list[i], "taskfile": f"{GuideTask.QUEST}_{i+1}", "priority": 2}]}
      batch_dict_event = {"batch": [{"account": account_list[i], "taskfile": f"{GuideTask.EVENT}_{i+1}", "priority": 1}]}

      AutomatorRecorder.setbatch(f"batch_{GuideTask.DAILY}_{i+1}", batch_dict_daily)
      AutomatorRecorder.setbatch(f"batch_{GuideTask.QUEST}_{i+1}", batch_dict_quest)
      AutomatorRecorder.setbatch(f"batch_{GuideTask.EVENT}_{i+1}", batch_dict_event)

  else:

    batch_dict_daily = {"batch": [{"group": GuideGroup.MAIN, "taskfile": GuideTask.DAILY, "priority": 3}]}
    batch_dict_quest = {"batch": [{"group": GuideGroup.ALL, "taskfile": GuideTask.QUEST, "priority": 2}]}
    batch_dict_event = {"batch": [{"group": GuideGroup.ALL, "taskfile": GuideTask.EVENT, "priority": 1}]}

    AutomatorRecorder.setbatch(f"batch_{GuideTask.DAILY}_{GuideGroup.MAIN}", batch_dict_daily)
    AutomatorRecorder.setbatch(f"batch_{GuideTask.QUEST}_{GuideGroup.ALL}", batch_dict_quest)
    AutomatorRecorder.setbatch(f"batch_{GuideTask.EVENT}_{GuideGroup.ALL}", batch_dict_event)

    if group_mode == AccountGroupMode.MAIN_SUB_GROUP:
      batch_dict_daily_sub = {"batch": [{"group": GuideGroup.SUB, "taskfile": GuideTask.DAILY_SUB, "priority": 4}]}
      AutomatorRecorder.setbatch(f"batch_{GuideTask.DAILY}_{GuideGroup.SUB}", batch_dict_daily_sub)
      
  batch_dict_settings = {"batch": [{"group": GuideGroup.ALL, 
                                    "taskfile": GuideTask.SETTINGS, 
                                    "priority": 0}]}
  AutomatorRecorder.setbatch(f"batch_{GuideTask.SETTINGS}_{GuideGroup.ALL}", batch_dict_settings)

  # generate schedules

  schedule_dict_settings = [get_sub_schedule_tplt("schedule_settings", f"batch_{GuideTask.SETTINGS}_{GuideGroup.ALL}")]
  
  if is_multi_account and group_mode == AccountGroupMode.ONE_TO_ONE_GROUP:
    schedule_list_daily = []
    schedule_list_quest = []
    schedule_list_event = []
    
    for i in range(len(account_list)):
      schedule_list_daily.append(get_sub_schedule_tplt(f"schedule_daily_{i+1}", f"batch_{GuideTask.DAILY}_{i+1}"))
      schedule_list_quest.append(get_sub_schedule_tplt(f"schedule_quest_{i+1}", f"batch_{GuideTask.QUEST}_{i+1}"))
      schedule_list_event.append(get_sub_schedule_tplt(f"schedule_event_{i+1}", f"batch_{GuideTask.EVENT}_{i+1}"))
    
    AutomatorRecorder.setschedule("daily", {"schedules": schedule_list_daily})
    AutomatorRecorder.setschedule("quest", {"schedules": schedule_list_quest})
    AutomatorRecorder.setschedule("event", {"schedules": schedule_list_event})

  else:
    schedule_list_daily = [get_sub_schedule_tplt("schedule_daily", f"batch_{GuideTask.DAILY}_{GuideGroup.MAIN}")]
    schedule_list_quest = [get_sub_schedule_tplt("schedule_quest", f"batch_{GuideTask.QUEST}_{GuideGroup.ALL}")]
    schedule_list_event = [get_sub_schedule_tplt("schedule_event", f"batch_{GuideTask.EVENT}_{GuideGroup.ALL}")]
    
    if group_mode == AccountGroupMode.MAIN_SUB_GROUP:
      schedule_list_daily.append(get_sub_schedule_tplt("schedule_daily_sub", f"batch_{GuideTask.DAILY}_{GuideGroup.SUB}"))
    
    AutomatorRecorder.setschedule("daily", {"schedules": schedule_list_daily})
    AutomatorRecorder.setschedule("quest", {"schedules": schedule_list_quest})
    AutomatorRecorder.setschedule("event", {"schedules": schedule_list_event})

  
  AutomatorRecorder.setschedule("settings", {"schedules": schedule_dict_settings})
  if os.path.exists("bind_schedule.txt"):
    os.remove("bind_schedule.txt")
  print("配置生成完毕，请根据自身需要修改任务。\n如需对日常任务进行修改，请运行`python main_new.py`后，\nedit -> task -e daily")
  print("\n接下来你可以输入：\n（1）python main_new.py\n（2）bind settings\n（3）first\n正常情况下，脚本将对游戏内设置进行自动优化。")
  print("可绑定计划为：daily-清日常, quest-主线推图，event-活动推图，settings-优化设置。")
  '''

  is_run_at_once: Choice[int] = ListPrompt(
      "即将启动脚本，请在加载完毕后，输入first指令并回车，脚本将尝试对游戏内设置进行自动优化。是否同意？",
      choices=[
          Choice("同意", data=0),
          Choice("非常同意", data=1),
          Choice("我有意见！",data=2)
      ],
  ).prompt().data

  if is_run_at_once !=2:
    exec(open('main_new.py', encoding='utf-8').read())

  '''
