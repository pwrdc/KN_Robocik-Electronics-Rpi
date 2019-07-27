from ports import TORPEDO_FIRE_DRIVER_PORT, TORPEDO_READY_CLIENT_PORT
from rov_comm import Client
import time

class Torpedoes:
    is_ready = True
    def __init__(self):
        self.client_fire = Client(TORPEDO_FIRE_DRIVER_PORT)
        self.client_ready = Client(TORPEDO_READY_CLIENT_PORT)

    def fire(self):
        command = self.client_fire.get_data()
        print(command)
        if command == "FIRE" and self.is_ready:
            print("I na koniec z obrotówy jeb") #tutaj szczelomy
            self.client_ready.send_data('WAIT')
            self.is_ready = False
            self.reload_torpedo()

    def reload_torpedo(self):
        reload_time = 2   # czas przeładowywania, do ustawienia
        """
        TUTAJ PRZEŁADOWANIE
        """
        time.sleep(reload_time)  # jak umiecie jakieś lepsze czekanie, to zmieńcie
        self.client_ready.send_data('READY')
        self.is_ready = True

if __name__ == "__main__":
    torpedoes = Torpedoes()

    while True:
        torpedoes.fire()
        time.sleep(0.02)
