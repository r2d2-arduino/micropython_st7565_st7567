from machine import Pin, SPI
from st7565_spi import ST7565_SPI
import LibreBodoni20 as MY_FONT
from time import sleep
# Set pins here
DC  = 4 #rs
RST = 2 #reset
CS  = 1
spi = SPI( 2, baudrate = 2_000_000, polarity = 1, phase = 1, sck = Pin(35), mosi = Pin(36) )

ROTATION_0   = 0
ROTATION_90  = 1  
ROTATION_180 = 2
ROTATION_270 = 3

lcd = ST7565_SPI( spi, CS, DC, RST, ROTATION_0 )
lcd.set_contrast(36) # 63 - max
lcd.fill(0)
lcd.set_font(MY_FONT)
lcd.text("Default 8x8 font", 0, 0)
lcd.draw_text("Custom font:  LibreBodoni  size 20", 0, 10)

lcd.show()