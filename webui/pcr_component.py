# -*- coding:utf-8 -*-
from typing import Optional

import pywebio
from abc import abstractmethod, ABC
from pcr_api import PCRAPI, script_version
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
        if not hasattr(self, "on_apply"):
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

    def get_datacenter_time(self):
        return pywebio.output.put_text(PCRAPI.get_datacenter_time())

    def apply(self):
        layer = wo.put_column([
            self.get_datacenter_time()
        ])
        return layer


class GetGithubInfo(ComponentBase):

    def apply(self):
        layer = wo.put_column([
            wo.put_markdown(PCRAPI.get_github_info())
        ])
        return layer


class GetScriptVersion(ComponentBase):

    def apply(self):
        layer = wo.put_column([
            wo.put_text(script_version)
        ])
        return layer


class RunAdbComponent(ComponentBase):
    # TODO:交互组件
    def run_adb(self):
        _scope = self.scope.add("RunAdbComponent")
        PCRAPI.run_adb(_scope.get('cmd'))

    def adb_popup(self):
        _scope = self.scope.add("RunAdbComponent")
        cmd = wp.put_input(_scope + 'cmd', label='执行的adb命令')
        btn = wo.put_button("执行", onclick=self.run_adb)

        cmd_popup = wo.popup('执行adb命令', [
            wo.put_column([
                cmd,
                wo.put_row([btn, wo.put_buttons(['关闭窗口'], onclick=lambda _: wo.close_popup())])
            ])
        ])
        return cmd_popup

    def apply(self):
        return wo.put_buttons(['执行adb命令'], onclick=lambda _: self.adb_popup())


class RunInitComponent(ComponentBase):
    # TODO:交互组件
    @staticmethod
    def unbind_btn():
        return wo.put_button("初始化模拟器环境", onclick=lambda: PCRAPI.run_init(), color='danger')

    def apply(self):
        _scope = self.scope.add("RunInitComponent")
        layer = wo.put_column([
            self.unbind_btn()
        ])
        return layer


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
        _scope = self.scope.add("ReadUserComponent")
        pywebio.output.put_text(self.PCRAPI.read_user(_scope.get('username')))

    def apply(self):
        _scope = self.scope.add("ReadUserComponent")
        username = wp.put_input(_scope + 'username', label='输入要读取的密码的用户名')
        btn = wo.put_button("确定", onclick=self.put_input, color="success")
        layer = wo.put_column([
            wo.put_row([username, btn])
        ])
        return layer


class BindScheduleComponent(ComponentBase):
    # TODO:交互组件
    def put_input(self):
        _scope = self.scope.add("BindScheduleComponent")
        pywebio.output.put_text(self.PCRAPI.bind_schedule(_scope.get('name')))

    def apply(self):
        _scope = self.scope.add("BindScheduleComponent")
        name = wp.put_input(_scope + 'name', label='输入要绑定的计划名')
        btn = wo.put_button("确定", onclick=self.put_input, color="success")
        layer = wo.put_column([
            wo.put_row([name, btn])
        ])
        return layer


class UnbindScheduleComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        self.PCRAPI.unbind_schedule()

    def apply(self):
        _scope = self.scope.add("UnbindScheduleComponent")
        btn = wo.put_button("取消绑定当前的计划", onclick=self.put_button, color='warning')
        layer = wo.put_column([
            wo.put_row([btn])
        ])
        return layer


class FirstStartPcrComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        self.PCRAPI.start_pcr(1)

    def apply(self):
        _scope = self.scope.add("FirstStartPcrComponent")
        btn = wo.put_button("first", onclick=self.put_button, color='info')
        layer = wo.put_column([
            wo.put_row([btn])
        ])
        return layer


class ContinueStartPcrComponent(ComponentBase):
    def put_button(self):
        # TODO: 需要堵塞才能看到效果，主程序运行完成按钮事件销毁
        self.PCRAPI.start_pcr(2)
        # import time
        # time.sleep(100)

    def apply(self):
        _scope = self.scope.add("ContinueStartPcrComponent")
        btn = wo.put_button("continue", onclick=self.put_button, color='info')
        layer = wo.put_column([
            wo.put_row([btn])
        ])
        return layer


class NotThingsStartPcrComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        self.PCRAPI.start_pcr(0)

    def apply(self):
        _scope = self.scope.add("NotThingsStartPcrComponent")
        btn = wo.put_button("不使用schedule", onclick=self.put_button, color='info')
        layer = wo.put_column([
            wo.put_row([btn])
        ])
        return layer


class StopPcrComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        self.PCRAPI.stop_pcr()

    def apply(self):
        _scope = self.scope.add("StopPcrComponent")
        btn = wo.put_button("停止脚本", onclick=self.put_button, color='danger')
        layer = wo.put_column([
            wo.put_row([btn])
        ])
        return layer


class ScheduleClearAllErrorComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        self.PCRAPI.schedule_clear_error()

    def apply(self):
        _scope = self.scope.add("ScheduleClearAllErrorComponent")
        btn = wo.put_button("清除全部错误", onclick=self.put_button, color='danger')
        layer = wo.put_column([
            wo.put_row([btn])
        ])
        return layer


class ScheduleClearErrorComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        _scope = self.scope.add("ScheduleClearErrorComponent")
        self.PCRAPI.schedule_clear_error(_scope.get('name'))

    def apply(self):
        _scope = self.scope.add("ScheduleClearErrorComponent")
        name = wp.put_input(_scope + 'name', label="清除名称为name的subschedule的错误")
        btn = wo.put_button("确认", onclick=self.put_button, color='danger')
        layer = wo.put_column([
            wo.put_row([name, btn])
        ])
        return layer


class ScheduleFinishAllErrorComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        self.PCRAPI.schedule_finish()

    def apply(self):
        _scope = self.scope.add("ScheduleFinishAllErrorComponent")
        btn = wo.put_button("直接完成全部schedule。", onclick=self.put_button, color='success')
        layer = wo.put_column([
            wo.put_row([btn])
        ])
        return layer


class ScheduleFinishComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        _scope = self.scope.add("ScheduleFinishComponent")
        self.PCRAPI.schedule_finish(_scope.get('name'))

    def apply(self):
        _scope = self.scope.add("ScheduleFinishComponent")
        name = wp.put_input(_scope + 'name', label="将某一个子subschedule设为完成。")
        btn = wo.put_button("确认", onclick=self.put_button, color='success')
        layer = wo.put_column([
            wo.put_row([name, btn])
        ])
        return layer


class ScheduleRestartAllErrorComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        self.PCRAPI.schedule_restart()

    def apply(self):
        _scope = self.scope.add("ScheduleRestartAllErrorComponent")
        btn = wo.put_button("重置全部计划，！除了永久执行的计划！", onclick=self.put_button, color='danger')
        layer = wo.put_column([
            wo.put_row([btn])
        ])
        return layer


class ScheduleRestartComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        _scope = self.scope.add("ScheduleRestartComponent")
        self.PCRAPI.schedule_restart(_scope.get('name'))

    def apply(self):
        _scope = self.scope.add("ScheduleRestartComponent")
        name = wp.put_input(_scope + 'name', label="重新开始某一个subschedule。")
        btn = wo.put_button("确认", onclick=self.put_button, color='warning')
        layer = wo.put_column([
            wo.put_row([name, btn])
        ])
        return layer


class DeviceReconnectComponent(ComponentBase):
    # TODO:交互组件
    def put_button(self):
        self.PCRAPI.device_reconnect()

    def apply(self):
        _scope = self.scope.add("DeviceReconnectComponent")
        btn = wo.put_button("重新搜索设备并连接", onclick=self.put_button, color='info')
        layer = wo.put_column([
            wo.put_row([btn])
        ])
        return layer


class AddBatchToPcrComponent(ComponentBase):
    # TODO:交互组件

    def add_batch_to_pcr_component(self):
        _scope = self.scope.add("AddBatchToPcrComponent")
        self.PCRAPI.add_batch_to_pcr(_scope.get('dict'), _scope.get('checkbox'))

    def apply(self):
        _scope = self.scope.add("AddBatchToPcrComponent")
        # data = pywebio.input.input_group("中途向任务队列中增加一条batch", [
        #     pywebio.input.input('合法的batch字典', name='batch'),
        #     pywebio.input.checkbox(options=['以continue模式运行该batch'], name='continue_')
        # ])

        title = wo.put_text("中途向任务队列中增加一条batch")
        _dict = wp.put_input(_scope + 'dict', label='合法的batch字典')
        _checkbox = wp.put_checkbox(scope=_scope + 'checkbox', options=['以continue模式运行该batch'], name='continue_')
        ok_btn = wo.put_button("确认", onclick=self.add_batch_to_pcr_component, color='primary')

        layer = wo.put_column([
            title,
            _dict,
            _checkbox,
            ok_btn
        ], size='25px 70px 25px 20px')
        return layer
        # print(data['batch'], data['continue_'])
        # self.pywebio_output.put_text(self.PCRAPI.add_batch_to_pcr(data['batch'], data['continue_']))


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


if __name__ == "__main__":
    RunAdbComponent().apply()
    import time

    time.sleep(90)
