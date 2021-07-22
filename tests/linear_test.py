import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)

GPIO.setup(14, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)


a = True
while True:
	time.sleep(1)
	if a:
		GPIO.output(15, GPIO.LOW)
		GPIO.output(14, GPIO.HIGH)
	else:
		GPIO.output(15, GPIO.HIGH)	
		GPIO.output(14, GPIO.LOW)
	a = not a


GPIO.cleanup()
