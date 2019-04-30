import ast
import json
import time

from engine import EngineDriver
import rov_comm
import ports

def compute_power(front, right, up, yaw):
    """
    front, right, up, yaw [-1,1]
    fl (front left), fr, bl, br, vl, vr, vb [-1,1]
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

    vlvr_to_vb = 0.5    # stosunek mocy silników pionowych przednich do tylnego. do konfiguracji
    fl = 1
    fr = fl - 2*right - 2*yaw
    bl = fl - 2*front - 2*yaw
    br = fl - 2*right - 2*front
    vb = up
    vl = up * vlvr_to_vb

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
        "vl": vl,
        "vr": vl,
        "vb": vb
    }
    
    return motor_powers

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
        engine_driver.set_engines(powers) #wrzucamy dict na silniki
    except Exception as e:
        print(e)
        time.sleep(5)

