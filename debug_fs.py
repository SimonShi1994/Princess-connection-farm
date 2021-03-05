from screencut import AutomatorDebuger

if __name__ == "__main__":
    self = AutomatorDebuger()
    # self.Init()
    self.Connect()
    # self.ocr_center
    self.Account("debug")
    # self.ATX.restart_agent()
    # self.ATX.refresh_minicap(10, 0, 80)
    # self.stop_th()
    # self.init_fastscreen()
    from tqdm import tqdm

    sc = self.getscreen()  # Warm Up
    pbar = tqdm(desc="testing..", total=50)

    for i in range(50):
        sc = self.getscreen()
        pbar.update(1)
    pbar.close()
