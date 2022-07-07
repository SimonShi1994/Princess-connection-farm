# -*- coding:utf-8 -*-
import asyncio
import time

import pywebio
from pcr_api import PCRAPI


class PCRComponent:
    def __init__(self):
        self.PCRAPI = PCRAPI()
        self.pywebio = pywebio
        self.pywebio_output = pywebio.output
        self.pywebio_input = pywebio.input
        self.pywebio_pin = pywebio.pin

        # 测试代码
        # self.PCRAPI.start_pcr(0)

    def get_datacenter_time_component(self):
        self.pywebio_output.put_text(PCRAPI.get_datacenter_time())

    def run_adb_component(self):
        cmd = self.pywebio_input.input('执行的命令')
        PCRAPI.run_adb(cmd)

    def run_init_component(self):
        self.pywebio_output.put_button("取消绑定当前的计划", onclick=lambda: PCRAPI.run_init(), color='info')

    def get_last_schedule_component(self):
        self.pywebio_output.put_text(PCRAPI.get_last_schedule())

    def get_device_status_component(self):
        self.pywebio_output.put_text(self.PCRAPI.get_device_status())

    def get_task_queue_component(self):
        self.pywebio_output.put_text(self.PCRAPI.get_task_queue())

    def get_schedule_status_component(self):
        self.pywebio_output.put_text(self.PCRAPI.get_schedule_status())

    def get_task_queue_component(self):
        self.pywebio_output.put_text(self.PCRAPI.get_task_queue())

    def get_schedule_status_component(self):
        self.pywebio_output.put_text(self.PCRAPI.get_schedule_status())

    def read_user_component(self):
        username = self.pywebio_input.input('输入要读取的密码的用户名')
        self.pywebio_output.put_text(self.PCRAPI.read_user(username))

    def bind_schedule_component(self):
        name = self.pywebio_input.input('输入要绑定的计划名')
        self.pywebio_output.put_text(self.PCRAPI.bind_schedule(name))

    def unbind_schedule_component(self):
        self.pywebio_output.put_button("取消绑定当前的计划", onclick=lambda: self.PCRAPI.unbind_schedule(), color='warning')

    def first_start_pcr_component(self):
        self.pywebio_output.put_button("first", onclick=lambda: self.PCRAPI.start_pcr(1), color='info')

    def continue_start_pcr_component(self):
        # TODO: 需要堵塞才能看到效果，主程序运行完成按钮事件销毁
        self.pywebio_output.put_button("continue", onclick=lambda: self.PCRAPI.start_pcr(2), color='info')
        import time
        time.sleep(100)

    def not_things_start_pcr_component(self):
        self.pywebio_output.put_button("不使用schedule", onclick=lambda: self.PCRAPI.start_pcr(0), color='info')

    def stop_pcr_component(self):
        self.pywebio_output.put_button("停止脚本", onclick=lambda: self.PCRAPI.stop_pcr(), color='danger')

    def schedule_clear_all_error_component(self):
        self.pywebio_output.put_button("清除全部错误", onclick=lambda: self.PCRAPI.schedule_clear_error(), color='danger')

    def schedule_clear_error_component(self):
        name = self.pywebio_input.input('清除名称为name的subschedule的错误')
        self.PCRAPI.schedule_clear_error(name)

    def schedule_finish_all_error_component(self):
        self.pywebio_output.put_button("直接完成全部schedule。", onclick=lambda: self.PCRAPI.schedule_finish(), color='danger')

    def schedule_finish_component(self):
        name = self.pywebio_input.input('将某一个子subschedule设为完成。')
        self.PCRAPI.schedule_finish(name)

    def schedule_restart_all_error_component(self):
        self.pywebio_output.put_button("重置全部计划，！除了永久执行的计划！", onclick=lambda: self.PCRAPI.schedule_restart(),
                                       color='danger')

    def schedule_restart_component(self):
        name = self.pywebio_input.input('重新开始某一个subschedule')
        self.PCRAPI.schedule_restart(name)

    def device_reconnect_component(self):
        self.pywebio_output.put_button("重新搜索设备并连接", onclick=lambda: self.PCRAPI.device_reconnect(), color='info')

    async def add_batch_to_pcr_component(self):
        data = await self.pywebio_input.input_group("中途向任务队列中增加一条batch", [
            self.pywebio_input.input('合法的batch字典', name='batch'),
            self.pywebio_input.checkbox(options=['以continue模式运行该batch'], name='continue_')
        ])
        print(data['batch'], data['continue_'])
        # self.pywebio_output.put_text(self.PCRAPI.add_batch_to_pcr(data['batch'], data['continue_']))

    async def add_task_to_pcr_component(self):
        data = await self.pywebio_input.input_group("中途向任务队列中增加一个谁做谁", [
            self.pywebio_input.input('用户列表，接受新任务的对象。', name='accs'),
            self.pywebio_input.input('显示在任务队列中的任务名称', name='taskname'),
            self.pywebio_input.input('合法的task字典，若不指定，则自动在tasks目录下找taskname的任务文件载入。', name='task'),
            self.pywebio_input.input('任务优先级', name='priority'),
            self.pywebio_input.checkbox(options=['以continue模式运行该任务', '随机accs的顺序'], name='_checkbox')
        ])
        print(data['accs'], data['_checkbox'])
        # self.pywebio_output.put_text(self.PCRAPI.add_task_to_pcr(data['accs'], data['_checkbox']))

    def write_user_component(self):
        data = self.pywebio_input.input_group("username and userdict", [
            self.pywebio_input.input('输入要写入的密码的用户名', name='username'),
            self.pywebio_input.textarea('输入要写入的dict', name='userdict')
        ])
        print(data['username'], data['userdict'])
        # self.pywebio_output.put_text(self.PCRAPI.write_user(data['username'], data['userdict']))

    def tabs_demo(self):
        self.pywebio_output.put_tabs([
            {'title': 'Text', 'content': self.pywebio_output.put_scope('ta', content=['aaa1'])},
            {'title': 'Markdown', 'content': self.pywebio_output.put_scope('tb', content=['bbb'])},
        ])
        self.pywebio.pin.put_input('tA', scope='ta')
        self.pywebio.pin.put_input('tB', scope='tb')
        self.pywebio.pin.put_actions('tA1', buttons=[{
            "label": 'test',
            'value': 'save',
            'type': 'submit',
            "color": 'danger'
        }], scope='ta')
        while True:
            changed = self.pywebio.pin.pin_wait_change('tA', 'tB', 'tA1')
            with self.pywebio.output.use_scope('ta', clear=False):
                self.pywebio.output.put_code(changed)


if __name__ == "__main__":
    D = PCRComponent()
    D.tabs_demo()
