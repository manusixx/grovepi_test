import time
import grovepi

# Establece los pines a ser conectados
sound_sensor = 0
bombillopin = 4     # Simula prender el bonbillo. D4
buzzer = 8
relay =  3
numleds = 1  #Si solo se tiene un 1 LED, cabiar el valor a 1
# Establecer el modo de lectura y escritura de cada pin
grovepi.pinMode(sound_sensor,"INPUT")
grovepi.pinMode(bombillopin,"OUTPUT")
grovepi.pinMode(buzzer,"OUTPUT")
grovepi.pinMode(relay,"OUTPUT")

# The threshold to turn the led on 400.00 * 5 / 1024 = 1.95v
threshold_value = 215

print("inicia programa")
time.sleep(1)

# Chainable RGB LED methods
# grovepi.storeColor(red, green, blue)
# grovepi.chainableRgbLed_init(pin, numLeds)
# grovepi.chainableRgbLed_test(pin, numLeds, testColor)
# grovepi.chainableRgbLed_pattern(pin, pattern, whichLed)
# grovepi.chainableRgbLed_modulo(pin, offset, divisor)
# grovepi.chainableRgbLed_setLevel(pin, level, reverse)

# test colors used in grovepi.chainableRgbLed_test()
testColorBlack = 0   # 0b000 #000000
testColorBlue = 1    # 0b001 #0000FF
testColorGreen = 2   # 0b010 #00FF00
testColorCyan = 3    # 0b011 #00FFFF
testColorRed = 4     # 0b100 #FF0000
testColorMagenta = 5 # 0b101 #FF00FF
testColorYellow = 6  # 0b110 #FFFF00
testColorWhite = 7   # 0b111 #FFFFFF

# patterns used in grovepi.chainableRgbLed_pattern()
thisLedOnly = 0
allLedsExceptThis = 1
thisLedAndInwards = 2
thisLedAndOutwards = 3

sleep_time=0.5

#Turns off the led specified by led_num
def turn_off_led(led_num):
    grovepi.storeColor(0,0,0)
    time.sleep(.1)
    grovepi.chainableRgbLed_pattern(bombillopin, thisLedOnly, led_num)
    time.sleep(.1)
  
#Turns on the led specified by led_num to color set by r,g,b
def turn_on_led(led_num,r,g,b):
    grovepi.storeColor(r,g,b)
    time.sleep(.1)
    grovepi.chainableRgbLed_pattern(bombillopin, thisLedOnly, led_num)
    time.sleep(.1)

grovepi.chainableRgbLed_init(bombillopin, numleds)
time.sleep(.5)

while True:
  try:
     # Read the sound level
     print("Leyendo sensor de sonido")
     sensor_value = grovepi.analogRead(sound_sensor)
    
     if sensor_value > threshold_value:
         print("encender alarma")
         turn_on_led(0,0,255,0) # Turn Led On
         grovepi.digitalWrite(buzzer,1) #Turn Buzzer On
         grovepi.digitalWrite(relay,1) #Turn Relay on
     else:
    	 print("apagar alarma")
    	 turn_off_led(0)
    	 grovepi.digitalWrite(buzzer,0)
    	 grovepi.digitalWrite(relay,0)
   
     print("Lectura de sonido")
     print(sensor_value)
     time.sleep(1)
  
  except KeyboardInterrupt: # Turn LED off before stopping
      turn_off_led(0)
      grovepi.digitalWrite(buzzer,0)
      grovepi.digitalWrite(relay,0)
      break 
  except IOError: # Print "Error" if communication error encountered
      print ("Error")
