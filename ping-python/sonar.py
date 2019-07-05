
from brping import Ping1D
import time
ping = Ping1D("/dev/ttyUSB1", 115200)

ping.initialize()

ping.set_speed_of_sound(1450000)
plik = open("daneSonar", "w")

try:
	while True:
		dane = ping.get_distance()
		if dane:
			plik.write(str(dane) + '\n')
			print(str(dane) + '\n')
		else:
			plik.write("Blad\n")
		time.sleep(0.035)
finally:
	plik.close()
