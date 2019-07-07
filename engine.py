import pigpio
import time
import json


class EngineDriver():

    engines_ready = False
    FREQUENCY = 500
    startup_time = 5
    STOP = 192

    old_min = -1
    old_max = 1
    new_max = 238 # when there are not transoptor values max and min shoud be 5 units higher
    new_min = 136
    set_dict = {"fl" : False, "fr" : False, "bl" : False, "br" : False,"vl" : False,"vr" : False,"vb" : False}
    old_dict = {"fl" : 187, "fr" : 187, "bl" : 187, "br" : 187, "vl" : 187, "vr" : 187, "vb" : 187}
    def __init__(self):
        self.engines_dict = {"fl" : 11, "fr" : 18, "bl" : 9, "br" : 25,"vl" : 10, "vr" : 23,"vb" : 24}
        #self._load_map_file()

        self.pi = pigpio.pi()
        print("Ustawianie silników")
        for val in self.engines_dict.values():
            print(val)
            self.pi.set_PWM_dutycycle(val, self.STOP)
            self.pi.set_PWM_frequency(val, self.FREQUENCY)
        time.sleep(5)
        self.engines_ready = True
        print("Silniki gotowe")
        #aby sterownik się zainicjował poprawnie, trzeba kila sekund dawać sygnał o wypełnieniu 75%
        # i okresie 2000us

    def __del__(self):
        for val in self.engines_dict.values():
            self.pi.set_PWM_dutycycle(val, self.STOP)
        self.pi.stop()

    def _load_map_file(self):
        try:
            dictionary = {}
            with open('engines_map.json', 'r') as _file:
                string = json.load(_file)
                dictionary = dict(string)
            self.engines_dict = dictionary
        except Exception as e:
            print(e)
            return

    def set_engines(self, dictionary):
        for key, val in dictionary.items():
            dictionary[key] = (((val - self.old_min) * (self.new_max - self.new_min)) / (self.old_max - self.old_min)) + self.new_min
        while True:
            for key, val in dictionary.items():
                if int(dictionary[key]) == int(self.old_dict[key]):
                    self.set_dict[key] = True
                elif dictionary[str(key)] < self.old_dict[str(key)]:
                    self.old_dict[key] = self.old_dict[key]-1
                elif dictionary[str(key)] > self.old_dict[str(key)]:
                    self.old_dict[key] = self.old_dict[key]+1
                self.pi.set_PWM_dutycycle(self.engines_dict[key],self.old_dict[key])
                #print(self.old_dict[key], dictionary[key])
                if all(is_set is True for is_set in self.set_dict.values()):
                    #print("all set")
                    for key in self.set_dict.keys():
                        self.set_dict[key] = False
                    return

if __name__ == '__main__':
    engine_driver = EngineDriver()

    eng = {"fl" : 205, "fr" : 205, "bl" : 205, "br" : 205, "vl" : 205, "vr" : 205, "vb" : 205}
    engine_driver.set_engines(eng) #w
    time.sleep(2)
    eng = {"fl" : 187, "fr" : 187, "bl" : 187, "br" : 187, "vl" : 187, "vr" : 187, "vb" : 187}
    engine_driver.set_engines(eng) #w
