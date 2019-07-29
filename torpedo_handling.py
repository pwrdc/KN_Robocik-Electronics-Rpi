import pigpio
import time
from logpy.LogPy import Logger

PWM_serwo = 23
reed_switch = 24
trigger = 25
en = 26

DELAY_AFTER_TRIGGER = 0.05 # delay between high and low state on trigger output in seconds
TIME_OF_INITIAL_ROTATION = 0.5 # time required to make one full rotation with max angle speed in seconds

FAST_ROTATION = 230 # you add/sub this to/from the neutral position
SLOW_ROTATION = 70 # same as above
NEUTRAL = 458


class TorpedoHandling:
    def __init__(self):
        self.pi = pigpio.pi()
        self.logger = Logger(filename='torpedoes_handling')

        if not self.pi.connected:
            self.logger.log("pi not connected", logtype='error')
            exit()

        self.logger.log("setup")
        self.setup()

    def setup(self):
        self.pi.set_mode(reed_switch, pigpio.INPUT)
        self.pi.set_mode(trigger, pigpio.OUTPUT)
        self.pi.set_mode(en, pigpio.OUTPUT)
        self.pi.write(en, 1)

        self.pi.set_PWM_frequency(PWM_serwo, 330)
        self.pi.set_PWM_range(PWM_serwo, 1000) # 270 max_cw, 730 max_ccw, 500 neutral
        self.pi.set_PWM_dutycycle(PWM_serwo, NEUTRAL)

    def initial_rotation(self):
        self.pi.set_PWM_dutycycle(PWM_serwo, NEUTRAL + FAST_ROTATION)
        time.sleep(TIME_OF_INITIAL_ROTATION)
        self.pi.set_PWM_dutycycle(PWM_serwo, NEUTRAL)

    def position(self):
        self.pi.set_PWM_dutycycle(PWM_serwo, NEUTRAL + FAST_ROTATION)
        while self.pi.read(reed_switch) == 0:
            pass
        self.pi.set_PWM_dutycycle(PWM_serwo, NEUTRAL + SLOW_ROTATION)
        while self.pi.read(reed_switch) == 1:
            pass
        self.pi.set_PWM_dutycycle(PWM_serwo, NEUTRAL - SLOW_ROTATION)
        while self.pi.read(reed_switch) ==  0:
            pass
        self.pi.set_PWM_dutycycle(PWM_serwo, NEUTRAL)

    def fire(self):
        self.pi.write(trigger, 1)
        time.sleep(DELAY_AFTER_TRIGGER)
        self.pi.write(trigger, 0)

    def stop(self):
        self.pi.set_PWM_dutycycle(PWM_serwo, NEUTRAL)
        self.pi.write(en, 0)

    def sequence(self):

        #self.pi.set_PWM_dutycycle(PWM_serwo, 300)

        self.logger.log("initial rotation")
        self.initial_rotation() # TODO move to __init__

        self.logger.log("position")
        self.position()

        self.logger.log("fire")
        self.fire()


        self.logger.log("stop")
        self.stop()

        self.logger.log("koniec")
        self.pi.set_PWM_dutycycle(PWM_serwo, 0)

        self.pi.stop()

if __name__ == "__main__":
    HANDLING = TorpedoHandling()
    HANDLING.sequence()
