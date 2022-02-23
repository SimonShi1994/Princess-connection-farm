# -*- coding:utf-8 -*-
import asyncio
import time
from typing import Optional, Callable

import pywebio
from abc import abstractmethod, ABC
from pcr_api import PCRAPI
import pywebio.output as wo
import pywebio.pin as wp


class ScopeName(str):
    def __new__(cls, name):
        return str.__new__(ScopeName, name)  # noqa

    def enter(self, clear=False):
        parent = self

        class ScopeName_:
            def __enter__(self):
                if parent == "__root__":
                    return ScopeName(pywebio.output.get_scope())  # Current Root
                else:
                    pywebio.output.use_scope(parent, clear=clear).__enter__()
                    return parent

            def __exit__(self, *args, **kwargs):
                if parent != "__root__":
                    pywebio.output.use_scope(parent, clear=clear).__exit__(*args, **kwargs)

        return ScopeName_()

    def add(self, scope):
        if self == "__root__":
            return ScopeName(scope)
        else:
            return ScopeName(str(self) + "_" + scope)

    def put_scope(self, name: str, content=[], position=pywebio.output.OutputPosition.BOTTOM):
        return pywebio.output.put_scope(self + name, content, scope=self, position=position)

    def del_scope(self, name=None):
        return pywebio.output.remove(self + name)

    def get(self, name: str, strict=True):
        return pywebio.pin.get_pin_value(self + name, strict)

    def __add__(self, other):
        return ScopeName(self.add(other))


class ComponentBase(ABC):
    def __init__(self, scope=None, api: Optional[PCRAPI] = None):
        if scope is None:
            scope = "__root__"
        self.scope = ScopeName(scope)
        self.PCRAPI = api
        self.used_scope = {}
        self.on_apply_queue = []  # 记录on_apply的调用队列
        """
        on_apply:
        调用__call__时，在执行完全部apply后执行的内容。
        调用add_component时，子元件的on_apply将被暂存到父元件的on_apply_queue队列。
        执行时，子元件的on_apply先执行，父元件的on_apply后执行
        ！在全部渲染完毕后被调用！
        """
        if not hasattr(self,"on_apply"):
            self.on_apply = None

    @abstractmethod
    def apply(self):
        """
        元件实现的主要部分
        但如果你想要触发on_apply事件，你得用__call__！
        __call__没有返回值，会执行最顶层的apply后，进一步按照先子再父的顺序执行on_apply！
        """
        pass

    def add_component(self, component: "ComponentBase", name=None):
        component.PCRAPI = self.PCRAPI
        if component.on_apply is not None:
            self.on_apply_queue.append(component.on_apply)  # 添加子元件的on_apply到调用队列
        self.on_apply_queue.extend(component.on_apply_queue)  # 合并调用队列到上级
        component.on_apply_queue = []
        if name is None:
            component.scope = self.scope
            out = component.apply()
            return out
        else:
            component.scope = self.scope + name
            self.used_scope.setdefault(name, self.scope + name)
            out = component.apply()
            return out

    def get_component_scope(self, name):
        return self.used_scope.get(name)

    def __call__(self):
        """
        最顶层的元件使用__call__
        apply只是渲染，__call__是渲染并执行所有的on_apply事件函数！
        __call__没有返回值！
        """
        self.apply()
        for func in self.on_apply_queue:
            func()
        self.on_apply_queue = []

class GetDatacenterTimeComponent(ComponentBase):

    @staticmethod
    def get_datacenter_time():
        return pywebio.output.put_text(PCRAPI.get_datacenter_time())

    def apply(self):
        layer = wo.put_column([
            self.get_datacenter_time()
        ])
        return layer


class RunAdbComponent(ComponentBase):
    # TODO:交互组件
    @staticmethod
    def run_adb(cmd):
        PCRAPI.run_adb(cmd)

    def apply(self):
        cmd = pywebio.input.input('执行的命令')
        self.run_adb(cmd)
        layer = wo.put_column([
            cmd
        ])
        return layer


class RunInitComponent(ComponentBase):
    # TODO:交互组件
    @staticmethod
    def unbind_btn():
        pywebio.output.put_button("取消绑定当前的计划", onclick=lambda: PCRAPI.run_init(), color='info')

    def apply(self):
        pass


class GetLastScheduleComponent(ComponentBase):

    @staticmethod
    def put_text():
        pywebio.output.put_text(PCRAPI.get_last_schedule())

    def apply(self):
        layer = wo.put_column([
            self.put_text()
        ])
        return layer


class GetDeviceStatusComponent(ComponentBase):

    def put_text(self):
        pywebio.output.put_text(self.PCRAPI.get_device_status())

    def apply(self):
        layer = wo.put_column([
            self.put_text()
        ])
        return layer


class GetTaskQueueComponent(ComponentBase):

    def put_text(self):
        pywebio.output.put_text(self.PCRAPI.get_task_queue())

    def apply(self):
        layer = wo.put_column([
            self.put_text()
        ])
        return layer


class GetScheduleStatusComponent(ComponentBase):

    def put_text(self):
        pywebio.output.put_text(self.PCRAPI.get_schedule_status())

    def apply(self):
        layer = wo.put_column([
            self.put_text()
        ])
        return layer


class ReadUserComponent(ComponentBase):
    # TODO:交互组件
    def put_input(self):
        username = pywebio.input.input('输入要读取的密码的用户名')
        pywebio.output.put_text(self.PCRAPI.read_user(username))

    def apply(self):
        pass


class BindScheduleComponent(ComponentBase):
    # TODO:交互组件
    def put_input(self):
        name = pywebio.input.input('输入要绑定的计划名')
        pywebio.output.put_text(self.PCRAPI.bind_schedule(name))

    def apply(self):
        pass


class UnbindScheduleComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        pywebio.output.put_button("取消绑定当前的计划", onclick=lambda: self.PCRAPI.unbind_schedule(), color='warning')

    def apply(self):
        pass


class FirstStartPcrComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        pywebio.output.put_button("first", onclick=lambda: self.PCRAPI.start_pcr(1), color='info')

    def apply(self):
        pass


class ContinueStartPcrComponent(ComponentBase):
    def put_button(self):
        # TODO: 需要堵塞才能看到效果，主程序运行完成按钮事件销毁
        pywebio.output.put_button("continue", onclick=lambda: self.PCRAPI.start_pcr(2), color='info')
        import time
        time.sleep(100)

    def apply(self):
        pass


class NotThingsStartPcrComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        pywebio.output.put_button("不使用schedule", onclick=lambda: self.PCRAPI.start_pcr(0), color='info')

    def apply(self):
        pass


class StopPcrComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        pywebio.output.put_button("停止脚本", onclick=lambda: self.PCRAPI.stop_pcr(), color='danger')

    def apply(self):
        pass


class ScheduleClearAllErrorComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        pywebio.output.put_button("清除全部错误", onclick=lambda: self.PCRAPI.schedule_clear_error(), color='danger')

    def apply(self):
        pass


class ScheduleClearErrorComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        name = pywebio.input.input('清除名称为name的subschedule的错误')
        self.PCRAPI.schedule_clear_error(name)

    def apply(self):
        pass


class ScheduleFinishAllErrorComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        pywebio.output.put_button("直接完成全部schedule。", onclick=lambda: self.PCRAPI.schedule_finish(), color='danger')

    def apply(self):
        pass


class ScheduleFinishComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        name = pywebio.input.input('将某一个子subschedule设为完成。')
        self.PCRAPI.schedule_finish(name)

    def apply(self):
        pass


class ScheduleRestartAllErrorComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        pywebio.output.put_button("重置全部计划，！除了永久执行的计划！", onclick=lambda: self.PCRAPI.schedule_restart(),
                                  color='danger')

    def apply(self):
        pass


class ScheduleRestartComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        name = pywebio.input.input('重新开始某一个subschedule')
        self.PCRAPI.schedule_restart(name)

    def apply(self):
        pass


class DeviceReconnectComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        pywebio.output.put_button("重新搜索设备并连接", onclick=lambda: self.PCRAPI.device_reconnect(), color='info')

    def apply(self):
        pass


class AddBatchToPcrComponent(ComponentBase):
    # TODO:交互组件
    @staticmethod
    async def add_batch_to_pcr_component():
        data = await pywebio.input.input_group("中途向任务队列中增加一条batch", [
            pywebio.input.input('合法的batch字典', name='batch'),
            pywebio.input.checkbox(options=['以continue模式运行该batch'], name='continue_')
        ])
        print(data['batch'], data['continue_'])
        # self.pywebio_output.put_text(self.PCRAPI.add_batch_to_pcr(data['batch'], data['continue_']))

    def apply(self):
        self.add_batch_to_pcr_component()


class AddTaskToPcrComponent(ComponentBase):
    # TODO:交互组件
    @staticmethod
    async def add_task_to_pcr_component():
        data = await pywebio.input.input_group("中途向任务队列中增加一个谁做谁", [
            pywebio.input.input('用户列表，接受新任务的对象。', name='accs'),
            pywebio.input.input('显示在任务队列中的任务名称', name='taskname'),
            pywebio.input.input('合法的task字典，若不指定，则自动在tasks目录下找taskname的任务文件载入。', name='task'),
            pywebio.input.input('任务优先级', name='priority'),
            pywebio.input.checkbox(options=['以continue模式运行该任务', '随机accs的顺序'], name='_checkbox')
        ])
        print(data['accs'], data['_checkbox'])
        # self.pywebio_output.put_text(self.PCRAPI.add_task_to_pcr(data['accs'], data['_checkbox']))

    def apply(self):
        self.add_task_to_pcr_component()


class WriteUserComponent(ComponentBase):
    # TODO:交互组件
    def input_group(self):
        data = pywebio.input.input_group("username and userdict", [
            pywebio.input.input('输入要写入的密码的用户名', name='username'),
            pywebio.input.textarea('输入要写入的dict', name='userdict')
        ])
        print(data['username'], data['userdict'])
        # self.pywebio_output.put_text(self.PCRAPI.write_user(data['username'], data['userdict']))

    def apply(self):
        pass


# class PCRComponent():
#     def __init__(self):
#         super().__init__()
#         self.PCRAPI = PCRAPI()
#         self.pywebio = pywebio
#         self.pywebio_output = pywebio.output
#         self.pywebio_input = pywebio.input
#         self.pywebio_pin = pywebio.pin
#
#         # 测试代码
#         # self.PCRAPI.start_pcr(0)
#
#     def get_datacenter_time_component(self):
#         self.pywebio_output.put_text(PCRAPI.get_datacenter_time())
#
#     def run_adb_component(self):
#         cmd = self.pywebio_input.input('执行的命令')
#         PCRAPI.run_adb(cmd)
#
#     def run_init_component(self):
#         self.pywebio_output.put_button("取消绑定当前的计划", onclick=lambda: PCRAPI.run_init(), color='info')
#
#     def get_last_schedule_component(self):
#         self.pywebio_output.put_text(PCRAPI.get_last_schedule())
#
#     def get_device_status_component(self):
#         self.pywebio_output.put_text(self.PCRAPI.get_device_status())
#
#     def get_task_queue_component(self):
#         self.pywebio_output.put_text(self.PCRAPI.get_task_queue())
#
#     def get_schedule_status_component(self):
#         self.pywebio_output.put_text(self.PCRAPI.get_schedule_status())
#
#     def read_user_component(self):
#         username = self.pywebio_input.input('输入要读取的密码的用户名')
#         self.pywebio_output.put_text(self.PCRAPI.read_user(username))
#
#     def bind_schedule_component(self):
#         name = self.pywebio_input.input('输入要绑定的计划名')
#         self.pywebio_output.put_text(self.PCRAPI.bind_schedule(name))
#
#     def unbind_schedule_component(self):
#         self.pywebio_output.put_button("取消绑定当前的计划", onclick=lambda: self.PCRAPI.unbind_schedule(), color='warning')
#
#     def first_start_pcr_component(self):
#         self.pywebio_output.put_button("first", onclick=lambda: self.PCRAPI.start_pcr(1), color='info')
#
#     def continue_start_pcr_component(self):
#         # TODO: 需要堵塞才能看到效果，主程序运行完成按钮事件销毁
#         self.pywebio_output.put_button("continue", onclick=lambda: self.PCRAPI.start_pcr(2), color='info')
#         import time
#         time.sleep(100)
#
#     def not_things_start_pcr_component(self):
#         self.pywebio_output.put_button("不使用schedule", onclick=lambda: self.PCRAPI.start_pcr(0), color='info')
#
#     def stop_pcr_component(self):
#         self.pywebio_output.put_button("停止脚本", onclick=lambda: self.PCRAPI.stop_pcr(), color='danger')
#
#     def schedule_clear_all_error_component(self):
#         self.pywebio_output.put_button("清除全部错误", onclick=lambda: self.PCRAPI.schedule_clear_error(), color='danger')
#
#     def schedule_clear_error_component(self):
#         name = self.pywebio_input.input('清除名称为name的subschedule的错误')
#         self.PCRAPI.schedule_clear_error(name)
#
#     def schedule_finish_all_error_component(self):
#         self.pywebio_output.put_button("直接完成全部schedule。", onclick=lambda: self.PCRAPI.schedule_finish(), color='danger')
#
#     def schedule_finish_component(self):
#         name = self.pywebio_input.input('将某一个子subschedule设为完成。')
#         self.PCRAPI.schedule_finish(name)
#
#     def schedule_restart_all_error_component(self):
#         self.pywebio_output.put_button("重置全部计划，！除了永久执行的计划！", onclick=lambda: self.PCRAPI.schedule_restart(),
#                                        color='danger')
#
#     def schedule_restart_component(self):
#         name = self.pywebio_input.input('重新开始某一个subschedule')
#         self.PCRAPI.schedule_restart(name)
#
#     def device_reconnect_component(self):
#         self.pywebio_output.put_button("重新搜索设备并连接", onclick=lambda: self.PCRAPI.device_reconnect(), color='info')
#
#     async def add_batch_to_pcr_component(self):
#         data = await self.pywebio_input.input_group("中途向任务队列中增加一条batch", [
#             self.pywebio_input.input('合法的batch字典', name='batch'),
#             self.pywebio_input.checkbox(options=['以continue模式运行该batch'], name='continue_')
#         ])
#         print(data['batch'], data['continue_'])
#         # self.pywebio_output.put_text(self.PCRAPI.add_batch_to_pcr(data['batch'], data['continue_']))
#
#     async def add_task_to_pcr_component(self):
#         data = await self.pywebio_input.input_group("中途向任务队列中增加一个谁做谁", [
#             self.pywebio_input.input('用户列表，接受新任务的对象。', name='accs'),
#             self.pywebio_input.input('显示在任务队列中的任务名称', name='taskname'),
#             self.pywebio_input.input('合法的task字典，若不指定，则自动在tasks目录下找taskname的任务文件载入。', name='task'),
#             self.pywebio_input.input('任务优先级', name='priority'),
#             self.pywebio_input.checkbox(options=['以continue模式运行该任务', '随机accs的顺序'], name='_checkbox')
#         ])
#         print(data['accs'], data['_checkbox'])
#         # self.pywebio_output.put_text(self.PCRAPI.add_task_to_pcr(data['accs'], data['_checkbox']))
#
#     def write_user_component(self):
#         data = self.pywebio_input.input_group("username and userdict", [
#             self.pywebio_input.input('输入要写入的密码的用户名', name='username'),
#             self.pywebio_input.textarea('输入要写入的dict', name='userdict')
#         ])
#         print(data['username'], data['userdict'])
#         # self.pywebio_output.put_text(self.PCRAPI.write_user(data['username'], data['userdict']))
#
#     def tabs_demo(self):
#         self.pywebio_output.put_tabs([
#             {'title': 'Text', 'content': self.pywebio_output.put_scope('ta', content=['aaa1'])},
#             {'title': 'Markdown', 'content': self.pywebio_output.put_scope('tb', content=['bbb'])},
#         ])
#         self.pywebio.pin.put_input('tA', scope='ta')
#         self.pywebio.pin.put_input('tB', scope='tb')
#         self.pywebio.pin.put_actions('tA1', buttons=[{
#             "label": 'test',
#             'value': 'save',
#             'type': 'submit',
#             "color": 'danger'
#         }], scope='ta')
#         while True:
#             changed = self.pywebio.pin.pin_wait_change('tA', 'tB', 'tA1')
#             with self.pywebio.output.use_scope('ta', clear=False):
#                 self.pywebio.output.put_code(changed)

class MainApp(ComponentBase):

    def apply(self):
        pass


if __name__ == "__main__":
    D = ComponentBase()
    D.MainApp()
