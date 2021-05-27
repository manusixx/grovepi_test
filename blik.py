import RPi.GPIO as GPIO
import time

print("Welcome")
print("Testing Led  out, Press CTRL+C to exit")

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #Broadcom pin-numbering
GPIO.setup(11, GPIO.OUT) #output led

try: 
    while True:
  	GPIO.output(11, 1) # set GPIO7 to 1/GPIO.HIGH/True
  	print("led on")
  	time.sleep(1)     
  	GPIO.output(11, 0) # set GPIO7 to 0/GPIO.LOW/False
  	print("led off") 
  	time.sleep(1)
except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()

