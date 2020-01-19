**This project is an update of [this](https://github.com/yy502/ePaperDisplay) project to fix it with Python 3.7+**

# 4.3 inch e-Paper Display

Scripts to display vector shapes, BMP images and texts on [WaveShare 4.3 inch e-paper display module](http://www.waveshare.com/wiki/4.3inch_e-Paper) via command-line instead of the Windows-only tools provided by the manufacture.

`epd.py` is based on the Arduino/C++ library provided by the manufacture.


## Generate bitmap images to work with the e-Paper

1. Make sure the resolution of the image is less than 800x600 pixels. Start the tool mspaint.exe on Windows to open the image to be converted;
2. Select the option 24-bit bitmap in the Save as Type list, to save the image as a bmp format file;
3. Start the software tool provided by Waveshare: [uC-GUI-BitmapConvert.exe](https://www.waveshare.com/wiki/4.3inch_e-Paper_Software);
4. Click File -> Open, and select the bitmap image you want to convert;
5. Click Image -> Convert Into -> Gray4 (2 BPP);
6. Click File ->Save As, and select the option Windows Bitmap file(*.bmp) in the Save as Type list, and then enter a correct file name and save the image. Please take a note to the format of the file name (see Notes on File Management part).

## Interact With the e-Paper Display

```Python
>>> from epd import *
>>> help()              # prints help message which details all available functions
...
>>> epd_connect()       # must initiate a connection first, and then send commands to EPD
> EPD connected
> EPD handshake
...                     # whatever you want to do with EPD
>>> epd_disconnect()    # a clean finish after use
```

## Notes on File Management

The manufacture's manual isn't very clear about this. I consulted their technical support regarding how to remove the preloaded files, but the answer he gave some isn't the fact by my experiments. So here's my conclusion:

* The 128MB internal storage is partitioned into 48MB for fonts and 80MB for images (according to the manual, unverified)
* When calling the import functions (one for fonts and one for images), the relevant internal partition gets CLEARED and the fonts or images in the *root* directory of the SD card are copied over.
* Valid fonts or images are determined by the file names:
  * `GBK32.FON`,`GBK48.FON` and `GBK64.FON` for fonts
  * capital letters and digits followed by `.BMP` for images. Note that the total length of file names must be no more than 10 chracters including `.BMP`.
* If no valid font or image is found on SD card, the import functions will just clear the relevant internal storage.
```Python
# Example: to import images
# insert SD card
> epd_set_memory_sd()
> epd_import_pic()
> epd_set_memory_nand()
# remove SD card
```

## Error Codes

```
0       Invalid command
1       SD card initiation failed
2       Invalid arguments
3       SD card not inserted
4       File not found
20      Validation failed
21      Invalid frame
250     Undefined error
```