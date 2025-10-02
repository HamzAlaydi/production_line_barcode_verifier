"""
I2C LCD Driver for 16x2 LCD Display
Supports common I2C LCD backpacks (PCF8574, MCP23008, etc.)
"""

import time
import sys

# Try to import smbus, fall back to simulator on Windows
try:
    import smbus
    HAS_SMBUS = True
except ImportError:
    HAS_SMBUS = False
    print("Warning: smbus not available, using LCD simulator")

class I2CLCD:
    # LCD Commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # Flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # Flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # Flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # Flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    # Flags for backlight control
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    En = 0b00000100  # Enable bit
    Rw = 0b00000010  # Read/Write bit
    Rs = 0b00000001  # Register select bit

    def __init__(self, i2c_bus=1, i2c_addr=0x27, rows=2, cols=16):
        """
        Initialize I2C LCD
        
        Args:
            i2c_bus (int): I2C bus number (usually 1 for Raspberry Pi)
            i2c_addr (int): I2C address of LCD (common: 0x27, 0x3F)
            rows (int): Number of rows (usually 2)
            cols (int): Number of columns (usually 16)
        """
        self.rows = rows
        self.cols = cols
        self.i2c_addr = i2c_addr
        
        if HAS_SMBUS:
            try:
                self.bus = smbus.SMBus(i2c_bus)
            except Exception as e:
                print(f"Error initializing I2C bus: {e}")
                raise
        else:
            self.bus = None
            print("Using LCD simulator (no I2C hardware available)")
        
        self.backlight_state = self.LCD_BACKLIGHT
        
        # Initialize LCD
        self._init_display()
    
    def _init_display(self):
        """Initialize the LCD display"""
        # Wait for LCD to be ready
        time.sleep(0.05)
        
        # Initial sequence for 4-bit mode
        self._write4bits(0x03 << 4)
        time.sleep(0.0045)
        
        self._write4bits(0x03 << 4)
        time.sleep(0.0045)
        
        self._write4bits(0x03 << 4)
        time.sleep(0.00015)
        
        self._write4bits(0x02 << 4)
        
        # Set 4-bit mode, 2 lines, 5x8 font
        self.command(self.LCD_FUNCTIONSET | self.LCD_4BITMODE | self.LCD_2LINE | self.LCD_5x8DOTS)
        
        # Turn display on with no cursor or blinking
        self.command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF)
        
        # Clear display
        self.clear()
        
        # Set entry mode
        self.command(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT)
    
    def _write4bits(self, data):
        """Write 4 bits to LCD"""
        self._write_byte(data | self.backlight_state)
        self._pulse_enable(data | self.backlight_state)
    
    def _write_byte(self, data):
        """Write byte to I2C"""
        if self.bus:
            try:
                self.bus.write_byte(self.i2c_addr, data)
            except Exception as e:
                print(f"Error writing to I2C: {e}")
        else:
            # Simulator mode - just print the data
            print(f"LCD Simulator: Write byte 0x{data:02X}")
    
    def _pulse_enable(self, data):
        """Pulse the enable pin"""
        self._write_byte(data | self.En)
        time.sleep(0.0001)
        self._write_byte(data & ~self.En)
        time.sleep(0.0001)
    
    def command(self, cmd):
        """Send command to LCD"""
        self._write4bits(cmd & 0xF0)
        self._write4bits((cmd << 4) & 0xF0)
    
    def write_char(self, char):
        """Write a single character"""
        self._write4bits(self.Rs | (ord(char) & 0xF0))
        self._write4bits(self.Rs | ((ord(char) << 4) & 0xF0))
    
    def write_string(self, text):
        """Write a string to LCD"""
        for char in text:
            self.write_char(char)
    
    def set_cursor(self, row, col):
        """Set cursor position"""
        if row == 0:
            col |= 0x80
        elif row == 1:
            col |= 0xC0
        elif row == 2:
            col |= 0x94
        elif row == 3:
            col |= 0xD4
        
        self.command(col)
    
    def clear(self):
        """Clear the display"""
        self.command(self.LCD_CLEARDISPLAY)
        time.sleep(0.002)  # Clear command takes longer
    
    def home(self):
        """Return cursor to home position"""
        self.command(self.LCD_RETURNHOME)
        time.sleep(0.002)  # Home command takes longer
    
    def display_on(self):
        """Turn display on"""
        self.command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON)
    
    def display_off(self):
        """Turn display off"""
        self.command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYOFF)
    
    def backlight_on(self):
        """Turn backlight on"""
        self.backlight_state = self.LCD_BACKLIGHT
        self._write_byte(self.backlight_state)
    
    def backlight_off(self):
        """Turn backlight off"""
        self.backlight_state = self.LCD_NOBACKLIGHT
        self._write_byte(self.backlight_state)
    
    def print_message(self, line1="", line2=""):
        """Print a two-line message"""
        self.clear()
        if line1:
            self.set_cursor(0, 0)
            self.write_string(line1[:self.cols])
        if line2:
            self.set_cursor(1, 0)
            self.write_string(line2[:self.cols])
    
    def close(self):
        """Close I2C connection"""
        if self.bus:
            try:
                self.bus.close()
            except:
                pass
        else:
            print("LCD Simulator: Connection closed")
