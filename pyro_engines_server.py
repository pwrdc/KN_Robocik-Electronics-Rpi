import ast
import json
import time
from engine import EngineDriver
import Pyro4

@Pyro4.expose
class Driver():
    def __init__(self):
        self.engine_driver = EngineDriver()
        self.daemon = Pyro4.Daemon('192.168.1.2')
        self.name_server = Pyro4.locateNS()
        self.name_server.register('engines_driver',self.daemon.register(self))
        print("registered")
    def compute_power(self,front, right, up, yaw):
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
    def set_velocities(self,powers_dict):
        try:
            powers = self.compute_power(powers_dict['front'],powers_dict['right'],
            powers_dict['up'],powers_dict['yaw'])
            self.engine_driver.set_engines(powers)
        except Exception as e:
            log = open('error_log.txt','w')
            log.write(str(e))
            log.close()
            time.sleep(1)

if __name__ =='__main__':
    enigne_dr = Driver()
    engine_dr.daemon.requestLoop()