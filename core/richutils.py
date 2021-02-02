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
