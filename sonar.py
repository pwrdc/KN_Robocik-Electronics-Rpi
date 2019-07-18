from brping import Ping1D
import time

from ports import DISTANCE_DRIVER_PORT, DISTANCE_CLIENT_PORT
from rov_comm import Client, ZMQ_Server
from definitions import DEFLOG, USB
from logpy.LogPy import Logger

class Sonar:
    def __init__(self, USB_device_adress=USB.SONAR):
        self.logger = DEFLOG.DISTANCE_LOCAL_LOG
        if DEFLOG.DISTANCE_LOCAL_LOG:
            self.logger = Logger(filename='front_distance',
                                 directory=DEFLOG.LOG_DIRECTORY)

        self.sensor = Ping1D(USB_device_adress, 115200)
        self.log("connected to the device")
        self.client = Client(DISTANCE_DRIVER_PORT)
        self.log("connected to the server")

    def run(self):
        # We must initialize the sensor before reading it
        if not self.sensor.initialize():
            error = "Sensor could not be initialized"
            print(error)
            self.log(error, 'error')
            exit(1)

        loop_condition = True
        while loop_condition:
            data = self.sensor.get_distance()
            if data:
                self.client.send_data(data)
                msg = str(data["distance"])
                self.log(msg)
            else:
                loop_condition = False
            time.sleep(0.035)

    def log(self, msg, logtype='info'):
        if self.logger:
            self.logger.log(msg, logtype=logtype)

    def __del__(self):
        pass
        if self.logger:
            self.logger.exit()

if __name__ == '__main__':
    sonar = Sonar()
    sonar.run()
