import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

GPIO.output(15, GPIO.HIGH)

pwm = GPIO.PWM(21, 400)

pwm.start(10)

a = True
while True:
	time.sleep(1)
	if a:
		GPIO.output(15, GPIO.LOW)
	else:
		GPIO.output(15, GPIO.HIGH)	
	a = not a

pwm.stop(0)

GPIO.cleanup()
