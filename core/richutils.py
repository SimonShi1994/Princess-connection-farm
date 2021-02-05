# RICH PRINT!
from rich import box as rbox
from rich.style import Style
from rich.table import Table
from rich.text import Text


class RText(Text):
    def __init__(self, *args, sep=' '):
        self.txt = sep.join([str(a) for a in args])
        super().__init__(self.txt)
        self.sty()

    def sty(self):
        pass


class RTitle(RText):
    def sty(self):
        self.stylize(Style(color="red", bold=True, underline=True))


class RSubTitle(RText):
    def sty(self):
        self.stylize(Style(color="cyan", bold=True))


class RValue(RText):
    def sty(self):
        self.stylize(Style(color="yellow", italic=True))

class RComment(RText):
    def sty(self):
        self.stylize(Style(color="magenta"))

class ROneTable(Table):
    def __init__(self, *args):
        super().__init__(args[0], pad_edge=True)
        for t in args[1:]:
            self.add_row(t)


class RNoHeadTable(Table):
    def __init__(self, title=None):
        super().__init__(title=title, show_header=False, box=rbox.ROUNDED)


class ROrderGrid(Table):
    def __init__(self, c, title=None):
        super().__init__(title=title, show_edge=False, show_header=False, pad_edge=False, show_lines=False,
                         box=rbox.SIMPLE, min_width=0,
                         collapse_padding=True)
        self.c = c
        self.cache_c = []

    def add(self, obj):
        self.cache_c += [obj]
        if len(self.cache_c) >= self.c:
            self.add_row(*self.cache_c)
            self.cache_c = []

    def finish(self):
        if len(self.cache_c) >= 0:
            self.add_row(*(self.cache_c + [] * (self.c - len(self.cache_c))))
            self.cache_c = []


class RProgress(ROrderGrid):
    def __init__(self, complete, total, width=15, percent=True):
        super().__init__(2)
        num = int(round(width * complete / total))
        bar_str = ['✦'] * num
        empty_str = ['·'] * (width - num)
        bar_str = ''.join(bar_str)
        empty_str = ''.join(empty_str)
        self.add(RSubTitle(bar_str) + RText(empty_str))
        if percent:
            self.add(RValue("%.0f%%" % (complete / total * 100)))
        self.finish()


class RLRProgress(ROrderGrid):
    def __init__(self, complete, total, L, R, width=15, percent=True):
        super().__init__(4)
        num = int(round(width * complete / total))
        bar_str = ['✦'] * num
        empty_str = ['·'] * (width - num)
        bar_str = ''.join(bar_str)
        empty_str = ''.join(empty_str)
        self.add(L)
        self.add(RSubTitle(bar_str) + RText(empty_str))
        if percent:
            self.add(RValue("%.0f%%" % (complete / total * 100)))
        self.add(R)
        self.finish()
