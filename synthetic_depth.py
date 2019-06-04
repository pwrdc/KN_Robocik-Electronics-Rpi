import time

from ports import DEPTH_DRIVER_PORT, DEPTH_CLIENT_PORT
from rov_comm import Client, ZMQ_Server
from logpy.LogPy import Logger

SCALETOCM = 1.019


class DepthSensor:
    def __init__(self):
        self.client = Client(DEPTH_DRIVER_PORT)
        self.logger = Logger(filename='depth')

    def run(self):
        print("enter depth or esc")

        user_input = ''
        while True:
            user_input = input()
            val = 0.0
            try:
                val = float(user_input)
                self.client.send_data(val)
            except:
                if user_input == 'esc':
                    break
    def __del__(self):
        pass
        #self.logger.exit()

if __name__ == '__main__':
    
    #server = ZMQ_Server(DEPTH_DRIVER_PORT, DEPTH_CLIENT_PORT)
    #server.run()
    
    depth_sensor = DepthSensor()
    depth_sensor.run()

    # in case of sensor error
