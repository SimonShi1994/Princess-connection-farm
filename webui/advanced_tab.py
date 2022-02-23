import pywebio.input as wi
from collections import OrderedDict
from pprint import pformat
import pywebio.output as wo
import pywebio.pin as wp
import pywebio.session as ws
import pywebio

from webui.pcr_component import ComponentBase
from random import sample
from typing import Optional
from string import ascii_letters, digits

html = """
<button type="button" onclick="myFunction()"> 点我！ </button>
<script>
function myFunction(){
    alert("Hello World!");
}
</script>
"""

def TABS_TPL(tabs_id:str):
    return """
<div class="webio-tabs" id="__TABS_ID__">
{{#tabs}}
    <input type="radio" class="toggle" name="__TABS_ID__" id="__TABS_ID__{{index}}" myindex="{{index}}" {{#checked}}checked{{/checked}}>
    <label for="__TABS_ID__{{index}}">
        <p>{{title}}</p>
        {{#close_btn}}<button type="button" onclick="Close___TABS_ID__({{index}})">x</button>{{/close_btn}}
    </label>
    <div class="webio-tabs-content">
    {{#content}}
        {{& pywebio_output_parse}}
    {{/content}}
    </div>
{{/tabs}}
{{{TEMPLATE_SCRIPT}}}
<script>
{{{CLOSE_SCRIPT}}}
{{{ADD_SCRIPT}}}
{{{CURRENT_SCRIPT}}}
{{{SHOWTAB_SCRIPT}}}
</script>
</div>""".replace("__TABS_ID__",tabs_id)
def _TEMPLATE_SCRIPT(tabs_id):
    # index, title, close_btn, scope_name
    return """
<script id="Template__TABS_ID__" type="x-tmpl-mustache">
<input type="radio" class="toggle" name="__TABS_ID__" id="__TABS_ID__{{index}}" myindex="{{index}}">
<label for="__TABS_ID__{{index}}">
    <p>{{title}}</p>
    {{#close_btn}}<button type="button" onclick="Close___TABS_ID__({{index}})">x</button>{{/close_btn}}
</label>
<div class="webio-tabs-content">
    <div id="pywebio-scope-{{scope_name}}"></div>
</div>
</script>
""".replace("__TABS_ID__",tabs_id)
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
""".replace("__TABS_ID__",tabs_id)
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
""".replace("__TABS_ID__",tabs_id)
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
""".replace("__TABS_ID__",tabs_id)
def _ADD_SCRIPT(tabs_id):
    return """
function Add___TABS_ID__(pg,title,close_btn,scope_name,show){
    var template = $('#Template__TABS_ID__').html();
    var obj = {
        index: String(pg),
        title: title,
        close_btn: close_btn,
        scope_name: scope_name
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
""".replace("__TABS_ID__",tabs_id)
class AdvancedTab(ComponentBase):
    def __init__(self,contents=[]):
        """
        ！！contents中不需要使用self.add_component，因为contents本身要求输入scope了。！！
        contents: List Of [ Dict {
            title - str: 标题,
            scope - str (default:S{index}) 子域域名
            contents - list (default:[]) : 初始内容，同put_scope
            checked - bool (default:False) : 默认是否显示
            close_btn - bool (default:True) : 是否允许关闭页面
        }]
        """
        super().__init__()
        self.init(contents)
        self.unique_id = "AT_"+''.join(sample(ascii_letters + digits, 10))

    @staticmethod
    def make_init_content(title:str,scope:Optional[str]=None,contents:Optional[list]=None,
                     checked:Optional[bool]=False,close_btn:Optional[bool]=True):
        obj = {
            'title':title,
            'scope':scope,
        }
        if contents is not None:
            obj['contents'] = contents
        if checked is not None:
            obj['checked'] = checked
        if close_btn is not None:
            obj['close_btn'] = close_btn
        return obj
    def init(self,contents=[]):
        subscopes = []
        self.tab_dict = OrderedDict({})
        for ind, content in enumerate(contents):
            assert isinstance(content, dict)
            assert 'title' in content
            content.setdefault("scope", f"S{ind}")
            assert content['scope'] not in subscopes
            subscopes.append(content['scope'])
            content.setdefault("checked", False)
            content.setdefault("close_btn", True)
            content.setdefault("contents", [])
            assert isinstance(content["contents"], list)

            D = self.tab_dict.setdefault(ind, {})
            D["title"] = content["title"]
            D["scope"] = content["scope"]

        self.init_contents = contents
        self.tab_count = len(self.tab_dict)  # ID计数器，并不是当前总数！（无限递增，保证ID不重复）
        return self


    def apply(self):
        print(self.init_contents)
        output = wo.put_widget(TABS_TPL(self.unique_id),
                      {
                          "tabs":[
                              {
                                  "index":str(ind),
                                  "title":cont["title"],
                                  "checked":cont["checked"],
                                  "close_btn":cont["close_btn"],
                                  "content":wo.put_scope(self.scope.add(cont['scope']),
                                                         cont['contents'])
                              } for ind,cont in enumerate(self.init_contents)
                          ],
                          "TEMPLATE_SCRIPT":_TEMPLATE_SCRIPT(self.unique_id),
                          "CLOSE_SCRIPT":_CLOSE_SCRIPT(self.unique_id),
                          "ADD_SCRIPT":_ADD_SCRIPT(self.unique_id),
                          "CURRENT_SCRIPT":_CURRENT_SCRIPT(self.unique_id),
                          "SHOWTAB_SCRIPT":_SHOWTAB_SCRIPT(self.unique_id),
                      })
        self.init_contents = None  # 好像必须得None触发__del__才能让他输出
        return output

    def add_tab(self, title: str, scope:Optional[str]=None, content:Optional["ComponentBase"]=None,
                enable_close=True,show_tab=True,save_tabs_info=True):
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
        scope_name = self.scope+scope
        close_btn = "true" if enable_close else "false"
        show = "true" if show_tab else "false"
        func_name = "Add___TABS_ID__".replace("__TABS_ID__",self.unique_id)
        ws.run_js(f"""{func_name}({pg},"{title}",{close_btn},"{scope_name}",{show})""")
        self.tab_dict[self.tab_count]={
            "title":title,
            "scope":scope,
        }
        if content is not None:
            assert isinstance(content,ComponentBase)
            self.tab_dict["content"]=content
            content.scope = self.scope.add(scope)  # 先设定根场景防止意外
            content.PCRAPI = self.PCRAPI  # 传递API
            if save_tabs_info:
                setattr(content,"__tabs_info__",{
                    "tab":self,
                    "index":self.tab_count
                })
            with self.scope.add(scope).enter(clear=True):
                content.apply()
        self.tab_count += 1

        return self.scope+scope

    def del_tab(self,ind:int):
        """
        ind - self.tab_dict中的key值
        return True - 可能删除成功； False - tab_dict找不到key
        """
        if ind in self.tab_dict:

            # 自动跳页
            current_ind = self.current_tab()
            assert current_ind>-1
            if current_ind == ind:
                tab_list = list(self.tab_dict.keys())
                cur = tab_list.index(current_ind)
                if cur==0:
                    # 跳后一页，如果有的话
                    self.show_tab(tab_list[cur+1])
                else:
                    # 跳前一页
                    self.show_tab(tab_list[cur-1])

            func_name = "Close___TABS_ID__".replace("__TABS_ID__", self.unique_id)
            ws.run_js(f"{func_name}({ind})")
            del self.tab_dict[ind]
            return True
        else:
            return False

    def show_tab(self,ind:int):
        # 高亮指定index的tab
        # 若tab_dict中有，则尝试高亮并返回True，否则返回False
        if ind in self.tab_dict:
            func_name = "Show___TABS_ID__".replace("__TABS_ID__", self.unique_id)
            ws.run_js(f"{func_name}({ind})")
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
        IN = wp.put_input(S+"IN",label="Test",value=f"My Name:{S+'IN'}")
        ti = self.__tabs_info__
        del_btn = wo.put_button("关闭",onclick=self.del_me)
        return wo.put_column([
            wo.put_text(f"PAGE SCOPE: {self.scope}"),
            wo.put_text(f"PAGE INDEX: {ti['index']}"),
            IN,
            del_btn
        ])

class TabAdder(ComponentBase):
    def __init__(self, bind_tab: "AdvancedTab", bind_mainpage:"MainPage"):
        super().__init__()
        self.bind_tab = bind_tab
        self.bind_mainpage = bind_mainpage

    def btn_click(self):
        S = self.scope
        title = S.get("TI")
        scope = S.get("SI")
        enable_close = len(S.get("EC"))==1
        show_tab = len(S.get("ST"))==1
        self.bind_tab.add_tab(title,scope,content=TestPage(),enable_close=enable_close,show_tab=show_tab)
        self.bind_mainpage.refresh_code()

    def apply(self):
        S = self.scope
        title_input = wp.put_input(S+"TI",label="标题")
        scope_input = wp.put_input(S+"SI",label="Scope")
        enable_close = wp.put_checkbox(S+"EC",["允许关闭"])
        show_tab = wp.put_checkbox(S+"ST",["显示新页面"])
        btn = wo.put_button("确定",self.btn_click)
        return wo.put_column([
            wo.put_text("新增TAB"),
            title_input,
            scope_input,
            enable_close,
            show_tab,
            btn
        ])

class TabDeler(ComponentBase):
    def __init__(self, bind_tab: "AdvancedTab", bind_mainpage:"MainPage"):
        super().__init__()
        self.bind_tab = bind_tab
        self.bind_mainpage = bind_mainpage

    def btn_click(self):
        S = self.scope
        index = S.get("II")
        self.bind_tab.del_tab(index)
        self.bind_mainpage.refresh_code()

    def apply(self):
        S = self.scope
        index_input = wp.put_input(S+"II",label="输入编号",type=wi.NUMBER)
        btn = wo.put_button("确定",self.btn_click)
        return wo.put_column([
            wo.put_text("删除TAB"),
            index_input,
            btn
        ])

class MainPage(PageBase):
    def __init__(self, bind_tab:AdvancedTab):
        super().__init__()
        self.bind_tab = bind_tab
        self.tab_adder = TabAdder(bind_tab,self)
        self.tab_deler = TabDeler(bind_tab,self)

    def get_tab_json(self):
        return pformat(self.bind_tab.tab_dict)

    def refresh_code(self):
        S = self.scope
        with S.add("code").enter(clear=True):
            wo.put_code(self.get_tab_json())

    def apply(self):
        S = self.scope
        code_area = S.put_scope("code",content=[wo.put_code(self.get_tab_json())])
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
        self.MainPage = MainPage(self.TAB)
    def apply(self):
        out = wo.put_column([
            self.TAB.init([
                AdvancedTab.make_init_content("MAIN","main",[self.MainPage()],True,False)
            ]).apply(),
            wo.put_html(html),
        ])
        return out

if __name__ == "__main__":
    app = MainAPP()
    pywebio.start_server(app,10234)
