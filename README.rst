Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-magtag/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/magtag/en/latest/
    :alt: Documentation Status

.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_MagTag/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_MagTag/actions
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

Helper library for the Adafruit MagTag.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Adafruit PortalBase <https://github.com/adafruit/Adafruit_CircuitPython_PortalBase>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_.


Usage Example
=============

.. code:: python

    # SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
    #
    # SPDX-License-Identifier: Unlicense
    import time
    import terminalio
    from adafruit_magtag.magtag import MagTag

    magtag = MagTag()

    magtag.add_text(
        text_font=terminalio.FONT,
        text_position=(
            50,
            (magtag.graphics.display.height // 2) - 1,
        ),
        text_scale=3,
    )

    magtag.set_text("Hello World")

    buttons = magtag.peripherals.buttons
    button_colors = ((255, 0, 0), (255, 150, 0), (0, 255, 255), (180, 0, 255))
    button_tones = (1047, 1318, 1568, 2093)
    timestamp = time.monotonic()

    while True:
        for i, b in enumerate(buttons):
            if not b.value:
                print("Button %c pressed" % chr((ord("A") + i)))
                magtag.peripherals.neopixel_disable = False
                magtag.peripherals.neopixels.fill(button_colors[i])
                magtag.peripherals.play_tone(button_tones[i], 0.25)
                break
        else:
            magtag.peripherals.neopixel_disable = True
        time.sleep(0.01)


Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/magtag/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_MagTag/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
