# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_magtag.graphics`
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

import gc
from time import sleep
import board
import displayio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MagTag.git"


class Graphics:
    """Graphics Helper Class for the MagTag Library

    :param default_bg: The path to your default background image file or a hex color.
                       Defaults to 0x000000.
    :param bool auto_refresh: Automatically refresh the eInk after writing to displayio.
                              Defaults to True.
    :param debug: Turn on debug print outs. Defaults to False.

    """

    # pylint: disable=too-many-instance-attributes, too-many-locals, too-many-branches, too-many-statements
    def __init__(self, *, default_bg=0xFFFFFF, auto_refresh=True, debug=False):

        self._debug = debug
        if not hasattr(board, "DISPLAY"):
            import adafruit_il0373  # pylint: disable=import-outside-toplevel

            displayio.release_displays()
            display_bus = displayio.FourWire(
                board.SPI(),
                command=board.EPD_DC,
                chip_select=board.EPD_CS,
                reset=board.EPD_RESET,
                baudrate=1000000,
            )

            self.display = adafruit_il0373.IL0373(
                display_bus,
                width=296,
                height=128,
                rotation=270,
                black_bits_inverted=False,
                color_bits_inverted=False,
                grayscale=True,
                refresh_time=1,
                seconds_per_frame=5,
            )
        else:
            self.display = board.DISPLAY

        self.auto_refresh = auto_refresh

        if self._debug:
            print("Init display")
        self.splash = displayio.Group(max_size=15)
        self._qr_group = None
        if self._debug:
            print("Init background")
        self._bg_group = displayio.Group(max_size=1)
        self._bg_file = None
        self.splash.append(self._bg_group)
        self.display.show(self.splash)

        # set the default background
        if default_bg is not None:
            self.set_background(default_bg)

        gc.collect()

    def set_background(self, file_or_color, position=None):
        """The background image to a bitmap file.

        :param file_or_color: The filename of the chosen background image, or a hex color.
        :param tuple position: Optional x and y coordinates to place the background at.

        """
        print("Set background to", file_or_color)
        while self._bg_group:
            self._bg_group.pop()

        if not position:
            position = (0, 0)  # default in top corner

        if not file_or_color:
            return  # we're done, no background desired
        if self._bg_file:
            self._bg_file.close()
        if isinstance(file_or_color, str):  # its a filenme:
            self._bg_file = open(file_or_color, "rb")
            print("Displaying image file")
            background = displayio.OnDiskBitmap(self._bg_file)
            self._bg_sprite = displayio.TileGrid(
                background,
                pixel_shader=displayio.ColorConverter(),
                x=position[0],
                y=position[1],
            )
        elif isinstance(file_or_color, int):
            # Make a background color fill
            print("Displaying color")
            color_bitmap = displayio.Bitmap(self.display.width, self.display.height, 1)
            color_palette = displayio.Palette(1)
            color_palette[0] = file_or_color
            self._bg_sprite = displayio.TileGrid(
                color_bitmap,
                pixel_shader=color_palette,
                x=position[0],
                y=position[1],
            )
        else:
            raise RuntimeError("Unknown type of background")
        self._bg_group.append(self._bg_sprite)
        if self.auto_refresh:
            self.display.refresh()
        gc.collect()

    def qrcode(
        self, qr_data, *, qr_size=1, x=0, y=0, qr_color=0x000000
    ):  # pylint: disable=invalid-name
        """Display a QR code on the eInk

        :param qr_data: The data for the QR code.
        :param int qr_size: The scale of the QR code.
        :param x: The x position of upper left corner of the QR code on the display.
        :param y: The y position of upper left corner of the QR code on the display.

        """
        import adafruit_miniqr  # pylint: disable=import-outside-toplevel

        # generate the QR code
        for qrtype in range(1, 5):
            try:
                qrcode = adafruit_miniqr.QRCode(qr_type=qrtype)
                qrcode.add_data(qr_data)
                qrcode.make()
                break
            except RuntimeError:
                pass
                # print("Trying with larger code")
        else:
            raise RuntimeError("Could not make QR code")
        # monochrome (2 color) palette
        palette = displayio.Palette(2)
        palette[0] = 0xFFFFFF
        palette[1] = qr_color

        # pylint: disable=invalid-name
        # bitmap the size of the matrix, plus border, monochrome (2 colors)
        qr_bitmap = displayio.Bitmap(
            qrcode.matrix.width + 2, qrcode.matrix.height + 2, 2
        )
        for i in range(qr_bitmap.width * qr_bitmap.height):
            qr_bitmap[i] = 0

        # transcribe QR code into bitmap
        for xx in range(qrcode.matrix.width):
            for yy in range(qrcode.matrix.height):
                qr_bitmap[xx + 1, yy + 1] = 1 if qrcode.matrix[xx, yy] else 0

        # display the QR code
        qr_sprite = displayio.TileGrid(qr_bitmap, pixel_shader=palette)
        if self._qr_group:
            try:
                self._qr_group.pop()
            except IndexError:  # later test if empty
                pass
        else:
            self._qr_group = displayio.Group()
            self.splash.append(self._qr_group)
        self._qr_group.scale = qr_size
        self._qr_group.x = x
        self._qr_group.y = y
        self._qr_group.append(qr_sprite)
        if self.auto_refresh:
            self.display.refresh()
            sleep(5)
