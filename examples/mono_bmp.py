from machine import Pin, SPI
from st7565_spi import ST7565_SPI
# Set pins here
DC  = 4 #rs
RST = 2 #reset
CS  = 1
spi = SPI( 2, baudrate = 2_000_000, polarity = 1, phase = 1, sck = Pin(36), mosi = Pin(35) )

lcd = ST7565_SPI( spi, CS, DC, RST, 0 )
lcd.set_contrast(36) # 63 - max
lcd.fill(0) # clear

lcd.load_bmp("images/tree128x64.bmp", 0, 0)

lcd.show()