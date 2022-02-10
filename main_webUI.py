import pywebio
from pywebio.output import put_row, put_column, put_code, put_grid, put_text, span, put_scope


def emuidemo():
    put_row([
        put_column([
            put_code('模拟器列表视图'),
            put_row([
                put_scope('TAB', content=put_code('A\nC\nD\nC\nD\nC\nD\nC\nD\nC\nD\nC\nD')), None,
                put_column([
                    put_scope('A1', content=put_code('A模拟器截图/视频推流，界面\nC\nD')),
                    put_scope('A2', content=put_code('A模拟器控制区input区分为单独控制\nC\nD')),
                    put_scope('A3', content=put_code('A账号进度区可查看当前执行任务【任务列表】进度表\nC\nD'))
                ], size='auto auto auto'),
                None,
                put_scope('B', content=put_code('B日志区\nC\nD\nC\nD\nC\nD\nC\nD\nC\nD\nC\nD')),
            ], size='10% 5px 40% 20px auto')
        ], size='auto auto')
    ], size='auto')
    # put_grid([
    #     [put_code('A')],
    #     [put_code('A'),put_code('A'),put_code('A')],
    # ], cell_width='100px', cell_height='100px')


emuidemo()
