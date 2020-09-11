import subprocess
from time import sleep
import smtplib
from gpiozero import LightSensor  #light sensor library
import Adafruit_DHT               #Humidity, Temperature sensor library
import RPi.GPIO as GPIO           #Smoke sensor library

# Sending Email 
SMTP_SERVER        = 'mx.tavanbogd.com'
SMTP_PORT          =  587
GMAIL_USERNAME     = 'student.u@tavanbogd.com'
GMAIL_PASSWORD     = 'Albedo#1' 
sendTo             = 'student.u@tavanbogd.com'
emailSubject       = "Warning!"
emailContent_Light = "Light detected in server room!"
emailContent_Humid = "Humidity problem!"
emailContent_Temp  = "Temprature problem!"
emailContent_Smoke = "Abnormal amount of gas"
emailContent       = "Not sure what's wrong..."

def sendmail(recipient, subject, content):
        #Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient, "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit

# GPIO 21                      ---> Light sensor
ldr = LightSensor(21)

# GPIO 4                       ---> Humidity, Temperature sensor
sensor = Adafruit_DHT.DHT11
pin = 4
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

#GPIO 2 and 26                 ---> Smoke sensor
GPIO.setup(2, GPIO.IN)
GPIO.setup(26, GPIO.IN)

cnt = 0                        # count the amount mail RPi sent
error_detected = False         # check the errors(True if error detected)

while True:
	sleep(5)
	print("\nLight(Threshold = 0.6): ", round(ldr.value, 2))
	print("Humidity, Temperature : ", int(humidity), int(temperature))
	print("Smoke (Safe = 1)      : ", GPIO.input(2), GPIO.input(26))

	if(ldr.value > 0.6):
		print("\nLight detected") 
		#error_detected = True
		error_number = 1
	elif(humidity > 70 or humidity < 20):
		print("\nHumidity problem")
		error_detected = True
		error_number = 10
	elif(temperature > 28 or temperature < 0):
		print("\nTemperature problem")
		error_detected = True
		error_number = 11
	elif(not GPIO.input(2) and not GPIO.input(26)):
		print("\nSmoke detected")
		error_detected = True
		error_number = 100

	if(error_detected):
                if(cnt >= 2):
                    # write to PostgreSQL
                    error_detected = False
                    continue     
                else:
                    #if(error_number)
                    #sendmail(sendTo, emailSubject, emailContent)
                    print("Sent email!")
                    cnt += 1
                    error_detected = False
	else:
                cnt = 0
