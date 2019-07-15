from __future__ import print_function
from RPi import GPIO
import time
from dual_tb9051ftg_rpi import motors, MAX_SPEED
import threading
import os

# Define a custom exception to raise if a fault is detected.
class DriverFault(Exception):
    def __init__(self, driver_num):
        self.driver_num = driver_num

def raiseIfFault():
    if motors.motor1.getFault():
        raise DriverFault(1)
    if motors.motor2.getFault():
        raise DriverFault(2)


clk = 2 #3 Sygnal enkodera
dt = 3 #5 Sygnal enkodera
counter = 0 #Zlicza impulsy enkodera
LastCounter = 0
GPIO.setmode(GPIO.BCM) #numerowanie pinow GPIO wedlug BCM
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 


# wylaczenie powiadomien o bledach
##GPIO.setwarnings(False)

def enkoder():
    global counter
    global clk
    global dt
    GPIO.setmode(GPIO.BCM)
    clkLastState = GPIO.input(clk)
    while True:
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)        
        if clkState != clkLastState:          
            if dtState != clkState:
                counter += 1
            else:
                counter -= 1
                os.system('clear')
            print("zeby wylaczyc wcisnij ctrl+c")
            print (counter)
            clkLastState = clkState
#petla dzialania silnikow i enkoderow
print("zeby wylaczyc wcisnij ctrl+c")
enk = threading.Thread(target=enkoder)
enk.start()

flag = 1
while flag == 1:
    try:
        motors.setSpeeds(0, 0) #ustawienie prędkości początkowo na 0
        direction = raw_input("zeby zamknac chwytak = 1, otworz = 0")
        direction = int(direction)
        print("obroty w 1 stronę") #trzeba sprawdzić która to jest strona
        if direction == 0:
            s=480 #480 to prędkość max - tak wynika z biblioteki,
            #jak będzie sie kręcić w złą stronę to zmienić na -480
        elif direction ==1:
            s=-480
        else:
            s=0 #jakby ktoś wprowadził coś innego niż 0 lub 1
        motors.motor1.setSpeed(s)
        raiseIfFault()
        time.sleep(0.002)        
        while LastCounter != counter:
            LastCounter = counter
            sleep(0.1)
        else:
            motors.motor1.setSpeed(0)
            
            raise Exception
    #except KeyboardInterrupt:
    except Exception:
        # wylaczanie silnikow przy przerwaniu programu przez wcisniecie ctrl+c
        motors.setSpeed(0, 0)
        flag = raw_input("Czy chcesz kontynuowac 1/0?")
        flag = int(flag)
GPIO.cleanup()
        

