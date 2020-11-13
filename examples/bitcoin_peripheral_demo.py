import time
import board
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag

i2c = board.I2C()

# You can display in 'GBP', 'EUR' or 'USD'
CURRENCY = "USD"
# Set up where we'll be fetching data from
DATA_SOURCE = "https://api.coindesk.com/v1/bpi/currentprice.json"
DATA_LOCATION = ["bpi", CURRENCY, "rate_float"]


def text_transform(val):
    if CURRENCY == "USD":
        return "$%d" % val
    if CURRENCY == "EUR":
        return "‎€%d" % val
    if CURRENCY == "GBP":
        return "£%d" % val
    return "%d" % val


magtag = MagTag(
    default_bg="/bitcoin_grayscale.bmp", url=DATA_SOURCE, json_path=DATA_LOCATION,
)

magtag.network.connect()

magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(
        (magtag.graphics.display.width // 2) - 1,
        (magtag.graphics.display.height // 2) - 1,
    ),
    text_scale=3,
)

magtag.preload_font(b"$012345789")  # preload numbers
magtag.preload_font((0x00A3, 0x20AC))  # preload gbp/euro symbol

buttons = magtag.peripherals.buttons
button_colors = ((255, 0, 0), (255, 150, 0), (0, 255, 255), (180, 0, 255))
button_tones = (1047, 1318, 1568, 2093)
timestamp = time.monotonic()

while True:
    for i, b in enumerate(buttons):
        if not b.value:
            print("Button %c pressed" % chr((ord("A") + i)))
            magtag.peripherals.neopixel_disable = False
            magtag.peripherals.neopixels.fill(button_colors[i])
            magtag.peripherals.play_tone(button_tones[i], 0.25)
            break
    else:
        magtag.peripherals.neopixel_disable = True

    if (time.monotonic() - timestamp) > 5:  # once a second...
        print("Battery voltage? ", magtag.peripherals.battery)
        while not i2c.try_lock():
            pass
        print(
            "I2C addresses found:",
            [hex(device_address) for device_address in i2c.scan()],
        )
        i2c.unlock()
        try:
            value = magtag.fetch()
            print("Response is", value)
        except (ValueError, RuntimeError) as e:
            print("Some error occured, retrying! -", e)
        timestamp = time.monotonic()

    time.sleep(0.01)
