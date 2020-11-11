# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_magtag.epaper`
================================================================================

Helper Library for the Adafruit MagTag.


* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Hardware:**

* `Adafruit MagTag <https://www.adafruit.com/product/4800>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

import board
from time import sleep
import displayio
import adafruit_il0373

MAGTAG_29_GRAYSCALE = 1

DISPLAY_TYPE_MONO = 1
DISPLAY_TYPE_TRICOLOR = 2
DISPLAY_TYPE_GRAYSCALE = 3

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MagTag.git"

class EPaper:
    """Class representing the EPaper Display. This is used to automatically
    initialize the display.

    :param int width: The width of the display in Pixels. Defaults to 64.
    :param int height: The height of the display in Pixels. Defaults to 32.
    :param int rotation: The degrees to rotate the display. Defaults to 270.
    """

    # pylint: disable=too-few-public-methods,too-many-branches
    def __init__(
        self,
        profile=MAGTAG_29_GRAYSCALE,
        rotation=270,
    ):
        display_type = None
        self._refresh_time = 5

        if profile == MAGTAG_29_GRAYSCALE:
            width = 296
            height = 128
            display_type = DISPLAY_TYPE_GRAYSCALE
        else:
            raise ValueError("Unknown MagTag Profile")

        try:
            displayio.release_displays()
            display_bus = displayio.FourWire(
                board.SPI(), command=board.EPD_DC, chip_select=board.EPD_CS, reset=board.EPD_RESET, baudrate=1000000
            )
            sleep(1)
            if display_type == DISPLAY_TYPE_GRAYSCALE:
                self.display = adafruit_il0373.IL0373(
                    display_bus,
                    width=width,
                    height=height,
                    rotation=rotation,
                    black_bits_inverted=False,
                    color_bits_inverted=False,
                    grayscale=True,
                    refresh_time=1,
                    seconds_per_frame=self._refresh_time,
                )
        except ValueError:
            raise RuntimeError("Failed to initialize ePaper Display") from ValueError

    @property
    def refresh_time(self):
        return self._refresh_time
