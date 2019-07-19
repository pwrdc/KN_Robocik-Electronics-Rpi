import time
import struct
import spidev

from engine import EngineDriver
from definitions import MODE, DEFLOG
import rov_comm
import ports

from logpy.LogPy import Logger


max_current = 40 #maksymalny dopuszczalny prad w amperach

ENGINES_LIST = ["fl", "fr", "bl", "br", "vfl", "vfr", "vbl", "vbr"]


# ROV3
def _normalize_values(val_important, val_void):
    if abs(val_important) + abs(val_void) <= 1:
        return val_important, val_void
    val_void /= 2
    if abs(val_important) + abs(val_void) <= 1:
        return val_important, val_void
    val_important /= 2
    return val_important, val_void

def compute_power_rov3(front, right, up, yaw):
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

    front, right = _normalize_values(front, right)
    front, yaw = _normalize_values(front, yaw)
    right, yaw = _normalize_values(right, yaw)

    vlvr_to_vb = 0.64    # stosunek mocy silników pionowych przednich do tylnego. do konfiguracji
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

    #bl = -bl
    #br = -br
    #vb = 0.0

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

# ROV4
def compute_power_rov4(front, right, up, yaw):
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

    #1.07.2019 - zmiana mapowania na dzialajace z zalaczonym opisem podlaczenia PWM
    motor_powers = {
        "fl": -fl,
        "fr": -fr,
        "bl": -bl,
        "br": -br,
        "vfl": -vbl,
        "vfr": -vbl,
        "vbl": -vbl,
	"vbr": -vbl
    }

    current = 0

    for i in ENGINES_LIST:
        current += 20 * abs(motor_powers[i]) # 100% mocy na pojedynczy silnik to 20A

    if current > max_current:
        norm_factor = max_current/current # wspolczynnik normalizacji mocy
        for i in ENGINES_LIST:
            motor_powers[i] *= norm_factor

    return motor_powers

def set_engines(powers):
    spi.writebytes(struct.pack("B", 255))
    for i in ENGINES_LIST:
        x = 100 + powers[i] * 100
        x = int(x)
        spi.writebytes(struct.pack("B",x))
    for i in range(5):
        tmp = spi.readbytes(1)[0]
   
if __name__ == '__main__':
    logger = DEFLOG.MOVEMENTS_LOCAL_LOG
    if logger:
        logger = Logger(filename='depth_sensor', directory=DEFLOG.LOG_DIRECTORY)
    logger = Logger()
    engine_slave = rov_comm.Client(ports.ENGINE_MASTER_PORT)

    if MODE == 'ROV4':
        spi = spidev.SpiDev()
        spi.open(0,0)
        spi.max_speed_hz = 15600000
    else:
        engine_driver = EngineDriver()

    print ("WIP")
    while True:
        try:
            movements = engine_slave.get_data() #robimy z byte na movements
            if logger:
                logger.log("movements: "+str(movements))
            if MODE == 'ROV4':
                powers = compute_power_rov4(movements['front'], movements['right'],
                                            movements['up'], movements['yaw'])
            else:
                powers = compute_power_rov3(movements['front'], movements['right'],
                                            movements['up'], movements['yaw'])

            if logger:
                logger.log("engines: "+str(powers))

            time.sleep(0.05)
            if MODE == 'ROV4':
                set_engines(powers)
            else:
                engine_driver.set_engines(powers)
        except Exception as e:
            print(e)
            if logger:
                logger.log(str(e), 'error')
            time.sleep(5)
