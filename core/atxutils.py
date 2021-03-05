import time

import adbutils
import uiautomator2 as u2

from core.pcr_config import debug


class AtxClient:
    def __init__(self, device: adbutils.AdbDevice = None):
        self.device = device
        self.base_minicap_refresh_url_format = "curl 127.0.0.1:7912/v2/minicap?frameRate={}&rotate={}&jpgQuality={}"

    def refresh_minicap(self, frame_rate: float = 10.0, rotation: int = 0, jpg_quality: int = 80) -> bool:
        for i in range(60):
            res = self._refresh_minicap(frame_rate, rotation, jpg_quality)
            if "success" not in res:
                if debug:
                    print(res)
                time.sleep(1)
            else:
                return True
        return False

    def _refresh_minicap(self, frame_rate: float=10.0, rotation: int=0, jpg_quality: int=80) -> str:
        return self.device.shell(self.base_minicap_refresh_url_format.format(frame_rate, rotation, jpg_quality))

    def push_binary(self) -> bool:
        output = self.device.adb_output("push", "atx-agent/atx-agent", "/data/local/tmp/atx-agent")
        if output is not None:
            print(output)
            self.device.shell("chmod 777 /data/local/tmp/atx-agent")
            return True
        return False

    def restart_agent(self) -> bool:
        output = self.device.shell("/data/local/tmp/atx-agent server -d --stop")
        if "atx-agent listening on" in output:
            print(output)
            return True
        return False

if __name__ == '__main__':
    d = adbutils.adb.device("emulator-5554")
    atx = AtxClient(d)
    atx.push_binary()
    atx.restart_agent()
    u2.connect()
    print(atx.refresh_minicap())