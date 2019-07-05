import time
from collections import defaultdict
from xbox360controller import Xbox360Controller
from threading import Thread
from RPi import GPIO
import os
import board
import busio
import sys, termios, tty
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
    
class MalySilnik(object):
    
    def __init__(self, _motor_pwm, _motor_dir, _clk, _dt): # parametry Hata oraz AC/DC
        self.motor_pwm = _motor_pwm
        self.motor_dir = _motor_dir
        self.clk = _clk
        self.dt = _dt
        self.counter = 0
        self.dziala = True
        self.UstawieniaSilnika()
        
    def UstawieniaSilnika(self): # funkcja ustawiajaca piny
        GPIO.setmode(GPIO.BCM) #numerowanie pinow GPIO wedlug BCM
        GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.motor_pwm, GPIO.OUT) #32 - PWM1
        GPIO.setup(self.motor_dir, GPIO.OUT) #18 - kierunek obrotu
        self.wypelnienie_pwm = GPIO.PWM(self.motor_pwm, 50) # ustawienie pinu na PWM)
        self.wypelnienie_pwm.start(0) # ustawienie pwm na 100%self.wypelnienie_pwm = 
        
    def Enkoder(self): # Funkcja sprawdzajaca enkoder
        GPIO.setmode(GPIO.BCM)
        clkLastState = GPIO.input(self.clk)
        print("en koder")
        while self.dziala:
            clkState = GPIO.input(self.clk)                    
            if (clkState != clkLastState):
                dtState = GPIO.input(self.dt)
                if (dtState != clkState):
                    self.counter += 1
                else:
                    self.counter -= 1
                #os.system('clear')
                #print (self.counter)
            time.sleep(0.0001) # musi byc najwiecej 1ms zeby odczyt sygnalow clk oraz dt PO przerwie nie byl taki sam [3] 
            clkLastState = clkState
            
    def ZamknijChwytak(self):
        Chwytak(False)
        
    def OtworzChwytak(self):
        Chwytak(True)
                
    def Chwytak(self, kierunek):
        self.dziala = False #Do zakonczenia watkow jesli wcisnieto kilka przyciskow po sobie
        time.sleep(0.1)
        self.dziala = True        
        last_counter = self.counter # Ostatia znana wartosc countera        
        GPIO.output(self.motor_dir, kierunek)
        enk = Thread(target=self.Enkoder) # Przygotowanie watku do sprawdzanie enkodera 1
        enk.start() # Uruchomienie watku dla enkodera 1
        licznik = Thread(target=self.Zabezpieczenie)
        licznik.start()
        while (self.dziala == True):
            self.wypelnienie_pwm.ChangeDutyCycle(100)                     
            last_counter = self.counter
            time.sleep(0.1)
            if (last_counter == self.counter):
                print("stop")
                self.dziala = False   
        self.wypelnienie_pwm.ChangeDutyCycle(0)
    
    def Zabezpieczenie(self):
        timer = time.clock() + 4
        while(timer > time.clock() and self.dziala == True):
            print(timer)
            print(time.clock())
        self.dziala = False
        
            
class DuzySilnik(object):    #Klasa dla duzych silnikow (2 silniki w podstawie)
    
    def __init__(self, _motor_en, _motor_pwm, _motor_dir, _ads, _ads_pin): # parametry Hata oraz AC/DC
        self.motor_en = _motor_en
        self.motor_pwm = _motor_pwm
        self.motor_dir = _motor_dir
        self.UstawieniaSilnika()
        self.pozycja = AnalogIn(_ads, _ads_pin) # Create single-ended input on channel 0      
            
    def Jedz(self, predkosc): #  -100 < predkosc < 100           Metoda do sterowania silnikiem
        predkosc = float(predkosc) * 100        
        if(predkosc != self.wypelnienie_pwm):            
            if(predkosc == 0):
                self.wypelnienie_pwm.ChangeDutyCycle(0)
            elif(predkosc > 0):
                GPIO.output(self.motor_dir, True)
                self.wypelnienie_pwm.ChangeDutyCycle(predkosc)
            else:                
                predkosc = predkosc - 2*predkosc
                if( predkosc != self.wypelnienie_pwm):
                    GPIO.output(self.motor_dir, False)
                    self.wypelnienie_pwm.ChangeDutyCycle(predkosc)

    def UstawieniaSilnika(self):
    	GPIO.setmode(GPIO.BCM) #numerowanie pinow GPIO wedlug BCM
    	GPIO.setup(self.motor_pwm, GPIO.OUT) #32 - PWM1
    	GPIO.setup(self.motor_dir, GPIO.OUT) #18 - kierunek obrotu
    	GPIO.setup(self.motor_en, GPIO.OUT) #15 Zeby ustawic Enable
    	GPIO.output(self.motor_en, True) # Zeby sterowac silnikiem - False wylacza silnik na HAT
    	self.wypelnienie_pwm = GPIO.PWM(self.motor_pwm, 50) # ustawienie pinu na PWM)
    	self.wypelnienie_pwm.start(0) # ustawienie pwm na 100%

    def Zatrzymaj(self):
        GPIO.output(self.motor_en, False)

    def Pozycja(self):
        print

            
   # def PodajPozycje(self):
    #    return self.pozycja.voltage

class X360controler:
    i2c = busio.I2C(board.SCL, board.SDA) # Create the I2C bus        
    ads = ADS.ADS1115(i2c) # Create the ADC object using the I2C bus
    ads_pin = [ADS.P0, ADS.P1, ADS.P2, ADS.P3]
    silnik_1 = DuzySilnik(22, 12, 24, ads, ads_pin[0]) # Przegub w podstawie
    silnik_2 = DuzySilnik(23, 13, 25, ads, ads_pin[1]) # Przegub w połowie ramienia
    silnik_chwytak = MalySilnik(16, 19, 20, 21)
    numberOfEngines = 0
    numberOfValues = 2
    stara_pozycja_1 = 0
    stara_pozycja_2 = 0
    AM1 = 0
    AM2 = 0
    run = True
    left_stick = [0, 0]
    right_stick = [0, 0]
    left_trigger = 0.0
    right_trigger = 0.0
    deadzone = 0.05
    engines = numberOfValues * [0]  # x_vel, y_vel, z_vel, yaw_vel
    #engines = 10 * [0.0]
    swiatla = 0
    obslugaDanych = None
    buttons = {'A': False,
               'B': False,
               'X': False,
               'Y': False,
               'LB': False,
               'RB': False,
               'LS': False,
               'RS': False,
               'back': False,
               'start': False,
               'mode': False,
               'DU': False,
               'DD': False,
               'DL': False,
               'DR': False}
    switches = {'A': False,
                'B': False,
                'X': False,
                'Y': False,
                'LB': False,
                'RB': False,
                'LS': False,
                'RS': False,
                'back': False,
                'start': False,
                'mode': False,
                'DU': False,
                'DD': False,
                'DL': False,
                'DR': False}

    """ 
    buttonsReactions: 'Releasedbutton_a','Releasedbutton_b','Releasedbutton_x','Releasedbutton_y','Releasedbutton_trigger_l','Releasedbutton_trigger_r': self._rb,
    ,'Releasedbutton_thumb_l','Releasedbutton_thumb_r','Releasedbutton_select','Releasedbutton_start': self._start,'Releasedbutton_mode',
    'Releasedbutton_back'
    'Pressedbutton_a','Pressedbutton_b','Pressedbutton_x','Pressedbutton_y','Pressedbutton_trigger_l','Pressedbutton_trigger_r': self._rb,
    ,'Pressedbutton_thumb_l','Pressedbutton_thumb_r','Pressedbutton_select','Pressedbutton_start': self._start,'Pressedbutton_mode',
    'Pressedbutton_back'
    """

    def __init__(self):        
        
        self.buttonReactions = defaultdict(lambda: None, {'a':'b'})
        #self.buttonReactions = {'Pressedbutton_a':self.RPI.pid_turn_on,
        #                        'Pressedbutton_b':self.RPI.pid.turn_off,
        #                        'Pressedbutton_y':self.RPI.pid_hold_depth}

        #buttonReactions= defaultdict(lambda: None,{'a':'b'})
        
    def sign(self, val):
        if val != 0:
            return val / abs(val)
        else:
            return 0

    def adjust_deadzone(self, value, dzone):
        if abs(value) > dzone:
            return (value - self.sign(value) * dzone) / (1 - dzone)
        else:
            return 0

    # PAD ACTIONS
    def a(self):
        # button_a
        self.buttons['A'] = True
        self.switches['A'] = not self.switches['A']
        print('A')
        #if self.buttonReactions['PressedButton_a'] != None:
        #    self.buttonReactions['PressedButton_a']()

    def _a(self):
        # button_a
        self.buttons['A'] = False
        print('_A')
        self._run_in_thread(self.silnik_chwytak.OtworzChwytak)
        #if self.buttonReactions['Releasedbutton_a'] != None:
        #    self.buttonReactions['Releasedbutton_a']()

    def b(self):
        # button_b
        self.buttons['B'] = True
        self.switches['B'] = not self.switches['B']
        print('B')

        #if self.buttonReactions['PressedButton_b'] != None:
        #    self.buttonReactions['PressedButton_b']()

    def _b(self):
        # button_b
        self.buttons['B'] = False
        print('_B')
        self._run_in_thread(self.silnik_chwytak.ZamknijChwytak)
        #if self.buttonReactions['Releasedbutton_b'] != None:
        #    self.buttonReactions['Releasedbutton_b']()

    def x(self):
        # button_x
        self.buttons['X'] = True
        self.switches['X'] = not self.switches['X']
        print('X')

        #if self.buttonReactions['PressedButton_x'] != None:
        #    self.buttonReactions['PressedButton_x']()

    def _x(self):
        # button_x
        self.buttons['X'] = False
        print('_X')
        #if self.buttonReactions['Releasedbutton_x'] != None:
        #    self.buttonReactions['Releasedbutton_x']()

    def y(self):
        # button_y
        self.buttons['Y'] = True
        self.switches['Y'] = not self.switches['Y']
        print('Y')

        #if self.buttonReactions['PressedButton_y'] != None:
        #    self.buttonReactions['PressedButton_y']()

    def _y(self):
        # button_y
        self.buttons['Y'] = False
        print('_Y')
        #if self.buttonReactions['Releasedbutton_y'] != None:
        #    self.buttonReactions['Releasedbutton_y']()

    def lb(self):
        # button_trigger_l
        self.buttons['LB'] = True
        self.switches['LB'] = not self.switches['LB']
        print('LB')

    def _lb(self):
        # button_trigger_l
        self.buttons['LB'] = False
        print('_LB')

    def rb(self):
        # button_trigger_r
        self.buttons['RB'] = True
        self.switches['RB'] = not self.switches['RB']
        print('RB')

    def _rb(self):
        # button_trigger_r
        self.buttons['RB'] = False
        print('_RB')

    def ls(self):
        # button_thumb_l
        self.buttons['LS'] = True
        self.switches['LS'] = not self.switches['LS']
        print('LS')
        self.cur_mode = not self.cur_mode
        print('Mov mode: {}'.format(self.cur_mode))

    def _ls(self):
        # button_thumb_l
        self.buttons['LS'] = False
        print('_LS')

    def rs(self):
        # button_thumb_r
        self.buttons['RS'] = True
        self.switches['RS'] = not self.switches['RS']
        print('RS')
        self.cur_precision = not self.cur_precision
        print('Precision mode: {}'.format(self.cur_precision))

    def _rs(self):
        # button_thumb_r
        self.buttons['RS'] = False
        print('_RS')

    def back(self):
        # button_select
        self.buttons['back'] = True
        self.switches['back'] = not self.switches['back']
        print('back')
        if self.buttonReactions['Pressedbutton_back'] != None:
            self.buttonReactions['Pressedbutton_back']()

    def _back(self):
        # button_select
        self.buttons['back'] = False
        print('_back')
        if self.buttonReactions['Releasedbutton_back'] != None:
            self.buttonReactions['Releasedbutton_back']()

    def start(self):
        # button_start
        self.buttons['start'] = True
        self.switches['start'] = not self.switches['start']
        print('start')
        if self.buttonReactions['PressedButton_start'] != None:
            self.buttonReactions['PressedButton_start']()

    def _start(self):
        # button_start
        self.buttons['start'] = False
        print('_start')
        if self.buttonReactions['ReleasedButton_y'] != None:
            self.buttonReactions['ReleasedButton_y']()

    def mode(self):
        # button_mode
        self.buttons['mode'] = True
        self.switches['mode'] = not self.switches['mode']
        print('mode')
        self.run = False
        if self.buttonReactions['Pressedbutton_mode'] != None:
            self.buttonReactions['Pressedbutton_mode']()

    def _mode(self):
        # button_mode
        self.buttons['mode'] = False
        print('_mode')
        if self.buttonReactions['Releasedbutton_mode'] != None:
            self.buttonReactions['Releasedbutton_mode']()

    def left(self, axis):
        # axis_l
        self.left_stick[0] = self.adjust_deadzone(axis.x, 3 * self.deadzone)
        self.left_stick[1] = -self.adjust_deadzone(axis.y, 3 * self.deadzone)

    def right(self, axis):
        # axis_r
        self.right_stick[0] = self.adjust_deadzone(axis.x, 3 * self.deadzone)
        self.right_stick[1] = -self.adjust_deadzone(axis.y, 3 * self.deadzone)

    def hat(self, axis):
        # hat
        if axis.x == 1:
            self.buttons['DR'] = True
            self.buttons['DL'] = False
            self.switches['DR'] = not self.switches['DR']
        elif axis.x == -1:
            self.buttons['DL'] = True
            self.buttons['DR'] = False
            self.switches['DL'] = not self.switches['DL']
        else:
            self.buttons['DR'] = False
            self.buttons['DL'] = False
        if axis.y == 1:
            self.buttons['DU'] = True
            self.buttons['DD'] = False
            self.switches['DU'] = not self.switches['DU']
        elif axis.y == -1:
            self.buttons['DD'] = True
            self.buttons['DU'] = False
            self.switches['DD'] = not self.switches['DD']
        else:
            self.buttons['DD'] = False
            self.buttons['DU'] = False

    def lt(self, axis):
        # trigger_l
        self.left_trigger = axis.value

    def rt(self, axis):
        # trigger_r
        self.right_trigger = axis.value

    def on_pressed(self, button):
        options = {'button_a': self.a,
                   'button_b': self.b,
                   'button_x': self.x,
                   'button_y': self.y,
                   'button_trigger_l': self.lb,
                   'button_trigger_r': self.rb,
                   'button_thumb_l': self.ls,
                   'button_thumb_r': self.rs,
                   'button_select': self.back,
                   'button_start': self.start,
                   'button_mode': self.mode}
        options[button.name]()

    def on_released(self, button):
        options = {'button_a': self._a,
                   'button_b': self._b,
                   'button_x': self._x,
                   'button_y': self._y,
                   'button_trigger_l': self._lb,
                   'button_trigger_r': self._rb,
                   'button_thumb_l': self._ls,
                   'button_thumb_r': self._rs,
                   'button_select': self._back,
                   'button_start': self._start,
                   'button_mode': self._mode}
        options[button.name]()

    def on_moved(self, axis):
        options = {'axis_l': self.left,
                   'axis_r': self.right,
                   'hat': self.hat,
                   'trigger_l': self.lt,
                   'trigger_r': self.rt}
        options[axis.name](axis)

    # STEERING FUNCTIONS
    #def steering(self):

    def cart2coord(self, x_coord, y_coord, z_coord, o_coord, a_coord, t_coord):  # to add inverse kinematics!
        pair1 = 1 * x_coord
        pair2 = 1 * y_coord
        pair3 = 1 * z_coord
        pair4 = 1 * o_coord
        pair5 = 1 * a_coord
        pair6 = 1 * t_coord
        return [pair1, pair2, pair3, pair4, pair5, pair6]
    
    def updateAngle(self): #funkcja aktualizjaca kąt
        VM1=self.silnik_1.pozycja.voltage -0.68 #volltage motor 1 - napiecie na siniku 1
        VM2=self.silnik_2.pozycja.voltage #napiecie na siniku 2
        self.AM1=12 + round((VM1-0.391)*360/(1.906 - 0.391), 0) #angle motor 1 - kąt na silniku 1
        self.AM2=163 + round((VM2-0.391)*360/(1.906 - 0.391), 0) #angle motor 2 - kąt na silniku 2
        
    def Start(self):

        with Xbox360Controller(0, axis_threshold=self.deadzone) as controller:
            # BUTTONS
            controller.button_a.when_pressed = self.on_pressed  # A
            controller.button_a.when_released = self.on_released
            controller.button_b.when_pressed = self.on_pressed  # B
            controller.button_b.when_released = self.on_released
            controller.button_x.when_pressed = self.on_pressed  # X
            controller.button_x.when_released = self.on_released
            controller.button_y.when_pressed = self.on_pressed  # Y
            controller.button_y.when_released = self.on_released
            controller.button_trigger_l.when_pressed = self.on_pressed  # LB
            controller.button_trigger_l.when_released = self.on_released
            controller.button_trigger_r.when_pressed = self.on_pressed  # RB
            controller.button_trigger_r.when_released = self.on_released
            controller.button_thumb_l.when_pressed = self.on_pressed  # LS
            controller.button_thumb_l.when_released = self.on_released
            controller.button_thumb_r.when_pressed = self.on_pressed  # RS
            controller.button_thumb_r.when_released = self.on_released
            controller.button_select.when_pressed = self.on_pressed  # back
            controller.button_select.when_released = self.on_released
            controller.button_start.when_pressed = self.on_pressed  # start
            controller.button_start.when_released = self.on_released
            controller.button_mode.when_pressed = self.on_pressed  # mode
            controller.button_mode.when_released = self.on_released
            # AXES
            controller.axis_l.when_moved = self.on_moved  # left
            controller.axis_r.when_moved = self.on_moved  # right
            controller.hat.when_moved = self.on_moved  # hat
            controller.trigger_l.when_moved = self.on_moved  # LT
            controller.trigger_r.when_moved = self.on_moved  # RT
            # The Loop
            counter =0
            minA = 250 #kat do warunkow, z zapasem w góre zamiast 180
            maxA = 350 #kat do warunkow, z zapasem w dół zamiast 360
            minB = 100 #kat do warunkow, z zapasem w dół zamiast 450
            maxB = 260 #kat do warunkow, z zapasem w dół zamiast 450
            dodatnia = 0.5 #rotation speed  
            ujemna = -0.5  #predkosc obrotow przeciwnie z wskazówkami zegara 
            while self.run:                
                time.sleep(0.005)
                try:
                    #print("przed metoda")
                   # self.updateAngle()
                   # if (self.AM2 < self.AM1 and self.AM1 - self.AM2 < 180):                
                    self._run_in_thread2(self.silnik_1.Jedz, self.right_stick[1]) # Dzialania silnika sa uruchamiane w watku zeby mozna bylo sterowac np. dwoma silnikami jednoczenie bez 
                    self._run_in_thread2(self.silnik_2.Jedz, self.left_stick[1])  # przerywania pracy programu i monitorowania pada
                        

##                    elif (self.AM1 <= minA):
##                        self._run_in_thread2(self.silnik_1.Jedz, ujemna)
##                        print("A<minA")
##                        
##                    elif (sef.AM1 >= maxA):
##                        self._run_in_thread2(self.silnik_1.Jedz, dodatnia)
##                        print("A>=maxA")     
                   # elif (self.AM2 + 5 >= self.AM1):
                   #     self._run_in_thread2(self.silnik_2.Jedz, ujemna)
                   #     print("B+5>=A")
##                    elif (self.AM2 <= minB):
##                        self._run_in_thread2(self.silnik_2.Jedz, dodatnia)
##                        print("B<=minB")
##                    elif (self.AM2 >= maxB):
##                        self._run_in_thread2(self.silnik_2.Jedz, ujemna)
##                        print("B>=maxB")
                    #elif (self.AM1 - self.AM2 >= 180):
                   #     self._run_in_thread2(self.silnik_2.Jedz, dodatnia)
                   #     print("A-B>=180")                    
                    
##                    if(AM1 != oldAM1 or  AM2 != oldAM2)
##                    if(self.stara_pozycja_1 != (self.silnik_1.pozycja.voltage-0.780)*360/(3.946 - 0.780) or self.stara_pozycja_2 != (self.silnik_2.pozycja.voltage-0.780)*360/(3.946 - 0.780)):
##                        os.system("clear")
##                        #print("Silnik 1: \t{:>5.3f}".format((self.silnik_1.pozycja.voltage-0.780)*360/(3.946 - 0.780)))       #=========================================================
##                        #print("Silnik 2: \t{:>5.3f}".format((self.silnik_2.pozycja.voltage-0.780)*360/(3.946 - 0.780))
##                        print("Silnik 1: \t{:>5.3f}".format(AM1)
##                        print("Silnik 1: \t{:>5.3f}".format(AM2)                                                              #=MA RAZIE NIE DZIALA TRZEBA USTAWIC ODPOWIEDNIO ENKODERY=
##                        self.stara_pozycja_1 = (self.silnik_1.pozycja.voltage-0.780)*360/(3.946 - 0.780)                      #=WYSKALOWAC ENKODERY WZGLEDEM MOZLIWYCH OBROTOW MANIPU. =
##                        self.stara_pozycja_2 = (self.silnik_2.pozycja.voltage-0.780)*360/(3.946 - 0.780)                      #=ZEBY NIE BYLO W POLOWIE OBROTU RAMIENIA ZMIANY ODCZYTU =
##                    print("za metoda")                                                                                        #=Z 0 NA 2V.                                             =
##                                                                                                                              #=========================================================
                except Exception as e:
                    print(e)
                    pass

    def _run_in_thread2(self, func, predkosc): # Ta metoda sluzy dla silnikow
        thread = Thread(target=func, args=[predkosc])
        thread.start()
        
    def _run_in_thread(self, func): # Ta metoda jest gdzies w programie - klasa z niej korzysta gdzies tam
        print("przed watkiem 1")
        thread = Thread(target=func)
        thread.start()

if __name__ == '__main__':
    pad = X360controler()
    pad.Start()

