from typing import TYPE_CHECKING,Optional
import os
import datetime,time


if TYPE_CHECKING:
    from automator_mixins._base import BaseMixin


class PCRError(Exception):
    error_dir="PCRError"
    def __init__(self,*args,automator:Optional["BaseMixin"]=None,screen_log=False,text_log=False,error_dir:Optional[str]=None):
        self.a=automator
        self.screen_log=screen_log
        self.text_log=text_log
        if error_dir is not None:
            self.error_dir=error_dir
        super().__init__(*args)
        self.record()

    def record(self):
        if self.a is None:
            return
        os.makedirs(self.error_dir)
        curtime=time.time()
        time_str=datetime.datetime.fromtimestamp(curtime).strftime("%Y%m%d%H%M%S")
        filename="%s_%s_%s"%(self.error_dir,self.a.account,time_str)
        if self.text_log:
            with open(filename+".log","w",encoding="utf-8") as f:
                f.write(self.__str__())
        if self.screen_log:
            self.a.save_last_screen(filename+".jpg")

class RecognizeError(PCRError):
    error_dir="PCRError/RecognizeError"
    pass

class ZhuxianIDRecognizeError(RecognizeError):
    error_dir = "PCRError/RecognizeError/ZhuXianID"
    pass

class MaoxianRecognizeError(RecognizeError):
    error_dir = "PCRError/RecognizeError/MaoXian"
    pass


