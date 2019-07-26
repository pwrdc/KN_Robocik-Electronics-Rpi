from ports import TORPEDO_DRIVER_PORT, TORPEDO_CLIENT_PORT
from rov_comm import Client
import time

class Torpedoes:
    def __init__(self):
        self.client = Client(TORPEDO_DRIVER_PORT)

    def fire(self):
        dictionary = self.client.get_data()
        print(type(dictionary))
        print(dictionary)
        fire = dictionary["fire"]
        is_ready = dictionary["is_ready"]
        if fire & is_ready:
            print("Fire")
            self.client.send_data(self.to_dict(
                fire=False,
                is_ready=False))
            self.reload_torpedo()

    def to_dict(self, fire=None, is_ready=None):
        ''' 
        Converting data to dictionary
        '''
        dic = {}
        for key,value in locals().items():
            if key != 'self' and key != 'dic' and value != None:
                dic[key] = value
        return dic

    def reload_torpedo(self):
        reload_time = 2   # czas przeładowywania, do ustawienia
        """
        TUTAJ PRZEŁADOWANIE
        """
        time.sleep(reload_time)  # jak umiecie jakieś lepsze czekanie, to zmieńcie
        self.client.send_data(self.to_dict(
            fire=self.client.get_data()["fire"],
            is_ready=True))

if __name__ == "__main__":
    torpedoes = Torpedoes()

    while True:
        torpedoes.fire()
        time.sleep(0.02)
