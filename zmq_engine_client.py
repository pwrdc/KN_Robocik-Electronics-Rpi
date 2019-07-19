import time
import struct
import spidev

from engine import EngineDriver
from definitions import MODE, DEFLOG
import rov_comm
import ports

from logpy.LogPy import Logger

# Parametry ograniczeń

max_current = 40    # maksymalny dopuszczalny prad w amperach
v_derating = 0.0   # Zakres <0.0 : 1.0>,
                            # kazda wartosc dopouszczalna, np:
                            # 0.0 -  ograncza wszystkie silniki jednakowo
                            # 0.5 - najpierw ogranicza silniki poziome (tylko połowe mocy), potem pionowe i poziome
                            # 1.0 - najpierw ogranicza silniki poziome (az do całkowitego zatrzymania), potem pionowe

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

    # ograniczenie mocy - BEGIN
    current = 0
    current_v = 0
    current_h = 0

    current_v += 20 * abs(motor_powers["fl"])
    current_v += 20 * abs(motor_powers["fr"])
    current_v += 20 * abs(motor_powers["bl"])
    current_v += 20 * abs(motor_powers["br"])

    current_h += 20*abs(motor_powers["vfl"])
    current_h += 20*abs(motor_powers["vfr"])
    current_h += 20*abs(motor_powers["vbl"])
    current_h += 20*abs(motor_powers["vbr"])

    current = current_h + current_v

    over_current = current - max_current

    if over_current > 0:
        v_over_current = min(v_derating*max_current, over_current);
        if current_v > 0:
            v_over_current = min(v_over_current, current_v)
            deratin_factor = 1.0 - v_over_current/current_v

            motor_powers["fl"] = motor_powers["fl"]*deratin_factor
            motor_powers["fr"] = motor_powers["fr"]*deratin_factor
            motor_powers["bl"] = motor_powers["bl"]*deratin_factor
            motor_powers["br"] = motor_powers["br"]*deratin_factor


    # ograniczenie mocy na wszystkich silnikach

    current = 0

    for i in ENGINES_LIST:
        current += 20 * abs(motor_powers[i]) # 100% mocy na pojedynczy silnik to 20A

    if current > max_current:
        norm_factor = max_current/current # wspolczynnik normalizacji mocy
        for i in ENGINES_LIST:
            motor_powers[i] *= norm_factor


    # ograniczenie mocy - END

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
