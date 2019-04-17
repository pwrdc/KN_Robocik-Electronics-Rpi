import ms5837
import time

from ports import depth_driver_port, depth_client_port
from rov_comm import Client, ZMQ_Server
from logpy.LogPy import Logger

SCALETOCM = 1.019


class DepthSensor:
    def __init__(self):
        self.sensor = ms5837.MS5837_30BA() # Default I2C bus is 1 (Raspberry Pi 3)        
        self.client = Client(depth_driver_port)
        self.logger = Logger(filename='depth')

    def run(self):
        # We must initialize the sensor before reading it
        if not self.sensor.init():
            print("Sensor could not be initialized")
            exit(1)

        # We have to read values from sensor to update pressure and temperature
        if not self.sensor.read():
            print("Sensor read failed!")
            exit(1)

        loop_condition = True
        while loop_condition:
            if self.sensor.read():
                self.client.send_data(self.sensor.pressure() * SCALETOCM)

                #print(self.sensor.pressure())
                msg = str(self.sensor.depth())
                self.logger.log(msg)
            else:
                loop_condition = False
    def __del__(self):
        self.logger.exit()

if __name__ == '__main__':
    
    server = ZMQ_Server(depth_driver_port, depth_client_port)
    server.run()
    
    depth_sensor = DepthSensor()
    depth_sensor.run()

    # in case of sensor error
