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

"""

import gc
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_magtag.network import Network
from adafruit_magtag.graphics import Graphics
from adafruit_magtag.peripherals import Peripherals

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MagTag.git"


class MagTag:
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
    :param status_neopixel: The pin for the status NeoPixel. Use ``board.NEOPIXEL`` for the on-board
                            NeoPixel. Defaults to ``None``, not the status LED
    :param json_transform: A function or a list of functions to call with the parsed JSON.
                           Changes and additions are permitted for the ``dict`` object.
    :param debug: Turn on debug print outs. Defaults to False.

    """

    # pylint: disable=too-many-instance-attributes, too-many-locals, too-many-branches, too-many-statements
    def __init__(
        self,
        *,
        url=None,
        headers=None,
        json_path=None,
        regexp_path=None,
        default_bg=0xFFFFFF,
        status_neopixel=None,
        json_transform=None,
        debug=False,
    ):

        self._debug = debug
        self.graphics = Graphics(
            default_bg=default_bg,
            auto_refresh=False,
            debug=debug,
        )
        self.display = self.graphics.display

        self.network = Network(
            status_neopixel=status_neopixel,
            extract_values=False,
            debug=debug,
        )

        self._url = None
        self.url = url
        self._headers = headers
        self._json_path = None
        self.json_path = json_path

        self._regexp_path = regexp_path

        self.splash = self.graphics.splash

        self.peripherals = Peripherals()

        # Add any JSON translators
        if json_transform:
            self.network.add_json_transform(json_transform)

        self._text = []
        self._text_color = []
        self._text_position = []
        self._text_wrap = []
        self._text_maxlen = []
        self._text_transform = []
        self._text_scale = []
        self._text_font = []
        self._text_line_spacing = []
        self._text_anchor_point = []

        gc.collect()

    # pylint: disable=too-many-arguments
    def add_text(
        self,
        text_position=(0, 0),
        text_font=terminalio.FONT,
        text_color=0x000000,
        text_wrap=0,
        text_maxlen=0,
        text_transform=None,
        text_scale=1,
        line_spacing=1.25,
        text_anchor_point=(0, 0.5),
    ):
        """
        Add text labels with settings

        :param str text_font: The path to your font file for your data text display.
        :param text_position: The position of your extracted text on the display in an (x, y) tuple.
                              Can be a list of tuples for when there's a list of json_paths, for
                              example.
        :param text_color: The color of the text, in 0xRRGGBB format. Can be a list of colors for
                           when there's multiple texts. Defaults to ``None``.
        :param text_wrap: When non-zero, the maximum number of characters on each line before text
                          is wrapped. (for long text data chunks). Defaults to 0, no wrapping.
        :param text_maxlen: The max length of the text. If non-zero, it will be truncated to this
                            length. Defaults to 0.
        :param text_transform: A function that will be called on the text before display
        :param int text_scale: The factor to scale the default size of the text by
        """
        if text_font is terminalio.FONT:
            self._text_font.append(text_font)
        else:
            self._text_font.append(bitmap_font.load_font(text_font))
        if not text_wrap:
            text_wrap = 0
        if not text_maxlen:
            text_maxlen = 0
        if not text_transform:
            text_transform = None
        if not isinstance(text_scale, (int, float)) or text_scale < 1:
            text_scale = 1
        if not isinstance(text_anchor_point, (tuple, list)):
            text_anchor_point = (0, 0.5)
        if not 0 <= text_anchor_point[0] <= 1 or not 0 <= text_anchor_point[1] <= 1:
            raise ValueError("Text anchor point values should be between 0 and 1.")
        text_scale = round(text_scale)
        gc.collect()

        if self._debug:
            print("Init text area")
        self._text.append(None)
        self._text_color.append(self.html_color_convert(text_color))
        self._text_position.append(text_position)
        self._text_wrap.append(text_wrap)
        self._text_maxlen.append(text_maxlen)
        self._text_transform.append(text_transform)
        self._text_scale.append(text_scale)
        self._text_line_spacing.append(line_spacing)
        self._text_anchor_point.append(text_anchor_point)

    # pylint: enable=too-many-arguments

    @staticmethod
    def html_color_convert(color):
        """Convert an HTML color code to an integer

        :param color: The color value to be converted

        """
        if isinstance(color, str):
            if color[0] == "#":
                color = color.lstrip("#")
            return int(color, 16)
        return color  # Return unconverted

    def set_headers(self, headers):
        """Set the headers used by fetch().

        :param headers: The new header dictionary

        """
        self._headers = headers

    def set_background(self, file_or_color, position=None):
        """The background image to a bitmap file.

        :param file_or_color: The filename of the chosen background image, or a hex color.

        """
        self.graphics.set_background(file_or_color, position)

    def preload_font(self, glyphs=None, index=0):
        # pylint: disable=line-too-long
        """Preload font.

        :param glyphs: The font glyphs to load. Defaults to ``None``, uses alphanumeric glyphs if
                       None.
        """
        # pylint: enable=line-too-long
        if not glyphs:
            glyphs = b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-!,. \"'?!"
        print("Preloading font glyphs:", glyphs)
        if self._text_font[index] is not terminalio.FONT:
            self._text_font[index].load_glyphs(glyphs)

    def set_text_color(self, color, index=0):
        """Update the text color, with indexing into our list of text boxes.

        :param int color: The color value to be used
        :param index: Defaults to 0.

        """
        if self._text[index]:
            color = self.html_color_convert(color)
            self._text_color[index] = color
            self._text[index].color = color

    def set_text(self, val, index=0, auto_refresh=True):
        """Display text, with indexing into our list of text boxes.

        :param str val: The text to be displayed
        :param index: Defaults to 0.

        """
        # Make sure at least a single label exists
        if not self._text:
            self.add_text()
        string = str(val)
        if self._text_maxlen[index]:
            if len(string) > self._text_maxlen[index]:
                # too long! shorten it
                string = string[: self._text_maxlen[index] - 3]
                string += "..."
        print("text index", self._text[index])
        index_in_splash = None

        if self._text[index] is not None:
            if self._debug:
                print("Replacing text area with :", string)
            index_in_splash = self.splash.index(self._text[index])
        elif self._debug:
            print("Creating text area with :", string)

        if len(string) > 0:
            self._text[index] = Label(
                self._text_font[index], text=string, scale=self._text_scale[index]
            )
            self._text[index].color = self._text_color[index]
            self._text[index].anchor_point = self._text_anchor_point[index]
            self._text[index].anchored_position = self._text_position[index]
            self._text[index].line_spacing = self._text_line_spacing[index]
        elif index_in_splash is not None:
            self._text[index] = None

        if index_in_splash is not None:
            if self._text[index] is not None:
                self.splash[index_in_splash] = self._text[index]
            else:
                del self.splash[index_in_splash]
        elif self._text[index] is not None:
            self.splash.append(self._text[index])
        if auto_refresh:
            self.refresh()

    def get_local_time(self, location=None):
        """Accessor function for get_local_time()"""
        return self.network.get_local_time(location=location)

    def push_to_io(self, feed_key, data):
        """Push data to an adafruit.io feed

        :param str feed_key: Name of feed key to push data to.
        :param data: data to send to feed

        """

        self.network.push_to_io(feed_key, data)

    def get_io_data(self, feed_key):
        """Return all values from the Adafruit IO Feed Data that matches the feed key

        :param str feed_key: Name of feed key to receive data from.

        """

        return self.network.get_io_data(feed_key)

    def get_io_feed(self, feed_key, detailed=False):
        """Return the Adafruit IO Feed that matches the feed key

        :param str feed_key: Name of feed key to match.
        :param bool detailed: Whether to return additional detailed information

        """
        return self.network.get_io_feed(feed_key, detailed)

    def get_io_group(self, group_key):
        """Return the Adafruit IO Group that matches the group key

        :param str group_key: Name of group key to match.

        """
        return self.network.get_io_group(group_key)

    def refresh(self):
        """
        Refresh the display
        """
        self.graphics.display.refresh()

    def fetch(self, refresh_url=None, timeout=10):
        """Fetch data from the url we initialized with, perfom any parsing,
        and display text or graphics. This function does pretty much everything
        Optionally update the URL

        :param str refresh_url: The overriding URL to fetch from. Defaults to ``None``.
        :param int timeout: The timeout period in seconds.

        """
        if refresh_url:
            self._url = refresh_url
        values = []

        values = self.network.fetch_data(
            self._url,
            headers=self._headers,
            json_path=self._json_path,
            regexp_path=self._regexp_path,
            timeout=timeout,
        )

        # fill out all the text blocks
        if self._text:
            for i in range(len(self._text)):
                string = None
                if self._text_transform[i]:
                    func = self._text_transform[i]
                    string = func(values[i])
                else:
                    try:
                        string = "{:,d}".format(int(values[i]))
                    except (TypeError, ValueError):
                        string = values[i]  # ok its a string
                if self._debug:
                    print("Drawing text", string)
                if self._text_wrap[i]:
                    if self._debug:
                        print("Wrapping text with length of", self._text_wrap[i])
                    lines = self.wrap_nicely(string, self._text_wrap[i])
                    string = "\n".join(lines)
                self.set_text(string, index=i, auto_refresh=False)
        self.refresh()
        if len(values) == 1:
            return values[0]
        return values

    # return a list of lines with wordwrapping
    @staticmethod
    def wrap_nicely(string, max_chars):
        """A helper that will return a list of lines with word-break wrapping.

        :param str string: The text to be wrapped.
        :param int max_chars: The maximum number of characters on a line before wrapping.

        """
        string = string.replace("\n", "").replace("\r", "")  # strip confusing newlines
        words = string.split(" ")
        the_lines = []
        the_line = ""
        for w in words:
            if len(the_line + " " + w) <= max_chars:
                the_line += " " + w
            else:
                the_lines.append(the_line)
                the_line = "" + w
        if the_line:  # last line remaining
            the_lines.append(the_line)
        # remove first space from first line:
        the_lines[0] = the_lines[0][1:]
        return the_lines

    @property
    def url(self):
        """
        Get or set the URL of your data source.
        """
        return self._json_path

    @url.setter
    def url(self, value):
        self._url = value
        if value and not self.network.uselocal:
            self.network.connect()
            # if self._debug:
            #    print("My IP address is", self.network.ip_address)

    @property
    def json_path(self):
        """
        Get or set the list of json traversal to get data out of. Can be list
        of lists for multiple data points.
        """
        return self._json_path

    @json_path.setter
    def json_path(self, value):
        if value:
            if isinstance(value[0], (list, tuple)):
                self._json_path = value
            else:
                self._json_path = (value,)
        else:
            self._json_path = None
