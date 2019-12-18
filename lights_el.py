import time

from ports import LIGHTS_DRIVER_PORT
from rov_comm import Client
from light_handling import LightHandling

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
    lights = Lights()

    while True:
        lights.set_brightness()
        time.sleep(0.02)
