from framebuf import FrameBuffer, MONO_HLSB
from state import State, TEMPERATURE_STATE_KEY, TARGET_TEMPERATURE_STATE_KEY, HUMIDITY_STATE_KEY, MODE_STATE_KEY
from lib.sh1106 import SH1106_I2C
from machine import Pin, I2C

WIDTH = const(128)
HEIGTH = const(64)
FREQUENCY = const(400000)


def text_scaled(
    display: SH1106_I2C, text: str, x: int, y: int, scale: int = 2, color: int = 1
):
    # Temporary 8x8 framebuffer
    buf = bytearray(8)
    fb = FrameBuffer(buf, 8, 8, MONO_HLSB)

    for char in text:
        fb.fill(0)
        fb.text(char, 0, 0, 1)

        for cx in range(8):
            for cy in range(8):
                if fb.pixel(cx, cy):
                    for dx in range(scale):
                        for dy in range(scale):
                            display.pixel(
                                x + cx * scale + dx, y + cy * scale + dy, color
                            )

        x += 8 * scale


class Display:
    scl: Pin
    sda: Pin
    i2c: I2C
    display: SH1106_I2C

    def __init__(self, scl: int, sda: int) -> None:
        self.scl = Pin(scl)
        self.sda = Pin(sda)

        # I2C setup
        self.i2c = I2C(0, scl=self.scl, sda=self.sda, freq=FREQUENCY)

        # OLED setup
        self.display = SH1106_I2C(WIDTH, HEIGTH, self.i2c)
        pass

    def handle_state_change(self, state: State) -> None:
        temperature = state.get(TEMPERATURE_STATE_KEY)
        target_teperature = state.get(TARGET_TEMPERATURE_STATE_KEY)
        humidity = state.get(HUMIDITY_STATE_KEY)
        mode = state.get(MODE_STATE_KEY)

        display = self.display

        display.fill(0)
        display.text(f"{humidity}%", 87, 55)
        display.text(f"{target_teperature}C", 0, 55)
        display.text(mode, 0, 0)
        text_scaled(display, f"{temperature}C", 23, 23)
        display.show()
