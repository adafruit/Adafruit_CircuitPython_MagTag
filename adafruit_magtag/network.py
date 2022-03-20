# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_magtag.network`
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

import neopixel
from adafruit_portalbase.network import NetworkBase
from adafruit_portalbase.wifi_esp32s2 import WiFi

try:
    from typing import Optional, Union
    import microcontroller
except ImportError:
    pass

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MagTag.git"


class Network(NetworkBase):
    """Class representing the Adafruit MagTag.

    :param status_neopixel: The pin for the status NeoPixel. Use ``board.NEOPIXEL`` for the on-board
                            NeoPixel. Defaults to ``None``, not the status LED
    :param bool extract_values: If true, single-length fetched values are automatically extracted
                                from lists and tuples. Defaults to ``True``.
    :param debug: Turn on debug print outs. Defaults to False.

    """

    # pylint: disable=too-many-instance-attributes, too-many-locals, too-many-branches, too-many-statements
    def __init__(
        self,
        *,
        status_neopixel: Optional[Union[microcontroller.Pin, neopixel.NeoPixel]] = None,
        extract_values: bool = True,
        debug: bool = False,
    ) -> None:
        if status_neopixel:
            if isinstance(status_neopixel, neopixel.NeoPixel):
                status_led = status_neopixel
            else:
                status_led = neopixel.NeoPixel(status_neopixel, 1, brightness=0.2)
        else:
            status_led = None
        super().__init__(
            WiFi(status_led=status_led),
            extract_values=extract_values,
            debug=debug,
        )

    @property
    def enabled(self) -> bool:
        """
        Get or Set whether the WiFi is enabled

        """
        return self._wifi.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._wifi.enabled = bool(value)
