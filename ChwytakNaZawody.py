import time
from collections import defaultdict #Byc moze ta biblioteka jest zbedna (prawdopdobnie jest)
from threading import Thread
from RPi import GPIO
import os
    
class MalySilnik(object):
    
    def __init__(self, _motor_pin1, _motor_pin2, _clk, _dt): # Argumenty dla 2 pinow dwoch przekaznikow oraz 2 pinow jednego enkodera
        self.motor_pin1 = _motor_pin1
        self.motor_pin2 = _motor_pin2
        self.clk = _clk
        self.dt = _dt
        self.counter = 0
        self.dziala = True
        self._UstawieniaSilnika()
        
    def _UstawieniaSilnika(self): # funkcja ustawiajaca piny
        GPIO.setmode(GPIO.BCM) #numerowanie pinow GPIO wedlug BCM
        GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.motor_pin1, GPIO.OUT) 
        GPIO.setup(self.motor_pin2, GPIO.OUT)
        GPIO.output(self.motor_pin1, GPIO.HIGH)
        GPIO.output(self.motor_pin2, GPIO.HIGH)
        
    def _Enkoder(self): # Funkcja sprawdzajaca enkoder
        GPIO.setmode(GPIO.BCM)
        clkLastState = GPIO.input(self.clk)
       #print("en koder")
        while self.dziala:
            clkState = GPIO.input(self.clk)                    
            if (clkState != clkLastState):
                dtState = GPIO.input(self.dt)
                if (dtState != clkState):
                    self.counter += 1
                else:
                    self.counter += 1
                #os.system('clear')
                print (self.counter)
            time.sleep(0.0001) # musi byc najwiecej 1ms zeby odczyt sygnalow clk oraz dt PO przerwie nie byl taki sam [3] 
            clkLastState = clkState
            
    def ZamknijChwytak(self):
        self._Chwytak(1)
        
    def OtworzChwytak(self):        
        self._Chwytak(0)

    def _ZatrzymajChwytak(self):        
        GPIO.output(self.motor_pin1, GPIO.HIGH)
        GPIO.output(self.motor_pin2, GPIO.HIGH)
        self.dziala = False
                
    def _Chwytak(self, kierunek):
        self.dziala = False #Do zakonczenia watkow jesli wcisnieto kilka przyciskow po sobie
        time.sleep(0.1)
        self.dziala = True        
        last_counter = self.counter # Ostatia znana wartosc countera        
        self._Watek(self._Enkoder) # Watek do zliczania odczytu z enkodera self.counter
        self._Watek(self._Zabezpieczenie) # Watek do uruchomienia zabezpieczenia 
        if (kierunek):
            GPIO.output(self.motor_pin1, GPIO.HIGH)
            GPIO.output(self.motor_pin2, GPIO.LOW)
        else:
            GPIO.output(self.motor_pin1, GPIO.LOW)
            GPIO.output(self.motor_pin2, GPIO.HIGH)
        while (self.dziala == True):   
            last_counter = self.counter
            time.sleep(0.1)            
            if (last_counter == self.counter):                
                last_counter = self.counter
                time.sleep(0.3)
                if (last_counter == self.counter): #Podwojne zabezpieczenie... 
                    print("stop") 
                    self.dziala = False
        self._ZatrzymajChwytak()
    
    def _Zabezpieczenie(self):
        timer = time.clock() + 5 # TEN CZAS MOZE TRZEBA BEDZIE ZWIKESZYC W WODZIE GDYZ CHWYTAK BEDZIE DZIALAL WOLNIEJ !!! np. z 5 na 8 sekund
        while(timer > time.clock() and self.dziala == True):
            pass
            #print(time.clock())
            #print(timer)
        print("Zabezpieczenie czasowe")
        self.dziala = False
        
    def _Watek(self, funkcja):
        funkcja = Thread(target=funkcja)
        funkcja.start() # Uruchomienie zliczania odczytu z enkodera self.counter
'''
silnik_chwytak = MalySilnik(12, 13, 20, 21)

while (True):
    kierunek = int(input("wcisnij 0 zeby otworzyc, 1 zeby zamknac \n"))
    print(kierunek)
    silnik_chwytak._Chwytak(kierunek)
    time.sleep(2)
'''
