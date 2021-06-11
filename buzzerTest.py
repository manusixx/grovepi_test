import time
import grovepi

buzzer = 8
relay = 3
 
grovepi.pinMode(buzzer,"OUTPUT")
grovepi.pinMode(relay,"OUTPUT")
 
while True:
    try:
        grovepi.digitalWrite(buzzer,1)
        grovepi.digitalWrite(relay,1)
        print("Encendidos")
        time.sleep(2)
        grovepi.digitalWrite(buzzer,0)
        grovepi.digitalWrite(relay,0)
 
    except KeyboardInterrupt: # Turn LED off before stopping
           grovepi.digitalWrite(buzzer,0)
           grovepi.digitalWrite(relay,0)
           break 
    except IOError: # Print "Error" if communication error encountered
           print ("Error")
