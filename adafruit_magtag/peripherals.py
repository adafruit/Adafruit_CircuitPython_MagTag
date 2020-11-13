# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_magtag.peripherals`
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
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
import neopixel
import simpleio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MagTag.git"


class Peripherals:
    """Peripherals Helper Class for the MagTag Library"""

    # pylint: disable=too-many-instance-attributes, too-many-locals, too-many-branches, too-many-statements
    def __init__(self):
        # Neopixels
        self.neopixels = neopixel.NeoPixel(board.NEOPIXEL, 4, brightness=0.3)
        self._neopixel_disable = DigitalInOut(board.NEOPIXEL_POWER)
        self._neopixel_disable.direction = Direction.OUTPUT
        self._neopixel_disable.value = False

        # Battery Voltage
        self._batt_monitor = AnalogIn(board.BATTERY)

        # Speaker Enable
        self._speaker_enable = DigitalInOut(board.SPEAKER_ENABLE)
        self._speaker_enable.direction = Direction.OUTPUT
        self._speaker_enable.value = False

        # Buttons
        self.buttons = []
        for pin in (board.BUTTON_A, board.BUTTON_B, board.BUTTON_C, board.BUTTON_D):
            switch = DigitalInOut(pin)
            switch.direction = Direction.INPUT
            switch.pull = Pull.UP
            self.buttons.append(switch)

    def play_tone(self, frequency, duration):
        """Automatically Enable/Disable the speaker and play
        a tone at the specified frequency for the specified duration

        """
        self._speaker_enable.value = True
        simpleio.tone(board.SPEAKER, frequency, duration)
        self._speaker_enable.value = False

    @property
    def battery(self):
        """Return the voltage of the battery"""
        return (self._batt_monitor.value / 65535.0) * 2.6 * 2

    @property
    def neopixel_disable(self):
        """
        Enable or disable the neopixels for power savings
        """
        return self._neopixel_disable.value

    @neopixel_disable.setter
    def neopixel_disable(self, value):
        self._neopixel_disable.value = value
