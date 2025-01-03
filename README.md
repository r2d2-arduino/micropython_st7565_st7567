# micropython_st7565_st7567
Framebuffer display controller driver for st7565 and st7567 using SPI connection.

## File Structure:
* **examples/** - a set of examples for using the library ST7565_SPI
* **for_examples/** - files related to examples.
* **mpy/** - pre-compressed versions of libraries (mpy-cross v6.3). Use them if you don't have enough RAM.
* **tools/font_to_py.py** - Used to convert ttf font to py script. First of all, you need to install: `pip install freetype-py`. Then run a command similar to the example: `python font_to_py.py -x LibreBodoni-Bold.ttf 24 LibreBodoni24.py`. More details: https://github.com/peterhinch/micropython-font-to-py
* **st7565_spi.py** - Main library for st7565 & st7567 displays

## Minimum code to run:
```python
from machine import Pin, SPI
from st7565_spi import ST7565_SPI

DC  = 4 #rs
RST = 2 #reset
CS  = 1
spi = SPI( 2, baudrate = 2_000_000, polarity = 1, phase = 1)

lcd = ST7565_SPI( spi, CS, DC, RST )

lcd.set_contrast(36)
lcd.text("Micropython", 0, 0, 1)

lcd.show()
```

## Display functions:
* **set_contrast( value )** - Set contrast of display: 1..63
* **set_font( font )** - Set font for text. Converted font is used. See utils/font_to_py.py.
* **draw_text( text, x, y )** - Draw text on buffer
* **draw_bitmap( bitmap, x, y, width, height )** - Draw a bitmap (glyph) on buffer
* **load_bmp( filename, x = 0, y = 0 )** - Load monochromatic BMP image on buffer
* **show( )** - Displays the contents of the buffer on the screen

* **other functions** - see more on https://docs.micropython.org/en/latest/library/framebuf.html#module-framebuf

