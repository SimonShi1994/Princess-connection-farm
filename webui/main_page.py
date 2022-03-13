# -*- coding:utf-8 -*-
from pprint import pformat

import pywebio

from view import *
from webui.advanced_tab import AdvancedTab

import pywebio.output as wo
import pywebio.pin as wp
import pywebio.session as ws
import pywebio.input as wi

html = """
<style>
.container, .container-fluid, .container-lg, .container-md, .container-sm, .container-xl {
    width: 100%;
    padding-right: 15px;
    padding-left: 15px;
    margin-right: auto;
    margin-left: auto;
}
.container {
    margin-top: 0;
    max-width: 100%;
}
.webio-tabs {
    margin-top: 0;
    margin-bottom: 1rem;
    border: 1px solid #e9ecef;
    border-radius: 0.25rem;
    overflow: hidden;
    display: flex;
    flex-wrap: wrap;
    align-content: flex-start;
}

.navbar {
    position: relative;
    display: -ms-flexbox;
    display: flex;
    -ms-flex-wrap: wrap;
    flex-wrap: wrap;
    -ms-flex-align: center;
    align-items: center;
    -ms-flex-pack: justify;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    height: 70px;
}
</style>
"""

logo_html = """
<nav class="navbar navbar-light bg-light">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">
      <img src="https://raw.githubusercontent.com/SimonShi1994/Princess-connection-farm/master/webclient/static/favicon.ico" alt="" height="40&" class="d-inline-block align-text-top">
      Princess-connection-farm
    </a>
  </div>
</nav>
"""

class PageBase(ComponentBase):
    def __init__(self):
        super().__init__()
        self.__tabs_info__ = {}


class TestPage(PageBase):
    def del_me(self):
        ti = self.__tabs_info__
        ti['tab'].del_tab(ti['index'])

    def apply(self):
        S = self.scope
        IN = wp.put_input(S + "IN", label="Test", value=f"My Name:{S + 'IN'}")
        ti = self.__tabs_info__
        del_btn = wo.put_button("关闭", onclick=self.del_me)
        return wo.put_column([
            wo.put_text(f"PAGE SCOPE: {self.scope}"),
            wo.put_text(f"PAGE INDEX: {ti['index']}"),
            IN,
            del_btn
        ])


class MainTabPage(PageBase):
    def __init__(self, bind_tab: AdvancedTab):
        super().__init__()
        self.bind_tab = bind_tab

    def test(self):
        S = self.scope
        self.bind_tab.add_tab('title', S + 'scope', content=TestPage(), enable_close=True,
                              show_tab=True)

    def apply(self):
        return wo.put_row([
            wo.put_column([
                self.add_component(MainPage(), "MainPage")
            ])
        ])


class MainAPP(ComponentBase):
    def __init__(self):
        super().__init__()
        self.TAB = AdvancedTab()
        self.MainPage = MainTabPage(self.TAB)  # 先绑定
        self.TAB.init([AdvancedTab.make_init_content("MAIN", "main", self.MainPage, False, True)])  # 重新init实现双向绑定

    def apply(self):
        # btn = wo.put_button("确定", self.MainPage.test)
        out = wo.put_column([
            wo.put_html(logo_html),
            wo.put_row([
                wo.put_html(html),
                wo.put_collapse('Large text', 'Awesome PyWebIO! ' * 30), None,
                self.add_component(self.TAB, name="TAB"),
                # btn
            ], size='20% 5px'),
        ], size='70px')
        return out


if __name__ == "__main__":
    app = MainAPP()
    pywebio.start_server(app, 10234)
    # from pywebio.session.threadbased import ScriptModeSession
