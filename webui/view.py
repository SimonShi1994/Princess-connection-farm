# -*- coding:utf-8 -*-
import time

import pywebio.output as wo
import pywebio.pin as wp

from pcr_component import *


class MainPage(ComponentBase):
    def __init__(self):
        super(MainPage, self).__init__()

    def _init(self):
        pass

    def apply(self):
        _scope = self.scope.add("MainPage")
        tpl = '''
                <div class="border shadow p-3 mb-5 bg-white rounded">
            <div class="alert alert-primary" role="alert">
                {{#git_info}}
                    {{& pywebio_output_parse}}
                {{/git_info}}
            </div>
    
            <div class="alert alert-secondary" role="alert">
                脚本当前所在版本为：
                {{#script_version}}
                    {{& pywebio_output_parse}}
                {{/script_version}}
            </div>
    '''

        layer = wo.put_widget(tpl, {
            "git_info": [self.add_component(GetGithubInfo(), "GetGithubInfo")],
            "script_version": [self.add_component(GetScriptVersion(), "GetScriptVersion")],
            "title": [wo.put_text("脚本控制区")],
            "contents": [
                wo.put_row([
                    wo.put_column([

                    ])
                ])
            ]
        })

        return layer


if __name__ == "__main__":
    MainPage().apply()
    time.sleep(90)
