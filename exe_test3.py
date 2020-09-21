# test3 is a modified version of test2:
# a) tried to catch specific errors in each logging method
# b) without condition writes log to file in the begining of time interval
# <Final version!>

import sys
import socket                       
import smtplib                        
import datetime
import psycopg2                 
import subprocess                    
import Adafruit_DHT                 # Humidity, Temperature sensor library
import RPi.GPIO as GPIO             # Smoke sensor library / General usage
from   gpiozero import LightSensor  # light sensor library
from   time     import sleep

# Sending Email 
SMTP_SERVER              = 'mx.tavanbogd.com'
SMTP_PORT                =  587
GMAIL_USERNAME           = 'student.u@tavanbogd.com'
GMAIL_PASSWORD           = 'Albedo#1' 
sendTo                   = 'student.u@tavanbogd.com'
emailSubject             = "Warning!"
emailContent_Light       = "Light detected in server room!"
emailContent_Humid       = "Humidity problem!"
emailContent_Temp        = "Temprature problem!"
emailContent_Smoke       = "Abnormal amount of gas"
emailContent             = "Not sure what's wrong..."

cnt                      = 0           # count the amount mail RPi sent
L_sensor                 = False
H_sensor                 = False
T_sensor                 = False
S_sensor                 = False

# GPIO 21                =  Light sensor
ldr                      = LightSensor(21)

# GPIO 4                 = Humidity, Temperature sensor
sensor                   = Adafruit_DHT.DHT11
pin                      = 4
humidity, temperature    = Adafruit_DHT.read_retry(sensor, pin)

#GPIO 2 and 26           = Smoke sensor
GPIO.setup(2, GPIO.IN)
GPIO.setup(26, GPIO.IN)

# Function to execute query on PostgreSQL
def insert_log(date, humid, temp, light, smoke_l, smoke_r):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect('dbname=rpi')
        cur = conn.cursor()
        # Query to execute 
        query = """
        INSERT INTO
            sensors
        VALUES
            (%s, %s, %s, %s, %s, %s)
        """
        values = (date, humid, temp, light, smoke_l, smoke_r)
        cur.execute(query, values)
        conn.commit()
    except(psycopg2.OperationalError):
         print("Couldn't connect to Postgre database, check connection details")
    except:
        print(sys.exc_info())

# Function to write log to file
def write_file():
    log = open("log_record.txt", "a")
    log.write(f"\nHumidity    : {humidity} \nTemperature : {temperature} \nLight       : {round(ldr.value, 2)} \nSmoke       : {GPIO.input(2)}-{GPIO.input(26)} \n")
    log.close() 
    subprocess.run(["sh", "/home/pi/stato.sh"])

# Fucntion to send email
def sendmail(recipient, subject, content):
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient, "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers) 
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit

interval = 5
# Main loop
while True:
	print(f"\n<wait '{interval}' sec>")
	sleep(interval)
        # writes log to file
	try:
	    write_file()
	except(PermissionError):
            print("User doesn't have a access to text file.")
	except:
            print("Unable to write to file!")

	print("\nLight(Threshold = 0.6): ", round(ldr.value, 2))
	print("Humidity, Temperature : ", int(humidity), int(temperature))
	print("Smoke (Safe = 1)      : ", GPIO.input(2), GPIO.input(26))

	if(ldr.value > 0.6):
		print("\nLight detected") 
		#error_detected = True
		L_sensor = True
	if(humidity > 70 or humidity < 20):
		print("\nHumidity problem")
		#error_detected = True
		H_sensor = True
	if(temperature > 28 or temperature < 0):
		print("\nTemperature problem")
		#error_detected = True
		T_sensor = True
	if(not GPIO.input(2) and not GPIO.input(26)):
		print("\nSmoke detected")
		#error_detected = True
		S_sensor = True

        # if any of the sensors triggered
	if(L_sensor or H_sensor or T_sensor or S_sensor):
                # if RPi sent more than 2 email at one interval
                if(cnt >= 2):
                    # write to PostgreSQL
                    date = datetime.datetime.now()
                    formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
                    insert_log(formatted_date, humidity, temperature, round(ldr.value, 2), GPIO.input(2), GPIO.input(26)) 
                        
                    T_sensor = H_sensor = S_sensor = L_sensor = False
                    continue     
                # if the mail count is less than 2
                else:
                    # Sending mail might cause error so error handling is added
                    try:
                        if(L_sensor):
                            sendmail(sendTo, emailSubject, emailContent_Light)
                        if(H_sensor):
                            sendmail(sendTo, emailSubject, emailContent_Humid)
                        if(T_sensor):
                            sendmail(sendTo, emailSubject, emailContent_Temp)
                        if(S_sensor):
                            sendmail(sendTo, emailSubject, emailContent_Smoke)
                        print("Sent email!")
                    except(socket.gaierror):
                        print("Sending email failed, check internet connection!")
                    except:
                        print("Unable to send email!")

                    cnt += 1
                    T_sensor = H_sensor = S_sensor = L_sensor = False
        # if none of the sensors are triggered
        # clear the counter for error email
	else:
                cnt = 0
