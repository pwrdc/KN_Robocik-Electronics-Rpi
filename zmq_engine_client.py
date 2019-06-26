import ast
import json
import time
import spidev
import struct

from engine import EngineDriver
import rov_comm
import ports

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 15600000

def compute_power(front, right, up, yaw):
    """
    front, right, up, yaw [-1,1]
    fl (front left), fr, bl, br, vfl (vertical front left), vfr, vbl, vbr [-1,1]
    przelicza prędkości na moc silników.
    fl przyjmuję początkowo jako 1,
    potem optymalizuję wartości za pomocą correction.
    optymalizacja - równe, najmniejsze możliwe obciążenie silników
    Wersja bez ograniczenia mocy - parametry z zakresu [-1,1] takie, że:
    abs(front) + abs(right) <= 1
    abs(front) + abs(yaw) <= 1
    abs(right) + abs(yaw) <= 1
    Pełna moc możliwa w każdym kierunku
    należy nałożyć dodatkowe ograniczenia przy wyznaczaniu parametrów!
    """

    fl = 1
    fr = fl - 2*right - 2*yaw
    bl = fl - 2*front - 2*yaw
    br = fl - 2*right - 2*front
    vbl = up

    correction = -0.5 * (min(fl, fr, bl, br) + max(fl, fr, bl, br))
    fl += correction
    fr += correction
    bl += correction
    br += correction

    bl =-bl
    br = -br

    motor_powers = {
        "fl": fl,
        "fr": fr,
        "bl": bl,
        "br": br,
        "vfl": vbl,
        "vfr": vbl,
        "vbl": vbl,
	"vbr": vbl
    }
    
    return motor_powers

def set_engines(powers):
    engines_list = ["fl", "fr", "bl", "br", "vfl", "vfr", "vbl", "vbr"]
    for i in engines_list:
        x = int(100 + powers[i] * 100, 10)
        spi.writebytes(strct.pack("B",x))
    spi.writebytes(struct.pack("B",255))

engine_driver = EngineDriver()
engine_slave = rov_comm.Client(ports.ENGINE_MASTER_PORT)
print ("a")
while True:
    try:
        string = engine_slave.get_data() #robimy z byte na string
        #print('Typ zmiennej string',type(string),string)
        #string = string[2:-1] # i tak zostaje b"tekst", po tej instrukcji zostanie tekst
        #dictionary = ast.literal_eval(string) #robimy dict
        #print(dictionary)
        #print(string)
        powers = compute_power(string['front'],string['right'],
        string['up'],string['yaw'])
        #print('dictionary type',type(dictionary),dictionary)
        #print(powers)
        set_engines(powers)
    except Exception as e:
        print(e)
        time.sleep(5)

