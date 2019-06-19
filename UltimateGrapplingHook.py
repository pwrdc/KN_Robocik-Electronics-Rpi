from RPi import GPIO
import time
import threading
import os
GPIO.setmode(GPIO.BCM)

# Adnotacja [1]
# Python nie ma definicji zmiennej. Stosuje ewentualnie makra. NIe ma rowniez wskaznikow wiec nie mozna przekazac
# konkretnego adresu makra. W funkcjach zawsze jest kopia umieszczona pod nowym makrem.
# Zeby tego uniknac trzeba stworzyc definicje wlasnej zmiennej (klase) czyli wlasnie klase Variable.
# Klasy sa przekazywane przez REFERENCJE dlatego zmienna counter1 pomimo, ze nie jest globalna to watek enkoder
# moze edytowac jego wartosc (jego, a nie kopie) i tym samym w main() jest ta zmiana zauwazalna.

# Adnotacja [2]
# Kazdy watek mozna uruchomic tylko raz. Jesli raz sie watek zatrzyma, to nie mozna uruchomic go po raz drugi.
# Stad przez referencje musi byc przekazywany parametr (thread.working) ktory pozwoli zatrzymac wykonywanie
# sie glownej czesci watku.

# Adnotacja [3]
# Problem wystepuje z natrafianiem sygnalow clk oraz dt na takie same stany po pewnym czasie.
# Stosujac time.sleep() tracimy ciaglosc odczytywania sygnalu i moze sie zdarzyc po np. time.sleep(1), ze
# trafimy na dokladnie ten sam sygnal SPRZED time.sleep(1) i odczyt bedzie falszywy.
# np. ze enkoder obracal sie w drugim kierunku albo nie obrocil sie wcale,
# albo jesli w 1 sekunde enkoder obrocil sie o 360 stopni. Dla watku bedzie to oznaczalo ze nie obrocil sie wcale
# i tym samym aby uzyskac balans pomiedzy zurzyciem procesora a skutecznoscia odczytu watku, trzeba ustawic time.sleep(0.0001)

class Variable(object): #klasa zmiennej zeby przekazywac do funkcji przez referencje -> sprawdz [1]
    def __init__(self, value): self.value = value

def UstawieniaRPi(_clk, _dt, _motor_en, _motor_pwm, _motor_dir): # funkcja ustawiajaca piny
    GPIO.setmode(GPIO.BCM) #numerowanie pinow GPIO wedlug BCM
    GPIO.setup(_clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(_dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(_motor_pwm, GPIO.OUT) #32 - PWM1
    GPIO.setup(_motor_dir, GPIO.OUT) #18 - kierunek obrotu
    GPIO.setup(_motor_en, GPIO.OUT) #15 Zeby ustawic Enable
 
def enkoder(clk, dt, counter, thread_working): # Funkcja sprawdzajaca enkoder
    GPIO.setmode(GPIO.BCM)
    clkLastState = GPIO.input(clk)
    print("en koder")
    while True:
        time.sleep(0.1) # Zeby nie mielilo procesora kiedy watek jest zawieszony przed swoim wykonywaniem
        while thread_working.value:            
            clkState = GPIO.input(clk)                    
            if clkState != clkLastState:
                dtState = GPIO.input(dt)
                if dtState != clkState:
                    counter.value += 1
                else:
                    counter.value -= 1
                #os.system('clear')
                print (counter.value)
            time.sleep(0.0001) # musi byc najwiecej 1ms zeby odczyt sygnalow clk oraz dt PO przerwie nie byl taki sam [3] 
            clkLastState = clkState
            

def main():
    clk1 = 2 #3 Sygnal clk enkodera
    dt1 = 3 #5 Sygnal dt enkodera
    motor1_en = 22 #15 zeby wlaczyc sterowanie silnikiem w HAT
    motor1_pwm = 12 #32 pin na ktorym jest wysylany pwm
    motor1_dir = 24 #18 odpowiedzialny za kierunek obrotu
    LastCounter1 = 0 # Ostatia znana wartosc countera
    flaga = 1 # Do dzialania maina
    GPIO.setwarnings(False) # wylaczenie powiadomien o bledach
    counter1 = Variable(0) #Zlicza impulsy enkodera
    thread_working1 = Variable(False) # zmienna "zatrzymujaca" enkoder [2]   
    UstawieniaRPi(clk1, dt1, motor1_en, motor1_pwm, motor1_dir) # Ustawienia Sterownika dla silnika 1
    enk1 = threading.Thread(target=enkoder, args=(clk1, dt1, counter1, thread_working1)) # Przygotowanie watku do sprawdzanie enkodera 1
    enk1.start() # Uruchomienie watku dla enkodera 1
    pwm1 = GPIO.PWM(motor1_pwm, 50) # ustawienie pinu na PWM)
    pwm1.start(0) # ustawienie pwm na 100%
    while flaga == 1:
        kierunek = int(input("zeby zamknac chwytak = 1, otworz = 0 \n\r"))  
        GPIO.output(motor1_dir, kierunek)
        GPIO.output(motor1_en, True) #Zeby sterowac silnikiem  HAT 
        thread_working1.value = True
        pwm1.ChangeDutyCycle(100)
        while True:            
            LastCounter1 = counter1.value
            time.sleep(0.1)
            if LastCounter1 == counter1.value:
                print("stop")
                pwm1.ChangeDutyCycle(0)
                thread_working1.value = False
                break
        GPIO.output(motor1_en, False) # Zatrzymanie silnika na HAT
        decyzja = int(input("Czy chcesz kontynuowac 1/0? \n\r"))
        flaga = decyzja
            
if __name__ == '__main__':
    main()

GPIO.cleanup()



