import psycopg2 
import datetime
import subprocess
from time import sleep           
from gpiozero import LightSensor #light sensor library
import Adafruit_DHT              #Humidity, Temperature sensor library
import smtplib
import RPi.GPIO as GPIO          #General usage/Smoke sensor library

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

# Connect to PostgreSQL
conn = psycopg2.connect('dbname=rpi')
cur = conn.cursor()

def insert_log(date, humid, temp, light, smoke_l, smoke_r):
    query = """
    INSERT INTO
        sensors
    VALUES
        (%s, %s, %s, %s, %s, %s)
    """
    values = (date, humid, temp, light, smoke_l, smoke_r)
    cur.execute(query, values)

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
		#error_mail_sent = True
	elif(humidity > 70 or humidity < 25):
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
        
        # Check the amount of error mail PRi sent
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

        # Write to file
	log = open("log_record.txt", "a")
	log.write(f"\nHumidity    : {humidity} \nTemperature : {temperature} \nLight       : {round(ldr.value, 2)} \nSmoke       : {GPIO.input(2)}-{GPIO.input(26)} \n")
	log.close() 
	subprocess.run(["sh", "/home/pi/stato.sh"])
	
        # Write to PostgreSQL
	date = datetime.datetime.now()
	formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
        
	insert_log(formatted_date, humidity, temperature, round(ldr.value, 2), GPIO.input(2), GPIO.input(26)) 
	conn.commit()
	cur.execute('select * from sensors')
	results = cur.fetchall()
	for i in results:
		print(i)

