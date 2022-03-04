def get_huodong_by_code(code: str):
    from scenes.huodong.HD20220208 import Map20220208
    HUODONG_CODE = {
        "current": Map20220208,
        "20220208": Map20220208,
    }
    if code in HUODONG_CODE:
        return HUODONG_CODE[code]
    else:
        raise ValueError(f"没有编号为{code}的活动，请检查scenes/huodng/huodong_manager.py！")
