import time
import asyncio
from config import WLAN_SSID, WLAN_PASSWORD
from machine import idle
from network import WLAN, STA_IF

INITIAL_TIMEOUT = const(10000) # milliseconds
RECONNECT_INTERVAL = const(60) # seconds

class WLANhandler:
    wlan: WLAN
    last_attempt: int

    def __init__(self) -> None:
        self.wlan = WLAN(STA_IF)
        self.wlan.active(True)

        print("connecting to wlan...")
        self.connect()

        if self.connected():
            print("connected to wlan with: ", self.wlan.ipconfig("addr4"))

    def connected(self) -> bool:
        return self.wlan.isconnected()

    async def run(self) -> None:
        while True:
            await asyncio.sleep(RECONNECT_INTERVAL)
            if not self.connected():
                self.connect()
                print("attampting wlan reconnect...")
            

    def connect(self) -> None:
        self.wlan.connect(WLAN_SSID, WLAN_PASSWORD)
        connection_start = time.ticks_ms()
        while not self.connected():
            if time.ticks_diff(time.ticks_ms(), connection_start) >= INITIAL_TIMEOUT:
                print("timeout trying to connect to wlan.")
                break
            idle()