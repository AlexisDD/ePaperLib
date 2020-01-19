import sys

from epd import *

if __name__ == "__main__":
    try:
        epd_connect()
    except:
        sys.exit()

    epd_clear()
    sleep(3)

    epd_ascii(100, 100, "Hello world")

    epd_update()
    sleep(5)

    epd_disconnect()
