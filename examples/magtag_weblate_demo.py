# SPDX-FileCopyrightText: 2020 Tim C, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
"""
Pull the current translated percent of CircuitPython
from Weblate and show it on the screen with text
and a progress bar
"""
import time
import terminalio
from adafruit_progressbar import ProgressBar
from adafruit_magtag.magtag import MagTag

# wait before anything
time.sleep(4)

# Set up where we'll be fetching data from
DATA_SOURCE = "https://hosted.weblate.org/api/projects/circuitpython/statistics/"
DATA_LOCATION = ["translated_percent"]


def text_transform(val):
    """ format the text for showing on the screen """
    return "Translated: {}%".format(val)


magtag = MagTag(
    url=DATA_SOURCE,
    json_path=DATA_LOCATION,
)

magtag.network.connect()

# translated % label
magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(
        (magtag.graphics.display.width // 2) - 1,
        42,
    ),
    text_scale=2,
    text_transform=text_transform,
    text_anchor_point=(0.5, 0.5),
)

# url label
BOTTOM_LBL_TXT = "hosted.weblate.org/projects/circuitpython/"
magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(
        (magtag.graphics.display.width // 2) - 1,
        (magtag.graphics.display.height) - 8,
    ),
    text_scale=1,
    text_transform=text_transform,
    text_anchor_point=(0.5, 1.0),
    is_data=False,
)

# CircuitPython label
TOP_LBL_TXT = "CircuitPython"
magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(
        (magtag.graphics.display.width // 2) - 1,
        12,
    ),
    text_scale=2,
    text_transform=text_transform,
    text_anchor_point=(0.5, 0.5),
    is_data=False,
)

# set the static labels
magtag.set_text(BOTTOM_LBL_TXT, index=1)
magtag.set_text(TOP_LBL_TXT, index=2)

# set progress bar width and height relative to board's display
BAR_WIDTH = magtag.graphics.display.width - 80
BAR_HEIGHT = 30

BAR_X = magtag.graphics.display.width // 2 - BAR_WIDTH // 2
BAR_Y = 66

# Create a new progress_bar object at (BAR_X, BAR_Y)
progress_bar = ProgressBar(
    BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT, 1.0, bar_color=0x999999, outline_color=0x000000
)

# add progress bar to main group
magtag.graphics.splash.append(progress_bar)

timestamp = None

while True:
    if (
        not timestamp or (time.monotonic() - timestamp) > 600
    ):  # once every 600 seconds...
        try:
            value = magtag.fetch()
            print("Response is", value)
            time.sleep(5)
            progress_bar.progress = value / 100.0
            magtag.refresh()
        except (ValueError, RuntimeError) as e:
            print("Some error occured, retrying! -", e)
        timestamp = time.monotonic()
