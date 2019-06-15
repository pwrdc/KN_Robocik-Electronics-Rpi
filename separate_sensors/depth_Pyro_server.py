import Pyro4
from definitions import RPI_ADDRESS

@Pyro4.expose
class Depth_SERVER():
    def __init__(self):
        self.depth = 0
        self.daemon = Pyro4.Daemon('192.168.1.6')
        self.name_server = Pyro4.locateNS()
        self.name_server.register('depth_server',self.daemon.register(self))
        print('Depth server registered')

    def set_depth(self, data):
        '''
        :param data: dictionary like in __init__
        '''
        self.depth = data

    def get_depth(self):
        return self.depth

if __name__ == '__main__':
    depthServer = Depth_SERVER()
    depthServer.daemon.requestLoop()
