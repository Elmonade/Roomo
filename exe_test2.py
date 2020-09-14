import datetime
import psycopg2
import subprocess
import smtplib
import Adafruit_DHT                 # Humidity, Temperature sensor library
import RPi.GPIO as GPIO             # Smoke sensor library
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
#error_detected          = False       # check the errors(True if error detected)
#error_type              = 0           # identify the error using code
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

# Connect to PostgreSQL
conn                     = psycopg2.connect('dbname=rpi')
cur                      = conn.cursor()

def insert_log(date, humid, temp, light, smoke_l, smoke_r):
    query = """
    INSERT INTO
        sensors
    VALUES
        (%s, %s, %s, %s, %s, %s)
    """
    values = (date, humid, temp, light, smoke_l, smoke_r)
    cur.execute(query, values)

# Fucntion to send email
def sendmail(recipient, subject, content):
        # Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient, "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        # Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
        # Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        # Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit

# Main loop
while True:
	print("\n<---Wait for 5sec--->\n")
	sleep(5)
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

	if(L_sensor or H_sensor or T_sensor or S_sensor):
                if(cnt >= 2):
                    # write to PostgreSQL
                    date = datetime.datetime.now()
                    formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
                    insert_log(formatted_date, humidity, temperature, round(ldr.value, 2), GPIO.input(2), GPIO.input(26)) 
                    conn.commit()
                    print("Wrote to PostgreSQL!")

                    T_sensor = H_sensor = S_sensor = L_sensor = False
                    continue     
                else:
                    # Use try-except block here
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
                    except:
                        print("Unable to send email!\nWriting to File...")
                        # Write to file
                        log = open("log_record.txt", "a")
                        log.write(f"\nHumidity    : {humidity} \nTemperature : {temperature} \nLight       : {round(ldr.value, 2)} \nSmoke       : {GPIO.input(2)}-{GPIO.input(26)} \n")
                        log.close() 
                        subprocess.run(["sh", "/home/pi/stato.sh"])

                    cnt += 1
                    T_sensor = H_sensor = S_sensor = L_sensor = False
	else:
                cnt = 0
