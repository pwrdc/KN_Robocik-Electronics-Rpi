import ast
import json
import time
import spidev
import struct

from engine import EngineDriver
import rov_comm
import ports

max_current = 40 #maksymalny dopuszczalny prad w amperach

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 15600000

engines_list = ["fl", "fr", "bl", "br", "vfl", "vfr", "vbl", "vbr"]

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

    motor_powers = {
        "fl": -fl,
        "fr": -fr,
        "bl": -bl,
        "br": -br,
        "vfl": -vbl,
        "vfr":- vbl,
        "vbl": -vbl,
	"vbr": -vbl
    }
    
    current = 0

    for i in engines_list:
        current += 20 * abs(motor_powers[i]) # 100% mocy na pojedynczy silnik to 20A
    
    if current < max_current:
        norm_factor = max_current/current # wspolczynnik normalizacji mocy
        for i in engines_list:
            motor_powers[i] *= norm_factor

    return motor_powers

def set_engines(powers):
    for i in engines_list:
        x = 100 + powers[i] * 100
        x = int(x)
        spi.writebytes(struct.pack("B",x))
    spi.writebytes(struct.pack("B",255))

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
        print(powers)
        time.sleep(0.05)
        set_engines(powers)
    except Exception as e:
        print(e)
        time.sleep(5)

