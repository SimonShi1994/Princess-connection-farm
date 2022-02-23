# -*- coding:utf-8 -*-
import random

import pywebio

from webui.pcr_component import ScopeName, ComponentBase, GetDatacenterTimeComponent
import pywebio.output as po
import pywebio.output as wo


class Tabs(ComponentBase):
    def __init__(self):
        super().__init__()
        self.tabs_scopename = ScopeName('tabs')
        self.component_regs = {
            "a": {'title': 'Text', 'content':
                self.tabs_scopename.put_scope('messages',
                                              self.add_component(GetDatacenterTimeComponent(), "messages"))},
            "b": {'title': 'Markdown', 'content': self.add_component(GetDatacenterTimeComponent(), "messages")},
        }

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
        # pin_wait_change建议在组件内使用
        # po.put_scope('tabs', content=po.put_tabs(self.now_use_tabs))
        # self.tabs_scopename.put_scope('tabs', content=po.put_tabs(self.now_use_tabs))
        tabs_main = self.tabs_scopename.add('tabs_main')
        while True:
            with self.tabs_scopename.enter(tabs_main):
                po.put_tabs(self.now_use_tabs)
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
                if changes.get('value') == 'add':
                    self.add_tab('b')
                    self.tabs_scopename.del_scope(tabs_main)
                elif changes.get('value') == 'del':
                    self.del_tab(-1)
                    print("del")
                    self.tabs_scopename.del_scope(tabs_main)

    def _backer(self):
        # 备份的demo代码
        wo.put_column([
            ScopeName('tabs').put_scope('tabs', content=po.put_tabs(self.now_use_tabs))
        ])
        with self.scope.add('messages').enter():
            pywebio.pin.put_input('tA'),
            pywebio.pin.put_actions('tA1', buttons=[{
                "label": 'test',
                'value': 'save',
                'type': 'submit',
                "color": 'danger'
            }])
            changed = pywebio.pin.pin_wait_change('tA1')
            po.put_code(changed)
            if not self.component_regs.get('b') in self.now_use_tabs:
                self.now_use_tabs.append(self.component_regs.get('b'))
            po.remove("tabs")

    def tabs_demo(self):
        # 备份的demo代码
        dict_a = {"a": {'title': 'Text', 'content': po.put_scope('neirong', content=['aaa1'])},
                  "b": {'title': 'Markdown', 'content': ScopeName('neirong').put_scope('neirong', content=['bbb'])}, }
        list_a = [
            dict_a.get("a")
        ]
        while True:
            po.put_scope('tabs', content=po.put_tabs(list_a))
            with po.use_scope('neirong', clear=False):
                pywebio.pin.put_input('tA', scope='neirong'),
                pywebio.pin.put_actions('tA1', buttons=[{
                    "label": 'test',
                    'value': 'save',
                    'type': 'submit',
                    "color": 'danger'
                }], scope='neirong')
                changed = pywebio.pin.pin_wait_change('tA', 'tB', 'tA1')
                po.put_code(changed)
                list_a.append(dict_a.get('b'))
                po.remove("tabs")


if __name__ == "__main__":
    a = Tabs()
    a.apply()
