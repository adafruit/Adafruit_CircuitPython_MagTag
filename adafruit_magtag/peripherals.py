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

* Adafruit's PortalBase library: https://github.com/adafruit/Adafruit_CircuitPython_PortalBase

"""

import board
import neopixel
import simpleio
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MagTag.git"


class Peripherals:
    """Peripherals Helper Class for the MagTag Library"""

    def __init__(self) -> None:
        # Neopixel power
        try:
            self._neopixel_disable = DigitalInOut(board.NEOPIXEL_POWER)
            self._neopixel_disable.direction = Direction.OUTPUT
            self._neopixel_disable.value = False
        except ValueError:
            self._neopixel_disable = None
        # Neopixels
        self.neopixels = neopixel.NeoPixel(board.NEOPIXEL, 4, brightness=0.3)

        # Battery Voltage
        self._batt_monitor = AnalogIn(board.BATTERY)

        # Speaker Enable
        self._speaker_enable = DigitalInOut(board.SPEAKER_ENABLE)
        self._speaker_enable.direction = Direction.OUTPUT
        self._speaker_enable.value = False

        # Light Sensor
        self._light = AnalogIn(board.LIGHT)

        # Buttons
        button_pins = [board.BUTTON_A, board.BUTTON_B, board.BUTTON_C, board.BUTTON_D]

        # Add BOOT0 as a button pin, only if it's defined.
        if hasattr(board, "BOOT0"):
            button_pins.append(board.BOOT0)

        self.buttons = []
        for pin in button_pins:
            switch = DigitalInOut(pin)
            switch.direction = Direction.INPUT
            switch.pull = Pull.UP
            self.buttons.append(switch)

    def play_tone(self, frequency: float, duration: float) -> None:
        """Automatically Enable/Disable the speaker and play
        a tone at the specified frequency for the specified duration
        It will attempt to play the sound up to 3 times in the case of
        an error.
        """
        if frequency < 0:
            raise ValueError("Negative frequencies are not allowed.")
        self._speaker_enable.value = True
        attempt = 0
        # Try up to 3 times to play the sound
        while attempt < 3:
            try:
                simpleio.tone(board.SPEAKER, frequency, duration)
                break
            except NameError:
                pass
            attempt += 1
        self._speaker_enable.value = False

    def deinit(self) -> None:
        """Call deinit to free all resources used by peripherals.
        You must call this function before you can use the peripheral
        pins for other purposes like PinAlarm with deep sleep."""
        self.neopixels.deinit()
        if self._neopixel_disable is not None:
            self._neopixel_disable.deinit()
        self._speaker_enable.deinit()
        for button in self.buttons:
            button.deinit()
        self._batt_monitor.deinit()
        self._light.deinit()

    @property
    def battery(self) -> float:
        """Return the voltage of the battery"""
        return (self._batt_monitor.value / 65535.0) * 3.3 * 2

    @property
    def neopixel_disable(self) -> bool:
        """
        Enable or disable the neopixels for power savings
        """
        if self._neopixel_disable is not None:
            return self._neopixel_disable.value
        return False

    @neopixel_disable.setter
    def neopixel_disable(self, value: bool) -> None:
        if self._neopixel_disable is not None:
            self._neopixel_disable.value = value

    @property
    def speaker_disable(self) -> bool:
        """
        Enable or disable the speaker for power savings
        """
        return not self._speaker_enable.value

    @speaker_disable.setter
    def speaker_disable(self, value: bool) -> None:
        self._speaker_enable.value = not value

    @property
    def button_a_pressed(self) -> bool:
        """
        Return whether Button A is pressed
        """
        return not self.buttons[0].value

    @property
    def button_b_pressed(self) -> bool:
        """
        Return whether Button B is pressed
        """
        return not self.buttons[1].value

    @property
    def button_c_pressed(self) -> bool:
        """
        Return whether Button C is pressed
        """
        return not self.buttons[2].value

    @property
    def button_d_pressed(self) -> bool:
        """
        Return whether Button D is pressed
        """
        return not self.buttons[3].value

    @property
    def any_button_pressed(self) -> bool:
        """
        Return whether any button is pressed
        """
        return False in [self.buttons[i].value for i in range(0, 4)]

    @property
    def light(self) -> int:
        """
        Return the value of the light sensor. The neopixel_disable property
        must be false to get a value.

        .. code-block:: python

            import time
            from adafruit_magtag.magtag import MagTag

            magtag = MagTag()

            while True:
                print(magtag.peripherals.light)
                time.sleep(0.01)

        """
        return self._light.value
