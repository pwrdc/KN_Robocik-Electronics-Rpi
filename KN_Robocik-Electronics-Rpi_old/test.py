from time import sleep
import struct
import spidev

ENGINES_LIST = ["fl", "fr", "bl", "br", "vfl", "vfr", "vbl", "vbr"]

def set_engines(powers):
    spi.writebytes(struct.pack("B", 255))
    for i in ENGINES_LIST:
        x = 100 + powers[i] * 100
        x = int(x)
        spi.writebytes(struct.pack("B",x))

        
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 15600000

while True:
    powers = { "fl": 0.05, "fr": 0.00, "bl":0.00, "br":0.00, "vfl":0.00, "vfr":0.00, "vbl":0.00, "vbr": 0.00}
    set_engines(powers)
    sleep(0.01)
