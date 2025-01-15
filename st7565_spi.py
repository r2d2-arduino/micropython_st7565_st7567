"""
ST7565_SPI display library (with framebuffer) v 0.1.7

Display: ST7565
Connection: SPI
Color: 1-bit monochrome
Controllers: Esp32-family, RP2
 
Project path: https://github.com/r2d2-arduino/micropython_st7565_st7567
MIT License

Author: Arthur Derkach
"""
from machine import Pin
from time import sleep_ms
from framebuf import FrameBuffer, MONO_VLSB, MONO_HMSB, MONO_HLSB

# LCD Commands definition
CMD_DISPLAY_ON = const(0xAF)
CMD_DISPLAY_OFF = const(0xAE) 
CMD_SET_START_LINE = const(0x40)
CMD_SET_PAGE = const(0xB0)
CMD_COLUMN_HI = const(0x10)
CMD_COLUMN_LOW = const(0x00)
CMD_SET_ADC_NORMAL = const(0xA1)
CMD_SET_ADC_REVERSE = const(0xA0)
CMD_SET_COL_NORMAL = const(0xC8)
CMD_SET_COL_REVERSE = const(0xC0)
CMD_SET_DISPLAY_NORMAL = const(0xA6)
CMD_SET_DISPLAY_REVERSE = const(0xA7)
CMD_SET_ALLPX_ON = const(0xA5)
CMD_SET_ALLPX_NORMAL = const(0xA4)
CMD_SET_BIAS_9 = const(0xA2)
CMD_SET_BIAS_7 = const(0xA3)
CMD_DISPLAY_RESET = const(0xE2)
CMD_SET_POWER = const(0x28)
CMD_SET_RESISTOR_RATIO = const(0x20)
CMD_SET_VOLUME = const(0x81)

# Display parameters
DISPLAY_WIDTH = const(128)
DISPLAY_HEIGHT = const(64)
DISPLAY_CONTRAST = const(0x20)
DISPLAY_RESISTOR_RATIO = const(5)
DISPLAY_POWER_MODE = const(7)

ROTATION_0   = const(0)
ROTATION_90  = const(1)
ROTATION_180 = const(2)
ROTATION_270 = const(3)

class ST7565_SPI( FrameBuffer ):
    """ST7565 Display controller driver"""
    def __init__( self, spi, cs_pin, dc_pin, rst_pin, rotation = 0, shift = 4 ):
        """ Constructor
        Args
        spi  (object): SPI
        cs_pin   (int): CS pin number (Chip Select)
        dc_pin   (int): DC pin number (command/parameter mode)
        rst_pin  (int): RST pin number (Reset)
        rotation (int): Display rotation 0 = 0 degrees, 1 = 90, 2 = 180, 3 = 270
        shift    (int): Screen shift in pixels 
        """ 
        self.spi = spi
        self.rst = Pin( rst_pin, Pin.OUT )
        self.dc  = Pin( dc_pin, Pin.OUT )
        self.cs  = Pin( cs_pin, Pin.OUT )

        self.shift = shift
        self.offset = 0
        
        self.font = None
        self.text_wrap = False
        
        self.rotation = rotation

        if self.rotation & 1:
            self.width = DISPLAY_HEIGHT
            self.height = DISPLAY_WIDTH
            self.fb_format = MONO_HMSB
        else:
            self.width = DISPLAY_WIDTH
            self.height = DISPLAY_HEIGHT
            self.fb_format = MONO_VLSB

        # Buffer initialization
        self.buffsize = DISPLAY_WIDTH * DISPLAY_HEIGHT // 8
        self.buffer = bytearray( self.buffsize )
        super().__init__( self.buffer, self.width, self.height, self.fb_format )

        self.init()

    def init( self ):
        """ Initial display settings """
        self.reset()

        self.write_command( CMD_DISPLAY_OFF ) # Display off
        self.write_command( CMD_SET_BIAS_9 ) # Display drive voltage 1/9 bias
        self.write_command( CMD_SET_ADC_REVERSE ) # Reverse SEG
        self.write_command( CMD_SET_COL_NORMAL ) # Commmon mode normal direction
        self.write_command( CMD_SET_RESISTOR_RATIO + DISPLAY_RESISTOR_RATIO ) # V5 R ratio
        self.write_command( CMD_SET_VOLUME ) # Contrast
        self.write_command( DISPLAY_CONTRAST )  # Contrast value
        self.write_command( CMD_SET_POWER + DISPLAY_POWER_MODE )

        if self.rotation == 1: # 90 degrees
            self.set_horizontal_reverse(False)
            self.set_vertical_reverse(False)
            self.offset = self.shift            
        elif self.rotation == 2: # 180 degrees
            self.set_horizontal_reverse(True)
            self.set_vertical_reverse(False)
            self.offset = self.shift
        elif self.rotation == 3: # 270 degrees
            self.set_horizontal_reverse(True)
            self.set_vertical_reverse(True)
            self.offset = 0             
        else: # 0 degrees
            self.set_horizontal_reverse(False)
            self.set_vertical_reverse(True)
            self.offset = 0

        self.write_command( CMD_DISPLAY_ON ) # Display on

    def reset( self ):
        """ Display reset """
        self.rst.value( 0 )
        sleep_ms( 1 )
        self.rst.value( 1 )
        sleep_ms( 30 )

        self.write_command(CMD_DISPLAY_RESET)

    def write_command( self, cmd ):
        """ Sending a command to the display
        Args
        cmd (int): Command number, example: 0x2E
        """
        self.dc.value( 0 )
        self.cs.value( 0 )
        self.spi.write( bytearray( [ cmd ] ) )
        self.cs.value( 1 )

    def write_data( self, data ):
        """ Sending data to the display
        Args
        data (int): Data byte, example: 0xF8
        """
        self.dc.value( 1 )
        self.cs.value( 0 )
        self.spi.write( data )
        self.cs.value( 1 )

    def set_contrast( self, value ):
        """ Set contrast of display
        Args
        value (int): Value of contrast 1..63
        """
        if 0x1 <= value <= 0x3f:
            self.write_command( CMD_SET_VOLUME )
            self.write_command( value )
        else:
            print( "Incorrect contrast value", value )

    def set_dot_reverse( self, on = True ):
        """ Set reverse of dots on the display
        Args
        on (bool): 0 - Off, 1 - On
        """
        if on:
            self.write_command( CMD_SET_DISPLAY_REVERSE )
        else:
            self.write_command( CMD_SET_DISPLAY_NORMAL )

    def set_horizontal_reverse( self, on = True ): 
        """ Set reverse the display horizontally (refresh screen)
        Args
        on (bool): 0 - Off, 1 - On
        """
        if on:
            self.write_command( CMD_SET_COL_REVERSE )
        else:
            self.write_command( CMD_SET_COL_NORMAL )

    def set_vertical_reverse( self, on = True ):
        """ Set reverse the display verticaly
        Args
        on (bool): 0 - Off, 1 - On
        """
        if on:
            self.write_command( CMD_SET_ADC_REVERSE )
        else:
            self.write_command( CMD_SET_ADC_NORMAL )

    def show_all_pixels( self, on = True ):
        """ Show all pixels on display
        Args
        on (bool): 0 - Off, 1 - On
        """
        if on:
            self.write_command( CMD_SET_ALLPX_ON )
        else:
            self.write_command( CMD_SET_ALLPX_NORMAL )

    def set_font(self, font):
        """ Set font for text
        Args
        font (module): Font module generated by font_to_py.py
        """
        self.font = font
        
    def set_text_wrap(self, on = True):
        """ Set text wrapping """
        if on:
            self.text_wrap = True
        else:
            self.text_wrap = False         

    def draw_text(self, text, x, y, color = 1):
        """ Draw text on display
        Args
        x (int) : Start X position
        y (int) : Start Y position
        """
        x_start = x
        screen_height = self.height
        screen_width  = self.width

        font = self.font
        wrap = self.text_wrap

        if font == None:
            print("Font not set")
            return False

        for char in text:   
            glyph = font.get_ch(char)
            glyph_height = glyph[1]
            glyph_width  = glyph[2]
            
            if char == " ": # double size for space
                x += glyph_width            

            if wrap and (x + glyph_width > screen_width): # End of row
                x = x_start
                y += glyph_height

            #if y + glyph_height > screen_height: # End of screen
            #    break
            
            #fb = FrameBuffer(bytearray(glyph[0]), glyph_width, glyph_height, MONO_HLSB)
            #self.blit(fb, x, y, 1 - color)
            self.draw_bitmap(glyph, x, y, color)
            x += glyph_width

    @micropython.viper
    def draw_bitmap(self, bitmap, x:int, y:int, color:int):
        """ Draw a bitmap on display
        Args
        bitmap (bytes): Bitmap data
        x      (int): Start X position
        y      (int): Start Y position
        color  (int): Color 0 or 1
        """
        data   = ptr8(bitmap[0]) #memoryview to bitmap
        height = int(bitmap[1])
        width  = int(bitmap[2])
        
        i = 0
        for h in range(height):
            bit_len = 0
            while bit_len < width:
                byte = data[i]
                xpos = bit_len + x
                ypos = h + y                
                #Drawing pixels when bit = 1
                if (byte >> 7) & 1:
                    self.pixel(xpos    , ypos, color)
                if (byte >> 6) & 1:
                    self.pixel(xpos + 1, ypos, color)
                if (byte >> 5) & 1:
                    self.pixel(xpos + 2, ypos, color)
                if (byte >> 4) & 1:
                    self.pixel(xpos + 3, ypos, color)
                if (byte >> 3) & 1:
                    self.pixel(xpos + 4, ypos, color)
                if (byte >> 2) & 1:
                    self.pixel(xpos + 5, ypos, color)
                if (byte >> 1) & 1:
                    self.pixel(xpos + 6, ypos, color)
                if byte & 1:
                    self.pixel(xpos + 7, ypos, color)

                bit_len += 8
                i += 1

    def load_bmp( self, filename, x = 0, y = 0, color = 1 ):
        """ Load monochromatic BMP image on buffer
        Args
        filename (string): filename of image, example: "rain.bmp"
        x (int) : Start X position
        y (int) : Start Y position
        color  (int): Color 0 or 1
        """
        f = open(filename, 'rb')

        if f.read(2) == b'BM':  #header
            dummy    = f.read(8)
            offset   = int.from_bytes(f.read(4), 'little')
            dummy    = f.read(4) #hdrsize
            width    = int.from_bytes(f.read(4), 'little')
            height   = int.from_bytes(f.read(4), 'little')
            planes   = int.from_bytes(f.read(2), 'little')
            depth    = int.from_bytes(f.read(2), 'little')
            compress = int.from_bytes(f.read(4), 'little')

            if planes == 1 and depth == 1 and compress == 0: #compress method == uncompressed
                f.seek(offset)
                
                self.send_bmp_to_buffer( f, x, y, width, height, color)
            else:
                print("Unsupported planes, depth, compress:", planes, depth, compress )
                
        f.close()    
        
    @micropython.viper
    def send_bmp_to_buffer( self, f, x:int, y:int, width:int, height:int, color:int):
        """ Send bmp-file to buffer
        Args
        f (object File) : Image file
        x (int) : Start X position
        y (int) : Start Y position        
        width (int): Width of image frame
        height (int): Height of image frame
        color  (int): Color 0 or 1
        """        
        row_size = ((width + 31) // 32) * 4  # Aligning rows to 4 bytes
        total_size = height * row_size
        bitmap = bytearray(total_size)
        
        image_data = f.read(total_size)
        image_buffer = ptr8(image_data)
        
        block = width // 8
        for h in range(height):
            offset = block * h
            for w in range(block):
                if color == 1:
                    bitmap[total_size - 1 - offset - w] = image_buffer[offset + block - 1 - w] ^ 0xff
                else:
                    bitmap[total_size - 1 - offset - w] = image_buffer[offset + block - 1 - w]

        fb = FrameBuffer(bitmap, width, height, MONO_HLSB)
        self.blit(fb, x, y)
        
    def prepare_buffer( self ):
        ''' Buffer preparation '''
        if self.rotation & 1: # for 90 & 270 degrees
            buffer = bytearray( self.buffsize )
            # resort order of normal buffer
            rowsize = DISPLAY_HEIGHT // 8
            for i in range(DISPLAY_WIDTH):
                for j in range(rowsize):
                    buffer[i + j * DISPLAY_WIDTH] = self.buffer[i * rowsize + j]
        else: # for 0 & 180 degrees
            buffer = self.buffer

        return buffer

    def show( self ):
        ''' Displays the contents of the buffer on the screen '''
        buffer = self.prepare_buffer()

        self.cs.value( 0 )

        for page in range( 8 ):
            self.dc.value( 0 ) # Command mode         
            self.spi.write( bytearray( [ CMD_SET_START_LINE,
                                         CMD_SET_PAGE + page,
                                         ( CMD_COLUMN_HI  | (self.offset >> 4) ),
                                         ( CMD_COLUMN_LOW | self.offset ) ] ) )
            self.dc.value( 1 ) # Data mode
            self.spi.write( buffer[ DISPLAY_WIDTH * page: DISPLAY_WIDTH * ( page + 1 ) ] )

        self.cs.value( 1 )   