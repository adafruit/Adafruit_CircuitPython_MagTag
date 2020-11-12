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
import audioio
import audiocore
import simpleio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MagTag.git"


class Graphics:
    """Peripherals Helper Class for the MagTag Library

    :param default_bg: The path to your default background image file or a hex color.
                       Defaults to 0x000000.
    :param debug: Turn on debug print outs. Defaults to False.

    """

    # pylint: disable=too-many-instance-attributes, too-many-locals, too-many-branches, too-many-statements
    def __init__(self):
        # Neopixels
        self.neopixels = neopixel.NeoPixel(board.NEOPIXEL, 4, brightness=0.3)
        pixel_power = DigitalInOut(board.NEOPIXEL_POWER)
        pixel_power.direction = Direction.OUTPUT
        pixel_power.value = False

        # Battery Voltage
        self._batt_monitor = AnalogIn(board.BATTERY)

        # Speaker Enable
        self._speaker_enable = DigitalInOut(board.SPEAKER_ENABLE)
        self._speaker_enable.direction = Direction.OUTPUT
        self._speaker_enable.value = False

        if hasattr(board, "SPEAKER"):
            self.audio = audioio.AudioOut(board.SPEAKER)
        else:
            raise AttributeError("Board does not have a builtin speaker!")

        # Buttons
        self.buttons = []
        for p in (board.BUTTON_A, board.BUTTON_B, board.BUTTON_C, board.BUTTON_D):
            switch = DigitalInOut(p)
            switch.direction = Direction.INPUT
            switch.pull = Pull.UP
            self.buttons.append(switch)

    def play_tone(self, frequency, duration):
        self._speaker_enable.value = True
        simpleio.tone(board.SPEAKER, frequency, duration)
        self._speaker_enable.value = False

    def play_wav_file(self, file_name, wait_to_finish=True):
        """Play a wav file.

        :param str file_name: The name of the wav file to play on the speaker.

        """
        wavfile = open(file_name, "rb")
        wavedata = audiocore.WaveFile(wavfile)
        self._speaker_enable.value = True
        self.audio.play(wavedata)
        if not wait_to_finish:
            return
        while self.audio.playing:
            pass
        wavfile.close()
        self._speaker_enable.value = False

    @property
    def battery(self):
        """Return the voltage of the battery"""
        return (self._batt_monitor.value / 65535.0) * 2.6 * 2
