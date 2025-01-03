from machine import Pin, SPI
from st7565_spi import ST7565_SPI
from time import sleep
# Set pins here
DC  = 4 #rs
RST = 2 #reset
CS  = 1
spi = SPI( 2, baudrate = 2_000_000, polarity = 1, phase = 1, sck = Pin(35), mosi = Pin(36) )

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

lcd = ST7565_SPI( spi, CS, DC, RST, 0 )
lcd.set_contrast(36) # 63 - max
lcd.fill(0) # clear

lcd.pixel(0, 63, 1)

lcd.ellipse(16, 20, 16, 16, 1, True)
lcd.ellipse(42, 46, 16, 16, 1)

lcd.rect(60, 4, 30, 30, 1, True)
lcd.rect(94, 32, 30, 30, 1)

for y in range(SCREEN_HEIGHT // 4):
    lcd.line(0, 0, SCREEN_WIDTH, y * 4 , 1)

lcd.show()
