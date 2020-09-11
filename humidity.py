import json
import Adafruit_DHT
from time import sleep

# Can't refresh faster than 2sec

sensor = Adafruit_DHT.DHT11
pin = 4
while True:
	humid, temp = Adafruit_DHT.read_retry(sensor, pin)
	print(temp, humid)
	sleep(3)

#json file creation

logme = {"Temperature":"temp", "humid": "0.4" }

with open('logme.txt', 'w') as json_file:
    json.dump(logme, json_file)
    
