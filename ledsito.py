#Autor: Manuel Alejandro Pastrana
#Descripcion: Aplicacion para sistema de deteccion de intrusos por  variacion del sonido 
import time
import grovepi
import urllib2 as ul 
import json 
import os

#Configuracion ThinSpeak
# Set de variables globales que permiten a los 15 segundos  tomar info y
# actualizar el channel cada 2 minutos
lastConnectionTime = time.time() #  ultima conexion
lastUpdateTime = time.time() #  ultima actualizacion 
postingInterval = 15 # Post de actualizacion
updateInterval = 15 # Update cada 15 segundos
writeAPIkey = "MGU4Q4CP8DDEBC0O"
channelID = "1413681"
# ThingSpeak server settings
url = "https://api.thingspeak.com/channels/"+channelID+"/bulk_update.json"
messageBuffer = []

# Establece los pines a ser conectados
sound_sensor = 0    # A0
bombillopin = 4     # D4
buzzer = 8          # D8 
relay =  3          # D3
numleds = 1  #Si solo se tiene un 1 LED, cabiar el valor a 1

# Establecer el modo de lectura y escritura de cada pin
grovepi.pinMode(sound_sensor,"INPUT")
grovepi.pinMode(bombillopin,"OUTPUT")
grovepi.pinMode(buzzer,"OUTPUT")
grovepi.pinMode(relay,"OUTPUT")

# El umbral o threshold para encender el led  215.00 * 5 / 1024 = 1.05v
threshold_value = 200

print("inicia programa")
time.sleep(1)


# patterns used in grovepi.chainableRgbLed_pattern()
thisLedOnly = 0
allLedsExceptThis = 1
thisLedAndInwards = 2
thisLedAndOutwards = 3

#Metodo que permite encender el led
def turn_off_led(led_num):
    grovepi.storeColor(0,0,0)
    time.sleep(.1)
    grovepi.chainableRgbLed_pattern(bombillopin, thisLedOnly, led_num)
    time.sleep(.1)
  
#metodo que permite apagar el led
def turn_on_led(led_num,r,g,b):
    grovepi.storeColor(r,g,b)
    time.sleep(.1)
    grovepi.chainableRgbLed_pattern(bombillopin, thisLedOnly, led_num)
    time.sleep(.1)

#metodo que conecta al servidor thingSpeak
def httpRequest(): 
    global messageBuffer 
    data = json.dumps({'write_api_key': writeAPIkey,'updates': messageBuffer}) # Format the json data buffer 
    req = ul.Request(url = url) 
    requestHeaders = {"User-Agent":"mw.doc.bulk-update (Raspberry Pi)","Content-Type":"application/json","Content-Length":str(len(data))} 
    for key,val in requestHeaders.iteritems(): # Set the headers
            req.add_header(key,val) 
    req.add_data(data) # Add the data to the request
    # Make the request to ThingSpeak
    try: 
           response = ul.urlopen(req) # Make the request print 
           response.getcode() # A 202 indicates that the server has accepted the request
    except ul.HTTPError as e: 
            print e.code # Print the error code 
    messageBuffer = [] # Reinitialize the message buffer global 
    lastConnectionTime = time.time() # Update the connection time

def getData():
    #Estableciendo que variables son Globales
    global sound 
    global led
    global relay
    global buzzer
    
    releer = True
    
    while releer: 
              try:
                  print("Inicia el sistema")
    		  # Obtener valor sensor de sonido
                  sensor_value = grovepi.analogRead(sound_sensor)
                  print ("Lectura de sensor sonido = ")
                  print (sensor_value)

                  # si el umbral es superado se enciende la alarma
                  if sensor_value > threshold_value:
                     print("encender alarma")
         	     turn_on_led(0,0,255,0) # Enciende Led 
         	     grovepi.digitalWrite(buzzer,1) #Activa Buzzer
         	     grovepi.digitalWrite(relay,1) #Activa Relay
		     #Hace set de los valores del sensor y actuadores para enviarlos a thingSpeak
                     sound = sensor_value
		     led = 1
		     relay = 1
		     buzzer = 1
                     time.sleep(0,1)
  		  
                  else:
    	 	       print("apagar alarma")
    	 	       turn_off_led(0)
    	 	       grovepi.digitalWrite(buzzer,0)
    	 	       grovepi.digitalWrite(relay,0)
		       sound = sensor_value
		       led = 0
                       relay = 0
		       buzzer = 0

		       #Terminar bucle correctamente
	               releer = False 
              except:  
                     print ("Error en la lectura del sensor... volviendo a leer")
	             time.sleep(0.5)

    return sound, led, relay, buzzer

#metodo que actualiza el JSON para enviar la info a ThigSpeak
def updatesJson():
	'''Function to update the message buffer every 15 seconds with data. And then call the httpRequest 
	function every 2 minutes. This examples uses the relative timestamp as it uses the "delta_t" parameter. 
	If your device has a real-time clock, you can also provide the absolute timestamp using the "created_at" parameter.
	'''

	global lastUpdateTime
	message = {}
	message['delta_t'] = int(round(time.time() - lastUpdateTime))
	Sound_Sensor,RGB_Led, Relay, Buzzer = getData()
	message['field1'] = Sound_Sensor
	message['field2'] = RGB_Led
	message['field3'] = Relay
	message['field4'] = Buzzer
	global messageBuffer
	messageBuffer.append(message)
        # If posting interval time has crossed 2 minutes update the ThingSpeak channel with your data
	if time.time() - lastConnectionTime >= postingInterval:
		httpRequest()
	lastUpdateTime = time.time()

grovepi.chainableRgbLed_init(bombillopin, numleds)
time.sleep(.5)

if __name__ == "__main__": # To ensure that this is run directly and does not run when imported
	while True:
  		try: 
                     if time.time() - lastUpdateTime >= updateInterval:
	  		print("========================================") 
	  		print("Enviando datos a ThinkSpeak...") 
          		updatesJson()
       		     
                     else: 
                         getData()
                         time.sleep(0.5)
 
  		except KeyboardInterrupt: # Turn LED off before stopping
      		       turn_off_led(0)
      		       grovepi.digitalWrite(buzzer,0)
      		       grovepi.digitalWrite(relay,0)
     		       break 
  		except IOError: # Print "Error" if communication error encountered
      			print ("Error")
