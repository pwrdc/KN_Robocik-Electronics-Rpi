import pigpio
import time
from logpy.LogPy import Logger
from ports import LIGHTS_DRIVER_PORT
from rov_comm import Client

PWM_lights = 27
ON_FULL = 600
OFF = 1400


class LightHandling:
    def __init__(self):
        self.pi = pigpio.pi()
        self.logger = Logger(filename='light_handling', directory='logs/electro/')

        if not self.pi.connected:
            self.logger.log("pi not connected", logtype='error')
            exit()

        self.logger.log("setup")
        self.setup()

    def setup(self):
        self.pi.set_PWM_frequency(PWM_lights, 400)
        self.pi.set_PWM_range(PWM_lights, OFF) # 550 - OFF, 950 - ON_FULL
        self.pi.set_PWM_dutycycle(PWM_lights, OFF)

    def lights_set_brightness(self,x):
        if x < 0: x = 0
        if x > 100: x = 100
        x=100-x
        self.pi.set_PWM_dutycycle(PWM_lights, -8*x+1400)
        self.logger.log("lights' brightness: " + str(x) + "%")

class Lights:

    def __init__(self):
            self.client_brightness = Client(LIGHTS_DRIVER_PORT)
            self.light_handling = LightHandling()

    def set_brightness(self):
        command = self.client_brightness.get_data()
        #print(command) 
        x = int(command['power'])
        self.light_handling.lights_set_brightness(x)

if __name__ == "__main__":
    LIGHTS = LightHandling()
    LIGHTS.lights_set_brightness(0)
