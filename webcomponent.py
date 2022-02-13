from abc import abstractmethod, ABC

import pywebio.output as wo
import pywebio.pin as wp
from pywebio import start_server


class ScopeName(str):
    def __new__(cls, name):
        return str.__new__(ScopeName, name)  # noqa

    def enter(self, clear=False):
        parent = self

        class ScopeName_:
            def __enter__(self):
                if parent == "__root__":
                    return ScopeName(wo.get_scope())  # Current Root
                else:
                    wo.use_scope(parent, clear=clear).__enter__()
                    return parent

            def __exit__(self, *args, **kwargs):
                if parent != "__root__":
                    wo.use_scope(parent, clear=clear).__exit__(*args, **kwargs)

        return ScopeName_()

    def add(self, scope):
        if self == "__root__":
            return ScopeName(scope)
        else:
            return ScopeName(str(self) + "_" + scope)

    def put_scope(self, name: str, content=[], position=wo.OutputPosition.BOTTOM):
        return wo.put_scope(self + name, content, scope=self, position=position)

    def get(self, name: str, strict=True):
        return wp.get_pin_value(self + name, strict)

    def __add__(self, other):
        return ScopeName(self.add(other))


class ComponentBase(ABC):
    def __init__(self, scope=None):
        if scope is None:
            scope = "__root__"
        self.scope = ScopeName(scope)

    @abstractmethod
    def apply(self):
        """
        元件实现的主要部分
        """
        pass

    def add_component(self, component: "ComponentBase", name=None):
        if name is None:
            component.scope = self.scope
            out = component.apply()
            return out
        else:
            component.scope = self.scope + name
            out = component.apply()
            return out

    def __call__(self):
        return self.apply()


class CalcPlus(ComponentBase):
    def get_A(self):
        A1 = self.scope.add("A1")
        return A1.get("A")

    def get_B(self):
        A1 = self.scope.add("A1")
        return A1.get("B")

    def btn_click(self):
        with self.scope.add("A2").enter(clear=True) as S:
            print("Put Text To", S)
            A = self.get_A()
            B = self.get_B()
            print("Get A = ", A, "B = ", B)
            wo.put_text(f"Result: {A + B}")

    def apply(self):
        print("Add S:", self.scope)
        A1 = self.scope.add("A1")
        title = wo.put_text("A+B Problem")
        input_A = wp.put_input(A1 + "A", type='number', label="A")
        input_B = wp.put_input(A1 + "B", type='number', label="B")
        btn = wo.put_button("CALC", onclick=self.btn_click)
        layer = wo.put_column([
            title,
            wo.put_row([input_A, input_B, btn])
        ])
        area_1 = self.scope.put_scope("A1", content=[layer])
        area_2 = self.scope.put_scope("A2", content=[])
        return wo.put_column([
            area_1,
            area_2
        ])


class CalcMinus(ComponentBase):
    def get_A(self):
        A1 = self.scope.add("A1")
        return A1.get("A")

    def get_B(self):
        A1 = self.scope.add("A1")
        return A1.get("B")

    def btn_click(self):
        with self.scope.add("A2").enter(clear=True) as S:
            print("Put Text To", S)
            A = self.get_A()
            B = self.get_B()
            print("Get A = ", A, "B = ", B)
            wo.put_text(f"Result: {A - B}")

    def apply(self):
        print("Minus S:", self.scope)
        A1 = self.scope.add("A1")
        title = wo.put_text("A-B Problem")
        input_A = wp.put_input(A1 + "A", type='number', label="A")
        input_B = wp.put_input(A1 + "B", type='number', label="B")
        btn = wo.put_button("CALC", onclick=self.btn_click)
        layer = wo.put_column([
            title,
            wo.put_row([input_A, input_B, btn])
        ])
        area_1 = self.scope.put_scope("A1", content=[layer])
        area_2 = self.scope.put_scope("A2", content=[])
        return wo.put_column([
            area_1,
            area_2
        ])


class CalcArea(ComponentBase):
    def __init__(self):
        super().__init__()
        self.plus = CalcPlus()
        self.minus = CalcMinus()

    def apply(self):
        print("CALC:", self.scope)
        tabs = wo.put_tabs([
            dict(title="PLUS", content=self.add_component(self.plus, "plus")),
            dict(title="MINUS", content=self.add_component(self.minus, "minus")),
        ])
        return tabs


class DisplayAllNumbers(ComponentBase):
    def __init__(self, bind_calcarea: CalcArea):
        super().__init__()
        self.bind = bind_calcarea

    def btn_click(self):
        P_A = self.bind.plus.get_A()
        P_B = self.bind.plus.get_B()
        M_A = self.bind.minus.get_A()
        M_B = self.bind.minus.get_B()
        with self.scope.add("B").enter(clear=False):
            wo.put_text(f"Plus:{P_A}+{P_B}  Minus:{M_A}-{M_B}")

    def apply(self):
        print("DISP:", self.scope)
        btn = wo.put_button("GetALL", onclick=self.btn_click)
        area_A = self.scope.put_scope("A", content=[btn])
        area_B = self.scope.put_scope("B")
        layer = wo.put_column([
            area_A,
            area_B
        ])
        return layer


class MainApp(ComponentBase):
    def __init__(self):
        super().__init__()
        self.calc = CalcArea()
        self.disp = DisplayAllNumbers(self.calc)

    def apply(self):
        print("MAIN:", self.scope)
        layer = wo.put_column([
            wo.put_text("Plus And Minus Demo"),
            wo.put_row([self.add_component(self.calc, "calc"),
                        self.add_component(self.disp, "disp")])
        ])
        return layer


if __name__ == "__main__":
    """
    元件结构
    MainApp {
        CalcArea {
            CalcPlus,
            CalcMinus,
        },
        DisplayAllNumbers
    }
    """
    server = start_server(MainApp(), port=10234)
