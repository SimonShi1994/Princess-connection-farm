import pywebio.input as wi
from collections import OrderedDict
from pprint import pformat
import pywebio.output as wo
import pywebio.pin as wp
import pywebio.session as ws
import pywebio

from pcr_component import ComponentBase
from random import sample
from typing import Optional
from string import ascii_letters, digits

html = """
<button type="button" class="btn btn-primary" onclick="myFunction()"> 点我！ </button>
<button type="button" class="close" aria-label="Close"><span aria-hidden="true">&times;</span></button>
<script>
function myFunction(){
    alert("Hello World!");
}
</script>
"""


def TABS_TPL(tabs_id: str):
    return """
<div class="webio-tabs" id="__TABS_ID__">
{{{TEMPLATE_SCRIPT}}}
<script>
{{{CLOSE_SCRIPT}}}
{{{ADD_SCRIPT}}}
{{{CURRENT_SCRIPT}}}
{{{SHOWTAB_SCRIPT}}}
</script>
</div>""".replace("__TABS_ID__", tabs_id)


def _TEMPLATE_SCRIPT(tabs_id):
    # index, title, close_btn, scope_name
    return """
<script id="Template__TABS_ID__" type="x-tmpl-mustache">
<input type="radio" class="toggle" name="__TABS_ID__" id="__TABS_ID__{{index}}" myindex="{{index}}">
<label for="__TABS_ID__{{index}}">
    <p>{{title}}
    {{#close_btn}}<button type="button" class="close" aria-label="Close" onclick="WebIO.pushData('','{{CALLBACK_ID}}')">
    <span aria-hidden="true">&times;</span></button>{{/close_btn}}
</p>
</label>
<div class="webio-tabs-content">
    <div id="pywebio-scope-{{scope_name}}"></div>
</div>
</script>
<style>
</style>
""".replace("__TABS_ID__", tabs_id)


def _CLOSE_SCRIPT(tabs_id):
    return """
function Close___TABS_ID__(pg){
    var option_node_name = "#__TABS_ID__"+String(pg);
    var option_node = $(option_node_name)
    if (option_node.length==0){
        alert("Can not find Option "+String(pg)+" !");
    }else{
        option_node.next().next().remove();
        option_node.next().remove();
        option_node.remove();
    }
}
""".replace("__TABS_ID__", tabs_id)


def _CURRENT_SCRIPT(tabs_id):
    return """
function Current___TABS_ID__(){
    var input_list = $("#__TABS_ID__").children().filter("input")
    for (var i=0;i<input_list.length;i++){
        if (input_list[i].checked){
            return input_list[i].getAttribute('myindex');
        }
    }
    return "-1";
}
""".replace("__TABS_ID__", tabs_id)


def _SHOWTAB_SCRIPT(tabs_id):
    return """
function Show___TABS_ID__(pg){
    var input_list = $("#__TABS_ID__").children().filter("input")
    for (var i=0;i<input_list.length;i++){
        if (input_list[i].getAttribute('myindex')==String(pg)){
            input_list[i].checked = true;
            return
        }
    }
}
""".replace("__TABS_ID__", tabs_id)


def _ADD_SCRIPT(tabs_id):
    return """
function Add___TABS_ID__(pg,title,close_btn,scope_name,show,callback_id){
    var template = $('#Template__TABS_ID__').html();
    var obj = {
        index: String(pg),
        title: title,
        close_btn: close_btn,
        scope_name: scope_name,
        CALLBACK_ID: callback_id,
    };
    Mustache.parse(template);
    var rendered = Mustache.render(template, obj);
    page_node = $('<div></div>').html(rendered).children()
    tab_node = $('#__TABS_ID__');
    tab_node.append(page_node);
    if (show){
        option_str = '#__TABS_ID__'+String(pg)
        $(option_str)[0].checked = true;
    }
}
""".replace("__TABS_ID__", tabs_id)


class AdvancedTab(ComponentBase):
    def __init__(self, contents=[]):
        """
        contents: List Of [ Dict {
            title - str: 标题,
            scope - str (default:S{index}) 子域域名
            content - ComponentBase ：（可选）展示的内容
            checked - bool (default:False) : 默认是否显示
            close_btn - bool (default:True) : 是否允许关闭页面
        }]
        """
        super().__init__()
        self.tab_dict = {}
        self.init_contents = []
        self.tab_count = 0  # ID计数器，并不是当前总数！（无限递增，保证ID不重复）
        self.init(contents)
        self.unique_id = "AT_" + ''.join(sample(ascii_letters + digits, 10))
        self.on_content_change = None  # TAB内容改变时执行

    def init(self, contents=[]):
        subscopes = []
        self.tab_dict = {}
        for ind, content in enumerate(contents):
            assert isinstance(content, dict)
            assert 'title' in content
            content.setdefault("scope", f"S{ind}")
            assert content['scope'] not in subscopes
            subscopes.append(content['scope'])
            content.setdefault("checked", False)
            content.setdefault("close_btn", True)
            if "content" in content:
                assert isinstance(content["content"], ComponentBase)
            else:
                content["content"] = None

        self.init_contents = contents
        self.tab_count = len(self.tab_dict)  # ID计数器，并不是当前总数！（无限递增，保证ID不重复）

    @staticmethod
    def make_init_content(title: str, scope: Optional[str] = None, content: Optional[ComponentBase] = None,
                          close_btn: Optional[bool] = True, checked: Optional[bool] = False):
        obj = {
            'title': title,
            'scope': scope,
        }
        if content is not None:
            obj['content'] = content
        if checked is not None:
            obj['checked'] = checked
        if close_btn is not None:
            obj['close_btn'] = close_btn
        return obj

    def apply(self):
        # Initial Apply, 展示一个空的tab
        # 新增tab在on_apply中实现，必须先渲染空框架才能新增tab
        output = wo.put_widget(TABS_TPL(self.unique_id),
                               {
                                   "TEMPLATE_SCRIPT": _TEMPLATE_SCRIPT(self.unique_id),
                                   "CLOSE_SCRIPT": _CLOSE_SCRIPT(self.unique_id),
                                   "ADD_SCRIPT": _ADD_SCRIPT(self.unique_id),
                                   "CURRENT_SCRIPT": _CURRENT_SCRIPT(self.unique_id),
                                   "SHOWTAB_SCRIPT": _SHOWTAB_SCRIPT(self.unique_id),
                               })
        return output

    def on_apply(self):
        # print("清空之前页面")
        self.init(self.init_contents)
        # print("加载初始页面")
        for ind, D in enumerate(self.init_contents):
            self.add_tab(D["title"], D["scope"], D["content"], D["close_btn"], D["checked"])

    def add_tab(self, title: str, scope: Optional[str] = None, content: Optional["ComponentBase"] = None,
                enable_close=True, show_tab=True, save_tabs_info=True):
        """
        title - 标题
        scope - 子域域名，若不设置，则默认为 S{index}
        content:ComponentBase - 可选，新增tab后输出的东西
            ComponentBase实例的引用还会被保存到self.tab_dict[ind][content]
            !!只能传入ComponentBase!!
        enable_close - 是否右上角有叉
        show_tab - 是否显示新tab
        save_tabs_info - 设置为True时，若content不为空，在content的__tabs_info__字典中存入：
            {
                tab:self,
                index:用于del的编号
            }
        return:ScopeName - 新tab的域名
        """
        pg = self.tab_count
        if scope is None:
            scope = f"S{pg}"
        scope_name = self.scope + scope
        close_btn = "true" if enable_close else "false"
        show = "true" if show_tab else "false"
        func_name = "Add___TABS_ID__".replace("__TABS_ID__", self.unique_id)
        if enable_close:
            # 需要注册一个回调函数
            def onclick_callback(*args, **kwargs):
                print("我也不知道会传啥进来：",args,kwargs)
                self.del_tab(pg)

            callback_id = ws.get_current_session().register_callback(onclick_callback)
        else:
            callback_id = "NOTUSED"
        ws.eval_js(f"""{func_name}({pg},"{title}",{close_btn},"{scope_name}",{show},"{callback_id}")""")
        self.tab_dict[self.tab_count] = {
            "title": title,
            "scope": scope,
        }
        if content is not None:
            assert isinstance(content, ComponentBase)
            self.tab_dict[self.tab_count]["content"] = content
            content.scope = self.scope.add(scope)  # 先设定根场景防止意外
            content.PCRAPI = self.PCRAPI  # 传递API
            if save_tabs_info:
                setattr(content, "__tabs_info__", {
                    "tab": self,
                    "index": self.tab_count
                })
            with self.scope.add(scope).enter(clear=True):
                content.apply()
        self.tab_count += 1
        if self.on_content_change is not None:
            self.on_content_change()
        return self.scope + scope

    def del_tab(self, ind: int):
        """
        ind - self.tab_dict中的key值
        return True - 可能删除成功； False - tab_dict找不到key
        """
        if ind in self.tab_dict:

            # 自动跳页
            current_ind = self.current_tab()
            assert current_ind > -1
            if current_ind == ind:
                tab_list = list(self.tab_dict.keys())
                cur = tab_list.index(current_ind)
                if cur == 0:
                    # 跳后一页，如果有的话
                    self.show_tab(tab_list[cur + 1])
                else:
                    # 跳前一页
                    self.show_tab(tab_list[cur - 1])

            func_name = "Close___TABS_ID__".replace("__TABS_ID__", self.unique_id)
            ws.eval_js(f"{func_name}({ind})")
            del self.tab_dict[ind]
            if self.on_content_change is not None:
                self.on_content_change()
            return True
        else:
            return False

    def show_tab(self, ind: int):
        # 高亮指定index的tab
        # 若tab_dict中有，则尝试高亮并返回True，否则返回False
        if ind in self.tab_dict:
            func_name = "Show___TABS_ID__".replace("__TABS_ID__", self.unique_id)
            ws.eval_js(f"{func_name}({ind})")
            return True
        else:
            return False

    def current_tab(self):
        # 获取当前tab的index
        # -1: 没有tab
        func_name = "Current___TABS_ID__".replace("__TABS_ID__", self.unique_id)
        out = int(ws.eval_js(f"{func_name}()"))
        return out


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


class TabAdder(ComponentBase):
    def __init__(self, bind_tab: "AdvancedTab"):
        super().__init__()
        self.bind_tab = bind_tab

    def btn_click(self):
        S = self.scope
        title = S.get("TI")
        scope = S.get("SI")
        enable_close = len(S.get("EC")) == 1
        show_tab = len(S.get("ST")) == 1
        self.bind_tab.add_tab(title, scope, content=TestPage(), enable_close=enable_close, show_tab=show_tab)

    def apply(self):
        S = self.scope
        title_input = wp.put_input(S + "TI", label="标题")
        scope_input = wp.put_input(S + "SI", label="Scope")
        enable_close = wp.put_checkbox(S + "EC", ["允许关闭"])
        show_tab = wp.put_checkbox(S + "ST", ["显示新页面"])
        btn = wo.put_button("确定", self.btn_click)
        return wo.put_column([
            wo.put_text("新增TAB"),
            title_input,
            scope_input,
            enable_close,
            show_tab,
            btn
        ])


class TabDeler(ComponentBase):
    def __init__(self, bind_tab: "AdvancedTab"):
        super().__init__()
        self.bind_tab = bind_tab

    def btn_click(self):
        S = self.scope
        index = S.get("II")
        self.bind_tab.del_tab(index)

    def apply(self):
        S = self.scope
        index_input = wp.put_input(S + "II", label="输入编号", type=wi.NUMBER)
        btn = wo.put_button("确定", self.btn_click)
        return wo.put_column([
            wo.put_text("删除TAB"),
            index_input,
            btn
        ])


class MainPage(PageBase):
    def __init__(self, bind_tab: AdvancedTab):
        super().__init__()
        self.bind_tab = bind_tab
        self.tab_adder = TabAdder(bind_tab)
        self.tab_deler = TabDeler(bind_tab)

    def get_tab_json(self):
        return pformat(self.bind_tab.tab_dict)

    def refresh_code(self):
        S = self.scope
        with S.add("code").enter(clear=True):
            wo.put_code(self.get_tab_json())

    def apply(self):
        S = self.scope
        code_area = S.put_scope("code", content=[wo.put_code(self.get_tab_json())])
        return wo.put_row([
            wo.put_column([
                self.add_component(self.tab_adder, "adder"),
                self.add_component(self.tab_deler, "deler"),
            ]),
            code_area,
        ])


class MainAPP(ComponentBase):
    def __init__(self):
        super().__init__()
        self.TAB = AdvancedTab()
        self.MainPage = MainPage(self.TAB)  # 先绑定
        self.TAB.init([AdvancedTab.make_init_content("MAIN", "main", self.MainPage, False, True)])  # 重新init实现双向绑定
        self.TAB.on_content_change = self.MainPage.refresh_code  # TAB内容改变时，刷新code显示

    def apply(self):
        out = wo.put_column([
            self.add_component(self.TAB, name="TAB"),
            wo.put_html(html),
        ])
        return out


if __name__ == "__main__":
    app = MainAPP()
    pywebio.start_server(app, 10239)
    # from pywebio.session.threadbased import ScriptModeSession
