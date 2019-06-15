import ms5837
import time

#from ports import DEPTH_DRIVER_PORT, DEPTH_CLIENT_PORT
#from rov_comm import Client, ZMQ_Server
from logpy.LogPy import Logger
import Pyro4
from definitions import DepthSensor as DP

SCALETOCM = 1.019


class DepthSensor:
    def __init__(self):
        self.sensor = ms5837.MS5837_30BA() # Default I2C bus is 1 (Raspberry Pi 3)        
        #self.client = Client(DEPTH_DRIVER_PORT)
        Pyro4.locateNS()
        self.depth_server = Pyro4.Proxy("PYRONAME:depth_server")
        #self.logger = Logger(filename='depth')
    def setter (self):
        exec('self.depth_server.'+str(DP.set_depth)+'(self.sensor.depth())')
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
                
                self.setter()
                time.sleep(0.001)
                #print(self.sensor.pressure())
                #msg = str(self.sensor.depth())
                #print(msg)
                #self.logger.log(msg)
            else:
                loop_condition = False
    def __del__(self):
        pass
        #self.logger.exit()

if __name__ == '__main__':
    
    #server = ZMQ_Server(DEPTH_DRIVER_PORT, DEPTH_CLIENT_PORT)
    #server.run()
    
    depth_sensor = DepthSensor()
    depth_sensor.run()

    # in case of sensor error
