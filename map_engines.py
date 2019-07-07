import pigpio
import time
import json

def map_engine():
    frequency = 500
    startup_time = 5
    stop = 187
    engines_dict = {"fl": 12, "fr": 26, "bl": 19, "br": 16, "vl": 13, "vr": 20, "vb": 21}
    engines_list = [12, 26, 19, 16, 13, 20, 21]
    new_dict = {}
    pi = pigpio.pi()
    print("Setting engines")
    for val in engines_dict.values():

        pi.set_PWM_dutycycle(val, stop)
        pi.set_PWM_frequency(val, frequency)

    time.sleep(startup_time)
    engines_ready = True
    print("Engines ready")

    for pin in engines_list:
        while True:
            pi.set_PWM_dutycycle(pin, 202)
            position = input("Which engine is it? 'fl', 'fr', 'bl', 'br', 'vl', 'vr', 'vb'")
            if (position not in engines_dict.keys()) or (position in new_dict.keys()):
                print("Try again")
            else:
                pi.set_PWM_dutycycle(pin, stop)
                new_dict[position] = pin
                break

    print("All set. Thanks!")
    with open('engines_map.json', 'w') as _file:
        json.dump(engines_dict, _file)

if __name__ == '__main__':
    map_engine()
