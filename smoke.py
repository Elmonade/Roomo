from time import sleep
from gpiozero import InputDevice
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN)
GPIO.setup(26, GPIO.IN)
#smoke = InputDevice(14)
smoke1 = GPIO.input(2)
smoke2 = GPIO.input(26)

while True:
	if GPIO.input(2):
		print ("Port  1 is High")
	else:
		print ("Port 1 is Low")
	if GPIO.input(26):
		print ("Port 2 is High")
	else:
		print ("Port 2 is Low")
	print('-------------->')
	sleep(2)
