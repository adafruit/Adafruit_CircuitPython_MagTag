# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
import terminalio
from adafruit_magtag.magtag import MagTag

# Set up where we'll be fetching data from
DATA_SOURCE = "https://api.coindesk.com/v1/bpi/currentprice.json"
DATA_LOCATION = ["bpi", "USD", "rate_float"]


def text_transform(val):
    return "Bitcoin: $%d" % val


magtag = MagTag(
    url=DATA_SOURCE,
    json_path=DATA_LOCATION,
)

magtag.network.connect()

magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(
        10,
        (magtag.graphics.display.height // 2) - 1,
    ),
    text_scale=3,
    text_transform=text_transform,
)

magtag.preload_font(b"$012345789")  # preload numbers
magtag.preload_font((0x00A3, 0x20AC))  # preload gbp/euro symbol

timestamp = None

while True:
    if not timestamp or (time.monotonic() - timestamp) > 60:  # once every 60 seconds...
        try:
            value = magtag.fetch()
            print("Response is", value)
        except (ValueError, RuntimeError) as e:
            print("Some error occured, retrying! -", e)
        timestamp = time.monotonic()
