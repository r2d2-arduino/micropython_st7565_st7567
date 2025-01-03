from machine import Pin, SPI
from st7565_spi import ST7565_SPI
from bitmaps import sun, suncloud, rain, rainlight, snowman
from time import sleep
# Set pins here
DC  = 4 #rs
RST = 2 #reset
CS  = 1
spi = SPI( 2, baudrate = 2_000_000, polarity = 1, phase = 1, sck = Pin(35), mosi = Pin(36) )

lcd = ST7565_SPI( spi, CS, DC, RST, 0 )
lcd.set_contrast(36) # 63 - max
  
bitmaps = [sun, suncloud, rain, rainlight, snowman]
size = 16
for i in range(len(bitmaps)):
    lcd.fill(0) # clear
    bitmap = bitmaps[i]
    for x in range(8):
        for y in range(4):
            lcd.draw_bitmap(bitmap, x * size, y * size, size, size)
    lcd.show()
    sleep(1)
    