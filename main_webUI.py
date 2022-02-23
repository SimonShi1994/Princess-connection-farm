# -*- coding:utf-8 -*-
import random

import pywebio

from webui.pcr_component import ScopeName, ComponentBase, GetDatacenterTimeComponent
import pywebio.output as po
import pywebio.output as wo


class Tabs:
    def __init__(self):
        super().__init__()
        # tab的主域
        self.tabs_scopename = ScopeName('tabs')
        # tab注册表
        self.component_regs = {
            "a": {'title': 'Text', 'content': '内容a'},
            "b": {'title': 'Markdown', 'content': '内容b'},
        }

        # 已经加载上的tab
        self.now_use_tabs = [
            self.component_regs.get("a")
        ]

    def apply(self):
        layer = wo.put_column([
            self._tab()
        ])
        return layer

    def add_tab(self, component_regs_key: str):
        self.now_use_tabs.append(self.component_regs.get(component_regs_key))

    def del_tab(self, index: int):
        if len(self.now_use_tabs) == 1 or index > len(self.now_use_tabs) - 1:
            return False
        else:
            del self.now_use_tabs[index]
            return True

    def get_now_running_tab(self):
        return self.now_use_tabs, len(self.now_use_tabs)

    @staticmethod
    async def wait_change(*args) -> bool:
        # 无法堵塞！请注意
        result = await pywebio.pin.pin_wait_change(*args)
        if result:
            return True

    def _tab(self):
        # style('float:left;padding-right:0;padding-left:0;margin-right:0;margin-left:0') 左对齐
        # pin_wait_change建议在组件内使用
        # po.put_scope('tabs', content=po.put_tabs(self.now_use_tabs))
        # self.tabs_scopename.put_scope('tabs', content=po.put_tabs(self.now_use_tabs))

        logo_img = open('./webclient/static/favicon.ico', 'rb').read()
        tabs_main = self.tabs_scopename.add('tabs_main')  # tab的子域，上边栏
        with tabs_main.enter(clear=True):
            po.put_column([
                po.put_row([
                    po.put_image(logo_img, title='Princess-connection-farm', height='20%'),
                    po.put_text('Princess-connection-farm')  # 这个错位了，应该是bug，虽然能用css改，但是感觉不要紧
                ]),
                po.put_tabs(self.now_use_tabs).style('margin-top:0')
            ], size='53px')

        # tab的增删测试按钮，非正式代码
        with po.use_scope('tabs_messages'):
            A = 'tA' + str(random.randint(1, 9999))
            B = 'tA1' + str(random.randint(1, 9999))
            C = 'tA2' + str(random.randint(1, 9999))
            pywebio.pin.put_input(A)
            pywebio.pin.put_actions(B, buttons=[{
                "label": 'test',
                'value': 'add',
                'type': 'submit',
                "color": 'success'
            }])
            pywebio.pin.put_actions(C, buttons=[{
                "label": 'del',
                'value': 'del',
                'type': 'submit',
                "color": 'danger'
            }])
            changes = pywebio.pin.pin_wait_change(A, B, C)
            print(changes)
            print(pywebio.output.get_scope(-1))
            if changes.get('value') == 'add':
                self.add_tab('b')
                self.tabs_scopename.del_scope(tabs_main)  # 清空子域
            elif changes.get('value') == 'del':
                self.del_tab(-1)
                print("del")
                self.tabs_scopename.del_scope(tabs_main)  # 清空子域


if __name__ == "__main__":
    a = Tabs()
    while True:
        a.apply()
