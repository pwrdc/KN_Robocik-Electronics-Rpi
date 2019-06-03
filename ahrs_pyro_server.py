import Pyro4
from definitions import RPI_ADDRESS

@Pyro4.expose
class AHRS_SERVER():
    def __init__(self):
        self.data = {
        'lineA_x':0,
        'lineA_y':0,
        'lineA_z':0,
        'angularA_x':0,
        'angularA_y':0,
        'angularA_z':0,
        'roll':0,
        'pitch':0,
        'yaw':0
        }
        self.daemon = Pyro4.Daemon(RPI_ADDRESS)
        self.name_server = Pyro4.locateNS()
        self.name_server.register('ahrs_server',self.daemon.register(self))
        print('AHRS server registered')

    def set_data(self, data):
        '''
        :param data: dictionary like in __init__
        '''
        self.data = data

    def get_all_data(self):
        return self.data
