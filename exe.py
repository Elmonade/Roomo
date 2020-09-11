import subprocess
from time import sleep
#light sensor library
from gpiozero import LightSensor
#Humidity, Temperature sensor library
import Adafruit_DHT
import smtplib
#Smoke sensor library
import RPi.GPIO as GPIO

# Sending Email 
SMTP_SERVER = 'mx.tavanbogd.com'
SMTP_PORT = 587
GMAIL_USERNAME = 'student.u@tavanbogd.com'
GMAIL_PASSWORD = 'Albedo#1' 
sendTo = 'student.u@tavanbogd.com'
emailSubject = "Warning!"
emailContent_Light = "Light detected in server room!"
emailContent_Humid = "Humidity problem!"
emailContent_Temp  = "Temprature problem!"
emailContent_Smoke = "Abnormal amount of gas"
error_mail_sent = False

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

# GPIO 21 ---> Light sensor
ldr = LightSensor(21)

# GPIO 4 ---> Humidity, Temperature sensor
sensor = Adafruit_DHT.DHT11
pin = 4
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

#GPIO 2 and 26 ---> Smoke sensor
GPIO.setup(2, GPIO.IN)
GPIO.setup(26, GPIO.IN)

#def execute(error):
#	if error == 1:
#		sendmail(sendTo, emailSubject, emailContent_Light)
#	elif error == 2:
#		sendmail(sendmail, emailSubject, emailContent_Humid)
#	elif error == 3:
#		sendmail(sendmail, emailSubject, emailContent_Temp)
#	elif error == 4:
#		sendmail(sendmail, emailSubject, emailContent_Smoke)

cnt = 0 #count the amount mail RPi sent

while True:
	print("\nLight(Threshold = 0.6): ", round(ldr.value, 2))
	print("Humidity, Temperature : ", int(humidity), int(temperature))
	print("Smoke (Safe = 1)      : ", GPIO.input(2), GPIO.input(26))

	if(ldr.value > 0.6):
		#execute(1)
		print("\nLight detected, sending email...") 
		#subprocess.run(["sh", "write_to_file.sh"])
		sendmail(sendTo, emailSubject, emailContent_Light)
		print("Sent!")
		error_mail_sent = True
	elif(humidity > 70 or humidity < 30):
		#execute(2)
		print("\nHumidity problem, sending email...")
		sendmail(sendTo, emailSubject, emailContent_Humid)
		print("Sent!")
		error_mail_sent = True
	elif(temperature > 28 or temperature < 0):
		#execute(3)
		print("\nTemperature problem, sending email...")
		sendmail(sendTo, emailSubject, emailContent_Temp)
		print("Sent!")
		error_mail_sent = True
	elif(not GPIO.input(2) and not GPIO.input(26)):
		#execute(4)
		print("\nSmoke detected, sending email...")
		sendmail(sendTo, emailSubject, emailContent_Smoke)
		print("Sent!")
		error_mail_sent = True
	sleep(3)

	if(error_mail_sent):
	        cnt += 1
	        #print("\nPutting myself to sleep...zzz")
	        sleep(15)
	        #print("\nFunctional!")
	        error_mail_sent = False
	        if(cnt >= 2):
	            print("Turning off sensors \nShutting down system") 
	            #subprocess.run(["sh", "/home/pi/turnoff.sh"])
	            break
	else:
                cnt = 0

      
