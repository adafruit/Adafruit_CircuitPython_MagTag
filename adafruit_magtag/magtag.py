# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_magtag.magtag`
================================================================================

Helper library for the Adafruit MagTag.


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

import gc
import time
import board
from adafruit_portalbase import PortalBase
from adafruit_magtag.network import Network
from adafruit_magtag.graphics import Graphics
from adafruit_magtag.peripherals import Peripherals

try:
    from typing import Optional, Union, Sequence, Dict, Callable, Any
    import microcontroller
    import neopixel
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MagTag.git"


class MagTag(PortalBase):
    """Class representing the Adafruit MagTag.

    :param url: The URL of your data source. Defaults to ``None``.
    :param headers: The headers for authentication, typically used by Azure API's.
    :param json_path: The list of json traversal to get data out of. Can be list of lists for
                      multiple data points. Defaults to ``None`` to not use json.
    :param regexp_path: The list of regexp strings to get data out (use a single regexp group). Can
                        be list of regexps for multiple data points. Defaults to ``None`` to not
                        use regexp.
    :param default_bg: The path to your default background image file or a hex color.
                       Defaults to 0x000000.
    :param status_neopixel: The pin for the status NeoPixel. Use ``board.NEOPIXEL`` for the
                            on-board NeoPixel. Defaults to ``None``, to not use the status LED
    :param json_transform: A function or a list of functions to call with the parsed JSON.
                           Changes and additions are permitted for the ``dict`` object.
    :param rotation: Default rotation is landscape (270) but can be 0, 90, or 180 for
                     portrait/rotated
    :param debug: Turn on debug print outs. Defaults to False.

    """

    # pylint: disable=too-many-instance-attributes, too-many-locals, too-many-branches, too-many-statements
    def __init__(
        self,
        *,
        url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        json_path: Optional[Sequence[Any]] = None,
        regexp_path: Optional[Sequence[str]] = None,
        default_bg: Union[str, int] = 0xFFFFFF,
        status_neopixel: Optional[Union[microcontroller.Pin, neopixel.NeoPixel]] = None,
        json_transform: Union[Sequence[Callable], Callable] = None,
        rotation: int = 270,
        debug: bool = False,
    ) -> None:
        self.peripherals = Peripherals()

        if status_neopixel == board.NEOPIXEL:
            status_neopixel = self.peripherals.neopixels

        network = Network(
            status_neopixel=status_neopixel,
            extract_values=False,
            debug=debug,
        )

        graphics = Graphics(
            default_bg=default_bg,
            auto_refresh=False,
            rotation=rotation,
            debug=debug,
        )

        super().__init__(
            network,
            graphics,
            url=url,
            headers=headers,
            json_path=json_path,
            regexp_path=regexp_path,
            json_transform=json_transform,
            debug=debug,
        )

        gc.collect()

    def exit_and_deep_sleep(self, sleep_time: float) -> None:
        """
        Stops the current program and enters deep sleep. The program is restarted from the beginning
        after a certain period of time.

        See https://circuitpython.readthedocs.io/en/latest/shared-bindings/alarm/index.html for more
        details.

        Note: This function is for time based deep sleep only. If you want to use a PinAlarm
        to wake up from deep sleep you need to deinit() the pins and use the alarm module
        directly.

        :param float sleep_time: The amount of time to sleep in seconds

        """
        if self._alarm:
            self.peripherals.neopixel_disable = True
            self.peripherals.speaker_disable = True
        super().exit_and_deep_sleep(sleep_time)

    def enter_light_sleep(self, sleep_time: float) -> None:
        """
        Enter light sleep and resume the program after a certain period of time.

        See https://circuitpython.readthedocs.io/en/latest/shared-bindings/alarm/index.html for more
        details.

        :param float sleep_time: The amount of time to sleep in seconds

        """
        if self._alarm:
            neopixel_values = self.peripherals.neopixels
            neopixel_state = self.peripherals.neopixel_disable
            self.peripherals.neopixel_disable = True
            speaker_state = self.peripherals.speaker_disable
            self.peripherals.speaker_disable = True
        super().enter_light_sleep(sleep_time)
        self.peripherals.neopixel_disable = neopixel_state
        self.peripherals.speaker_disable = speaker_state
        for i in range(4):
            self.peripherals.neopixels[i] = neopixel_values[i]
        gc.collect()

    # pylint: disable=arguments-differ
    def set_text(self, val: str, index: int = 0, auto_refresh: bool = True) -> None:
        """Display text, with indexing into our list of text boxes.

        :param str val: The text to be displayed
        :param index: Defaults to 0.
        :param auto_refresh: Automatically refresh the display after setting the
                             text. Defaults to True

        """
        super().set_text(val, index)
        if auto_refresh:
            self.refresh()

    # pylint: enable=arguments-differ

    def _fetch_set_text(self, val: str, index: int = 0) -> None:
        self.set_text(val, index=index, auto_refresh=False)

    # pylint: disable=arguments-differ
    def fetch(
        self,
        refresh_url: Optional[str] = None,
        timeout: int = 10,
        auto_refresh: bool = True,
    ) -> Any:
        """Fetch data from the url we initialized with, perfom any parsing,
        and display text or graphics. This function does pretty much everything
        Optionally update the URL

        :param str refresh_url: The overriding URL to fetch from. Defaults to ``None``.
        :param int timeout: The timeout period in seconds.

        """

        values = super().fetch(refresh_url=refresh_url, timeout=timeout)
        if auto_refresh:
            self.refresh()
        return values

    # pylint: enable=arguments-differ

    def refresh(self) -> None:
        """
        Refresh the display
        """
        while True:
            try:
                self.graphics.display.refresh()
                return
            except RuntimeError:
                time.sleep(1)

    def remove_all_text(self, auto_refresh=True, clear_font_cache=False):
        """Remove all added text and labels. This version has an

        :param auto_refresh: Automatically refresh the display after setting the
                             text. Defaults to True.
        :param bool clear_font_cache: Clear the font cache. Defaults to False.
        """

        # Remove the labels
        for i in range(
            len(self._text)  # pylint: disable=access-member-before-definition
        ):
            self.set_text("", auto_refresh=False, index=i)
        # Remove the data
        self._text = []  # pylint: disable=attribute-defined-outside-init
        if clear_font_cache:
            self._fonts = {}  # pylint: disable=attribute-defined-outside-init
        if auto_refresh:
            self.refresh()
        gc.collect()
