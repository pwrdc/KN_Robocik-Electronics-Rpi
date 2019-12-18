import ms5837
import time

from logpy.LogPy import Logger

from ports import DEPTH_DRIVER_PORT, DEPTH_CLIENT_PORT
from definitions import DEFLOG
from .rov_comm import Client

class DepthSensor:
    def __init__(self):
        self.sensor = ms5837.MS5837_02BA() # Default I2C bus is 1 (Raspberry Pi 3)        
        self.client = Client(DEPTH_DRIVER_PORT)

        self.logger = DEFLOG.DEPTH_LOCAL_LOG
        if self.logger:
            self.logger = Logger(filename='depth_sensor', directory=DEFLOG.LOG_DIRECTORY)

    def run(self):
        # We must initialize the sensor before reading it
        if not self.sensor.init():
            error = "Sensor could not be initialized"
            self.log(error, 'error')
            print(error)
            exit(1)

        # We have to read values from sensor to update pressure and temperature
        if not self.sensor.read():
            error = "Sensor read failed!"
            self.log(error, 'error')
            print(error)
            exit(1)

        loop_condition = True
        while loop_condition:
            if self.sensor.read():
                self.client.send_data(self.sensor.depth())

                msg = str(self.sensor.depth())
                if self.logger:
                    self.logger.log(msg)
            else:
                loop_condition = False

    def __del__(self):
        self.logger.exit()

    def log(self, msg, logtype='info'):
        if self.logger:
            self.logger.log(msg, logtype=logtype)

if __name__ == '__main__':
    depth_sensor = DepthSensor()
    depth_sensor.run()
