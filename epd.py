import socket
from time import sleep

_DEBUG = False
# assumed serial interfaces for different platforms
_MAC = "/dev/cu.usbserial"
_LINUX = "/dev/ttyUSB0"

# insert path to your serial port here if known. (DEV for device)
_DEV = ""

if _DEV == "":
    # try to auto-determine what serial port to use
    # this is not guaranteed to work!
    from platform import system

    if system() == 'Linux':
        _DEV = _LINUX
    elif system() == 'Darwin':
        _DEV = _MAC
    else:
        _DEV = input('Define serial port for EPD connection (e.g. /dev/ttyUSB1 or just hit enter for none): ')


def _verify(cmd):
    result = 0
    cmd_split = [int(cmd[start:start + 2], 16) for start in range(0, len(cmd), 2)]
    for i in range(len(cmd_split)):
        result ^= cmd_split[i]
    return ("0" + (hex(result)[2:]))[-2:]


_soc = None
BAUD_RATE = 115200
_BAUD_RATE_DEFAULT = 115200
_BAUD_RATES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
_MAX_STRING_LEN = 1024 - 4

# frame segments
_FRAME_BEGIN = "A5"
_FRAME_END = "CC33C33C"

# colours
BLACK = "00"
DARK_GRAY = "01"
GRAY = "02"
WHITE = "03"

# commands
_CMD_HANDSHAKE = "00"  # handshake
_CMD_SET_BAUD = "01"  # set baud
_CMD_READ_BAUD = "02"  # read baud
_CMD_MEMORYMODE = "07"  # set memory mode
_CMD_STOPMODE = "08"  # enter stop mode
_CMD_UPDATE = "0A"  # update
_CMD_SCREEN_ROTATION = "0D"  # set screen rotation
_CMD_LOAD_FONT = "0E"  # copy font files from SD card to NandFlash.
# Font files include GBK32/48/64.FON
# 48MB allocated in NandFlash for fonts
# LED will flicker 3 times when starts and ends.
_CMD_LOAD_PIC = "0F"  # Import the image files from SD card to the NandFlash.
# LED will flicker 3 times when starts and ends.
# 80MB allocated in NandFlash for images
_CMD_SET_COLOR = "10"  # set colour
_CMD_SET_EN_FONT = "1E"  # set English font
_CMD_SET_CH_FONT = "1F"  # set Chinese font

_CMD_DRAW_PIXEL = "20"  # set pixel
_CMD_DRAW_LINE = "22"  # draw line
_CMD_FILL_RECT = "24"  # fill rectangle
_CMD_DRAW_RECT = "25"  # draw rectangle
_CMD_DRAW_CIRCLE = "26"  # draw circle
_CMD_FILL_CIRCLE = "27"  # fill circle
_CMD_DRAW_TRIANGLE = "28"  # draw triangle
_CMD_FILL_TRIANGLE = "29"  # fill triangle
_CMD_CLEAR = "2E"  # clear screen use back colour
_CMD_DRAW_STRING = "30"  # draw string
_CMD_DRAW_BITMAP = "70"  # draw bitmap

# FONT SIZE (32/48/64 dots)
GBK32 = "01"
GBK48 = "02"
GBK64 = "03"

ASCII32 = "01"
ASCII48 = "02"
ASCII64 = "03"

# Memory Mode
_MEM_NAND = "00"
_MEM_SD = "01"

# set screen rotation
_EPD_NORMAL = "00"  # screen normal
_EPD_INVERSION = "01"  # screen inversion

# command define
_cmd_handshake = _FRAME_BEGIN + "0009" + _CMD_HANDSHAKE + _FRAME_END
_cmd_handshake += _verify(_cmd_handshake)
_cmd_read_baud = _FRAME_BEGIN + "0009" + _CMD_READ_BAUD + _FRAME_END
_cmd_read_baud += _verify(_cmd_read_baud)
_cmd_stopmode = _FRAME_BEGIN + "0009" + _CMD_STOPMODE + _FRAME_END
_cmd_stopmode += _verify(_cmd_stopmode)
_cmd_update = _FRAME_BEGIN + "0009" + _CMD_UPDATE + _FRAME_END
_cmd_update += _verify(_cmd_update)
_cmd_clear = _FRAME_BEGIN + "0009" + _CMD_CLEAR + _FRAME_END
_cmd_clear += _verify(_cmd_clear)
_cmd_import_font = _FRAME_BEGIN + "0009" + _CMD_LOAD_FONT + _FRAME_END
_cmd_import_font += _verify(_cmd_import_font)
_cmd_import_pic = _FRAME_BEGIN + "0009" + _CMD_LOAD_PIC + _FRAME_END
_cmd_import_pic += _verify(_cmd_import_pic)
_cmd_use_nand = _FRAME_BEGIN + "000A" + _CMD_MEMORYMODE + _MEM_NAND + _FRAME_END
_cmd_use_nand += _verify(_cmd_use_nand)
_cmd_use_sd = _FRAME_BEGIN + "000A" + _CMD_MEMORYMODE + _MEM_SD + _FRAME_END
_cmd_use_sd += _verify(_cmd_use_sd)

# vector 7 segment LCD digits (calculator-like digits)
#
# 34 points that make up all the stokes
# origin is top-left corner
# see ePaperDisplay/docs/LCD_digit_font_design.svg for reference

_LCD_DIGIT_WIDTH = 120
_LCD_DIGIT_HEIGHT = 220
_LCD_SPACING = 20  # space between 2 adjacent digits

_LPBG0 = [0, 0]  # two points defining the background area of each digit
_LPBG1 = [_LCD_DIGIT_WIDTH, _LCD_DIGIT_HEIGHT]

_LP01 = (20, 0)
_LP02 = (100, 0)
_LP03 = (10, 10)
_LP04 = (110, 10)
_LP05 = (0, 20)
_LP06 = (120, 20)
_LP07 = (30, 30)
_LP08 = (90, 30)
_LP09 = (45, 60)
_LP10 = (75, 60)  # unused
_LP11 = (45, 90)  # unused
_LP12 = (75, 90)
_LP13 = (0, 95)
_LP14 = (30, 95)
_LP15 = (90, 95)
_LP16 = (120, 95)
_LP17 = (15, 110)
_LP18 = (105, 110)
_LP19 = (0, 125)
_LP20 = (30, 125)
_LP21 = (90, 125)
_LP22 = (120, 125)
_LP23 = (45, 130)
_LP24 = (75, 130)  # unused
_LP25 = (45, 160)  # unused
_LP26 = (75, 160)
_LP27 = (30, 190)
_LP28 = (90, 190)
_LP29 = (0, 200)
_LP30 = (120, 200)
_LP31 = (10, 210)
_LP32 = (110, 210)
_LP33 = (20, 220)
_LP34 = (100, 220)

#  ---               H1
# | . |           V1 C1 V2
# ><---><         T1T2H2T3T4
# | . |           V3 C2 V4
#  ---               H3
#
# each horizontal/vertical stroke is drawn with 4 filled triangles
# each dot of colon is a filled rectangle
# each triangle filler beside H2 is a filled triangle
# H2 overlaps with T2 and T3

_H1 = [(_LP01, _LP07, _LP03), (_LP01, _LP07, _LP02), (_LP02, _LP08, _LP04), (_LP02, _LP08, _LP07)]
_H2 = [(_LP14, _LP20, _LP17), (_LP14, _LP20, _LP15), (_LP15, _LP21, _LP20), (_LP15, _LP21, _LP18)]
_H3 = [(_LP27, _LP33, _LP31), (_LP27, _LP33, _LP28), (_LP28, _LP34, _LP33), (_LP28, _LP34, _LP32)]
_V1 = [(_LP05, _LP07, _LP03), (_LP05, _LP07, _LP13), (_LP13, _LP14, _LP07), (_LP13, _LP14, _LP17)]
_V2 = [(_LP08, _LP06, _LP04), (_LP08, _LP06, _LP15), (_LP15, _LP16, _LP06), (_LP15, _LP16, _LP18)]
_V3 = [(_LP19, _LP20, _LP17), (_LP19, _LP20, _LP29), (_LP29, _LP27, _LP20), (_LP29, _LP27, _LP31)]
_V4 = [(_LP21, _LP22, _LP18), (_LP21, _LP22, _LP28), (_LP28, _LP30, _LP22), (_LP28, _LP30, _LP32)]
_C1 = [(_LP09, _LP12)]
_C2 = [(_LP23, _LP26)]
_T1 = [(_LP13, _LP19, _LP17)]
_T2 = [(_LP14, _LP20, _LP17)]
_T3 = [(_LP15, _LP21, _LP18)]
_T4 = [(_LP16, _LP22, _LP18)]

_LCD_0 = _H1 + _H3 + _V1 + _V2 + _V3 + _V4 + _T1 + _T2 + _T3 + _T4
_LCD_1 = _V2 + _V4 + _T3 + _T4
_LCD_2 = _H1 + _H2 + _H3 + _V2 + _V3
_LCD_3 = _H1 + _H2 + _H3 + _V2 + _V4 + _T4
_LCD_4 = _H2 + _V1 + _V2 + _V4 + _T4
_LCD_5 = _H1 + _H2 + _H3 + _V1 + _V4
_LCD_6 = _H1 + _H2 + _H3 + _V1 + _V3 + _V4 + _T1
_LCD_7 = _H1 + _V1 + _V2 + _V4 + _T3 + _T4
_LCD_8 = _H1 + _H2 + _H3 + _V1 + _V2 + _V3 + _V4 + _T1 + _T4
_LCD_9 = _H1 + _H2 + _H3 + _V1 + _V2 + _V4 + _T4
_LCD_COLON = _C1 + _C2
_LCD_BG = _LPBG0 + _LPBG1

# for quick retrieval using target digit as index
_LCD_DIGITS = [_LCD_0, _LCD_1, _LCD_2, _LCD_3, _LCD_4, _LCD_5, _LCD_6, _LCD_7, _LCD_8, _LCD_9]

# some default LCD digit sizes/scales
LCD_SM = 0.33  # approx. 17 digits over entire width
LCD_MD = 0.63  # approx. 9 digits over entire width
LCD_LG = 1.15  # approx. 5 digits over entire width


# NOTE:
#   the EPD does not handle too many triangles at a time
#   if it does not display the digits sent, there are too many
#   send over a few segments until I fix it

def _lcd_digit(x, y, d, scale=LCD_MD):
    # draw digit over existing image with transparency like other hollow shapes
    if d == ':':
        for rect in _LCD_COLON:
            (x0, y0), (x1, y1) = rect
            epd_fill_rect(int(scale * x0 + x), int(scale * y0 + y),
                          int(scale * x1 + x), int(scale * y1 + y))
    elif d in [str(s) for s in range(0, 10)]:
        for tri in _LCD_DIGITS[int(d)]:
            (x0, y0), (x1, y1), (x2, y2) = tri
            epd_fill_triangle(int(scale * x0 + x), int(scale * y0 + y),
                              int(scale * x1 + x), int(scale * y1 + y),
                              int(scale * x2 + x), int(scale * y2 + y))
    else:
        print("'%s' is not a digit or colon. Leaving it blank." % d)


def epd_lcd_digits(x, y, digits, scale=LCD_MD):
    if digits == '':
        return
    # for now, the input is expected to be a sequence of digits
    # or a time with colon as the separator, e.g. 12:48

    # fill all background area including spacing with white rectangle
    epd_set_color(WHITE, WHITE)
    epd_fill_rect(x, y,
                  int(x + (len(digits) - 1) * (_LCD_DIGIT_WIDTH + _LCD_SPACING) * scale + _LCD_DIGIT_WIDTH * scale),
                  int(y + _LCD_DIGIT_HEIGHT * scale))
    epd_set_color(BLACK, WHITE)

    count = 0
    for d in digits:
        _lcd_digit(int(x + count * scale * (_LCD_DIGIT_WIDTH + _LCD_SPACING)), y, d, scale)
        count += 1
        if count % 5 == 0:
            # force an update every 5 digits to avoid a no-display
            # due to too many triangles filling up EPD's buffer
            epd_update()
            sleep(2)
    if count % 5 != 0:
        # so we don't refresh twice if we just did it by the last digit in the loop
        epd_update()


# lightweight (in terms of drawing) and scalable block digits
# in contrast to the nice LCD digits which require drawing many
# triangles for each digit, these simple digits only require
# up to 3 rectangles (6x coordinates) per digit
#
# see ePaperDisplay/docs/block_digit_font_design.svg for reference
# a 3x5 rectangle in FG colour is drawn and up to 2 areas are
# 'subtracted' with BG colour to make a digit, e.g.
#
# ### ### ### ### ### # # ### ###  #  ###
# # # # #   # #   #   # #   #   #  #  # #  #
# ### ###   # ### ### ### ### ###  #  # #
#   # # #   # # #   #   #   # #    #  # #  #
# ### ###   # ### ###   # ### ###  #  ###

BLOCK_DIGIT_WIDTH = 30
BLOCK_DIGIT_HEIGHT = 50
BLOCK_DIGIT_SPACING = 5  # space between 2 block digits

BP01 = (0, 0)
BP02 = (10, 0)
BP03 = (20, 0)
BP04 = (0, 10)
BP05 = (10, 10)
BP06 = (20, 20)
BP07 = (30, 20)
BP08 = (0, 30)
BP09 = (10, 30)
BP10 = (20, 40)
BP11 = (30, 40)
BP12 = (10, 50)
BP13 = (20, 50)
BP14 = (30, 50)

BLK_0 = [(BP05, BP10)]
BLK_1 = [(BP01, BP12), (BP03, BP14)]
BLK_2 = [(BP04, BP06), (BP09, BP11)]
BLK_3 = [(BP04, BP06), (BP08, BP10)]
BLK_4 = [(BP02, BP06), (BP08, BP13)]
BLK_5 = [(BP05, BP07), (BP08, BP10)]
BLK_6 = [(BP02, BP07), (BP09, BP10)]
BLK_7 = [(BP04, BP13)]
BLK_8 = [(BP05, BP06), (BP09, BP10)]
BLK_9 = [(BP05, BP06), (BP08, BP10)]
BLK_COLON = BLK_8  # invert FG/BG colour
BLK_BG = (BP01, BP14)

# for quick retrieval using target digit as index
BLK_DIGITS = [BLK_0, BLK_1, BLK_2, BLK_3, BLK_4, BLK_5, BLK_6, BLK_7, BLK_8, BLK_9]

# some default LCD digit sizes/scales
BLOCK_SM = 1.0  # approx. 23 digits over entire width
BLOCK_MD = 2.5  # approx. 9 digits over entire width
BLOCK_LG = 4.65  # approx. 5 digits over entire width


def block_digit(x, y, d, scale=BLOCK_SM):
    (x0, y0), (x1, y1) = BLK_BG

    if d == ':':
        epd_set_color(WHITE, WHITE)
        epd_fill_rect(int(scale * x0 + x), int(scale * y0 + y),
                      int(scale * x1 + x), int(scale * y1 + y))
        epd_set_color(BLACK, WHITE)
        d = '8'
    elif d in [str(s) for s in range(0, 10)]:
        epd_set_color(BLACK, WHITE)
        epd_fill_rect(int(scale * x0 + x), int(scale * y0 + y),
                      int(scale * x1 + x), int(scale * y1 + y))
        epd_set_color(WHITE, WHITE)
    else:
        print("'%s' is not a digit or colon. Leaving it blank." % d)
        return

    for rect in BLK_DIGITS[int(d)]:
        (x0, y0), (x1, y1) = rect
        epd_fill_rect(int(scale * x0 + x), int(scale * y0 + y),
                      int(scale * x1 + x), int(scale * y1 + y))
    epd_set_color(BLACK, WHITE)


def epd_block_digits(x, y, digits, scale=BLOCK_SM):
    if digits == '':
        return
    # fill all background area including spacing with white rectangle
    epd_set_color(WHITE, WHITE)
    epd_fill_rect(x, y,
                  int(x + (len(digits) - 1) * (
                          BLOCK_DIGIT_SPACING + BLOCK_DIGIT_WIDTH) * scale + BLOCK_DIGIT_WIDTH * scale),
                  int(y + BLOCK_DIGIT_HEIGHT * scale))
    count = 0
    for d in digits:
        block_digit(int(x + count * scale * (BLOCK_DIGIT_SPACING + BLOCK_DIGIT_WIDTH)), y, d, scale)
        count += 1


# ASCII string to Hex string. e.g. "World" => "576F726C64"
def a2h(string):
    hex_str = ""
    for c in string:
        hex_str = hex_str + hex(ord(c))[-2:]
    return hex_str + "00"  # append "00" to string as required


def send(cmd):
    if soc is None:
        print(">> EPD not connected. Try epd_connect()")
    elif type(soc) == socket.socket(socket.AF_INET, socket.SOCK_STREAM):
        soc.send(bytes.fromhex(cmd))
    else:
        soc.write(bytes.fromhex(cmd))
        if _DEBUG:
            print(">", soc.readline())


def epd_connect(rate=BAUD_RATE):
    global soc, BAUD_RATE
    import serial
    try:
        soc = serial.Serial(
            port=_DEV,
            baudrate=rate,
            timeout=1
        )
        print("> EPD connected via serial port")
        if BAUD_RATE != rate:
            BAUD_RATE = rate
            print("> Client-side BAUD_RATE is now %d" % rate)
        return
    except:
        print(">> Unable to connect to USB serial port", _DEV)
        soc = None


def epd_debug(v):
    """Print responses of requests"""
    global _DEBUG
    if v:
        _DEBUG = True
    else:
        _DEBUG = False


def epd_handshake():
    print("> EPD handshake")
    send("A5000900CC33C33CAC")
    # send(_cmd_handshake)


def epd_disconnect():
    global soc
    if soc is not None:
        soc.close()
    print("> EPD connection closed.")


def epd_update():
    send(_cmd_update)


def epd_clear():
    send(_cmd_clear)
    epd_update()


def reset_baud_rate():
    BAUD_RATE = _BAUD_RATE_DEFAULT


def epd_set_baud(baud_rate):  # 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200
    global BAUD_RATE
    if type(soc) == socket.socket(socket.AF_INET, socket.SOCK_STREAM):
        print("> Do not change baud rate when using WiFi relay, or the WiFi module and the EPD will have different baud"
              " rates and stop understanding each other.")
        return
    if baud_rate in _BAUD_RATES:
        hex_rate = ('0000000' + hex(baud_rate)[2:])[-8:]
        _cmd = _FRAME_BEGIN + "000D" + _CMD_SET_BAUD + hex_rate + _FRAME_END
        send(_cmd)
        print("> Releasing current serial connection...")
        epd_disconnect()
        print("> Waiting for the EPD to re-initiate with new baud rate...")
        sleep(5)
        print("> Reconnecting with baud rate %d ..." % baud_rate)
        epd_connect(rate=baud_rate)
    else:
        print("> Invalid baud rate. Pick from", _BAUD_RATES)


def epd_read_baud():
    print("> EPD baud rate:")
    send(_cmd_read_baud)


def epd_set_memory_nand():
    send(_cmd_use_nand)


def epd_set_memory_sd():
    send(_cmd_use_sd)


def epd_sleep():
    print("> EPD sleep")
    send(_cmd_stopmode)


def epd_screen_normal():
    _cmd = _FRAME_BEGIN + "000A" + _CMD_SCREEN_ROTATION + _EPD_NORMAL + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)
    epd_update()


def epd_screen_invert():
    _cmd = _FRAME_BEGIN + "000A" + _CMD_SCREEN_ROTATION + _EPD_INVERSION + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)
    epd_update()


def epd_import_font():
    send(_cmd_import_font)


def epd_import_pic():
    send(_cmd_import_pic)


def epd_set_color(fg, bg):
    if fg in [BLACK, DARK_GRAY, GRAY, WHITE] and bg in [BLACK, DARK_GRAY, GRAY, WHITE]:
        _cmd = _FRAME_BEGIN + "000B" + _CMD_SET_COLOR + fg + bg + _FRAME_END
        _cmd += _verify(_cmd)
        send(_cmd)


def epd_set_en_font(en_size):
    _cmd = _FRAME_BEGIN + "000A" + _CMD_SET_EN_FONT + en_size + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_set_ch_font(ch_size):
    _cmd = _FRAME_BEGIN + "000A" + _CMD_SET_CH_FONT + ch_size + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_pixel(x0, y0):
    print("> EPD Pixel")
    hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
    hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]

    _cmd = _FRAME_BEGIN + "000D" + _CMD_DRAW_PIXEL + hex_x0 + hex_y0 + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_line(x0, y0, x1, y1):
    hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
    hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
    hex_x1 = "0" + str(((x1 >> 8) & 0xFF)) + ("0" + str(hex(x1 & 0xFF)[2:]))[-2:]
    hex_y1 = "0" + str(((y1 >> 8) & 0xFF)) + ("0" + str(hex(y1 & 0xFF)[2:]))[-2:]
    _cmd = _FRAME_BEGIN + "0011" + _CMD_DRAW_LINE + hex_x0 + hex_y0 + hex_x1 + hex_y1 + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_rect(x0, y0, x1, y1):
    hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
    hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
    hex_x1 = "0" + str(((x1 >> 8) & 0xFF)) + ("0" + str(hex(x1 & 0xFF)[2:]))[-2:]
    hex_y1 = "0" + str(((y1 >> 8) & 0xFF)) + ("0" + str(hex(y1 & 0xFF)[2:]))[-2:]
    _cmd = _FRAME_BEGIN + "0011" + _CMD_DRAW_RECT + hex_x0 + hex_y0 + hex_x1 + hex_y1 + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_fill_rect(x0, y0, x1, y1):
    hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
    hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
    hex_x1 = "0" + str(((x1 >> 8) & 0xFF)) + ("0" + str(hex(x1 & 0xFF)[2:]))[-2:]
    hex_y1 = "0" + str(((y1 >> 8) & 0xFF)) + ("0" + str(hex(y1 & 0xFF)[2:]))[-2:]
    _cmd = _FRAME_BEGIN + "0011" + _CMD_FILL_RECT + hex_x0 + hex_y0 + hex_x1 + hex_y1 + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_circle(x0, y0, r):
    hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
    hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
    hex_r = "0" + str(((r >> 8) & 0xFF)) + ("0" + str(hex(r & 0xFF)[2:]))[-2:]
    _cmd = _FRAME_BEGIN + "000F" + _CMD_DRAW_CIRCLE + hex_x0 + hex_y0 + hex_r + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_fill_circle(x0, y0, r):
    hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
    hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
    hex_r = "0" + str(((r >> 8) & 0xFF)) + ("0" + str(hex(r & 0xFF)[2:]))[-2:]
    _cmd = _FRAME_BEGIN + "000F" + _CMD_FILL_CIRCLE + hex_x0 + hex_y0 + hex_r + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_triangle(x0, y0, x1, y1, x2, y2):
    hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
    hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
    hex_x1 = "0" + str(((x1 >> 8) & 0xFF)) + ("0" + str(hex(x1 & 0xFF)[2:]))[-2:]
    hex_y1 = "0" + str(((y1 >> 8) & 0xFF)) + ("0" + str(hex(y1 & 0xFF)[2:]))[-2:]
    hex_x2 = "0" + str(((x2 >> 8) & 0xFF)) + ("0" + str(hex(x2 & 0xFF)[2:]))[-2:]
    hex_y2 = "0" + str(((y2 >> 8) & 0xFF)) + ("0" + str(hex(y2 & 0xFF)[2:]))[-2:]
    _cmd = _FRAME_BEGIN + "0015" + _CMD_DRAW_TRIANGLE + hex_x0 + hex_y0 + hex_x1 + hex_y1 + hex_x2 + hex_y2 + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_fill_triangle(x0, y0, x1, y1, x2, y2):
    hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
    hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
    hex_x1 = "0" + str(((x1 >> 8) & 0xFF)) + ("0" + str(hex(x1 & 0xFF)[2:]))[-2:]
    hex_y1 = "0" + str(((y1 >> 8) & 0xFF)) + ("0" + str(hex(y1 & 0xFF)[2:]))[-2:]
    hex_x2 = "0" + str(((x2 >> 8) & 0xFF)) + ("0" + str(hex(x2 & 0xFF)[2:]))[-2:]
    hex_y2 = "0" + str(((y2 >> 8) & 0xFF)) + ("0" + str(hex(y2 & 0xFF)[2:]))[-2:]
    _cmd = _FRAME_BEGIN + "0015" + _CMD_FILL_TRIANGLE + hex_x0 + hex_y0 + hex_x1 + hex_y1 + hex_x2 + hex_y2 + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def epd_ascii(x0, y0, txt):
    if len(txt) <= _MAX_STRING_LEN:
        size = len(txt) + 14
        hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
        hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
        hex_txt = a2h(txt)
        hex_size = "0" + str(((size >> 8) & 0xFF)) + ("0" + str(hex(size & 0xFF)[2:]))[-2:]
        _cmd = _FRAME_BEGIN + hex_size + _CMD_DRAW_STRING + hex_x0 + hex_y0 + hex_txt + _FRAME_END
        _cmd += _verify(_cmd)
        send(_cmd)
    else:
        print("> Too many characters. Max length =", _MAX_STRING_LEN)


# Not tested, not modified
def epd_chinese(x0, y0, gb2312_hex):  # "hello world" in Chinese: C4E3 BAC3 CAC0 BDE7
    gb2312_hex = gb2312_hex.replace(" ", "") + "00"
    if len(gb2312_hex) / 2 <= _MAX_STRING_LEN:
        hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
        hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
        hex_size = ("000" + hex(13 + len(gb2312_hex) / 2)[2:])[-4:]
        _cmd = _FRAME_BEGIN + hex_size + _CMD_DRAW_STRING + hex_x0 + hex_y0 + gb2312_hex + _FRAME_END
        _cmd += _verify(_cmd)
        send(_cmd)
    else:
        print("> Too many characters. Max length =", _MAX_STRING_LEN)


def epd_bitmap(x0, y0, name):  # file names must be all capitals and <10 letters including '.'
    size = len(name) + 14
    hex_x0 = "0" + str(((x0 >> 8) & 0xFF)) + ("0" + str(hex(x0 & 0xFF)[2:]))[-2:]
    hex_y0 = "0" + str(((y0 >> 8) & 0xFF)) + ("0" + str(hex(y0 & 0xFF)[2:]))[-2:]
    hex_name = a2h(name)
    hex_size = "0" + str(((size >> 8) & 0xFF)) + ("0" + str(hex(size & 0xFF)[2:]))[-2:]
    _cmd = _FRAME_BEGIN + hex_size + _CMD_DRAW_BITMAP + hex_x0 + hex_y0 + hex_name + _FRAME_END
    _cmd += _verify(_cmd)
    send(_cmd)


def get_width(txt, size=32):  # size in [32,48,64]
    # characters in size 32 are manually measured so their
    # widths are accurate. font size 48 and 64 are assumed
    # widths based on simple calculation for rough estimates.
    if size not in [32, 48, 64]:
        print("> Error: size must be in [32,48,64]")
        return
    width = 0
    for c in txt:
        if c in "'":
            width += 5
        elif c in "ijl|":
            width += 6
        elif c in "f":
            width += 7
        elif c in " It![].,;:/\\":
            width += 8
        elif c in "r-`(){}":
            width += 9
        elif c in '"':
            width += 10
        elif c in "*":
            width += 11
        elif c in "x^":
            width += 12
        elif c in "Jvz":
            width += 13
        elif c in "cksy":
            width += 14
        elif c in "Labdeghnopqu$#?_1234567890":
            width += 15
        elif c in "T+<>=~":
            width += 16
        elif c in "FPVXZ":
            width += 17
        elif c in "ABEKSY&":
            width += 18
        elif c in "HNUw":
            width += 19
        elif c in "CDR":
            width += 20
        elif c in "GOQ":
            width += 21
        elif c in "m":
            width += 22
        elif c in "M":
            width += 23
        elif c in "%":
            width += 24
        elif c in "@":
            width += 27
        elif c in "W":
            width += 28
        else:  # non-ascii or Chinese character
            width += 32
    return int(width * (size / 32.0))


def wrap_ascii(x, y, txt, limit=800, size=32):  # does not work well with size 48 or 64
    DELIMITER = " "
    DELIMITER_WIDTH = get_width(DELIMITER, size)
    WHITE_WIDTH = get_width(" ", size)
    lines = txt.strip().split("\n")
    y_offset = 0
    for l in lines:
        words = l.strip().split(DELIMITER)
        line = ""
        line_width = 0
        for word in words:
            word_width = get_width(word, size)
            if line_width + DELIMITER_WIDTH + word_width <= limit:
                line += DELIMITER + word
                line_width += DELIMITER_WIDTH + word_width
            else:
                # clear line up to the whole line width
                epd_set_color(WHITE, WHITE)
                epd_fill_rect(x, y + y_offset, x + limit, y + y_offset + size)
                epd_set_color(BLACK, WHITE)
                epd_ascii(x, y + y_offset, line.strip(DELIMITER))
                y_offset += size
                line = word
                line_width = word_width
        if line != "":
            # clear line up to the whole line width
            epd_set_color(WHITE, WHITE)
            epd_fill_rect(x, y + y_offset, x + limit, y + y_offset + size)
            epd_set_color(BLACK, WHITE)
            epd_ascii(x, y + y_offset, line.strip(DELIMITER))
            y_offset += size


def print_help():  # list all available functions
    print("""\
epd_connect()                           # opens a connection to EPD (TCP/IP or USB serial)
epd_handshake()                         # check if EPD is ready via serial connection
epd_disconnect()                        # close serial connection to EPD
epd_debug(True|False)                 # enable/disable(default) DEBUG serial communication (SLOW!)
epd_sleep()                              # put EPD to sleep. to wake up pin by physical pin only

epd_read_baud()                         # read EPD serial connection baud rate
epd_set_baud(int)                       # set EPD serial baud rate & restart & reconnect

epd_set_memory_nand()                   # use internal memory (default)
epd_set_memory_sd()                     # use SD card

epd_import_font()                       # copy font files form SD card to internal memory
epd_import_pic()                        # copy images from SD card to internal memory

epd_set_color(foreground,background)    # set colours from BLACK|DARK_GRAY|GRAY|WHITE

epd_set_ch_font(GBK32|GBK48|GBK64)      # set Chinese font size
epd_set_en_font(ASCII32|ASCII48|ASCII64)# set ASCII font size

epd_screen_normal()                     # flip EPD screen back to normal
epd_screen_invert()                     # flip EPD screen 180 degrees
epd_clear()                             # clear display
epd_update()                            # update screen with buffered commands

epd_lcd_digits(x,y,"digits string",scale=LCD_SM|LCD_MD|LCD_LG|<num>)
                                        # display digits including colon in LCD-digit font
                                        # scale can be any reasonable number
epd_block_digits(x,y,"digits string",scale=BLOCK_SM|BLOCK_MD|BLOCK_LG|<num>)
                                        # display 3x5 block digits including colon
                                        # scale can be any reasonable number
epd_ascii(x,y,"ascii string")           # display ascii string
epd_chinese(x,y,"hex code of Chinese")  # display Chinese string

wrap_ascii(x,y,txt,limit=800,size=32)   # auto-wraps a paragraph of ascii texts and displays
                                        # from origin x,y with optional width limit and font size

epd_pixel(x,y)                          # draw a pixel
epd_line(x0,y0,x1,y1)                   # draw a line
epd_rect(x0,y0,x1,y1)                   # draw a rectangle
epd_fill_rect(x0,y0,x1,y1)              # draw a filled rectangle
epd_circle(x,y,radius)                  # draw a circle
epd_fill_circle(x,y,radius)             # draw a filled circle
epd_triangle(x0,y0,x1,y1,x2,y2)         # draw a triangle
epd_fill_triangle(x0,y0,x1,y1,x2,y2)    # draw a filled triangle

epd_bitmap(x,y,"image file name")       # display image
""")
