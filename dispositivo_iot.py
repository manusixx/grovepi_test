#Autor: Manuel Alejandro Pastrana
#Descripcion: Aplicacion para sistema de deteccion de intrusos por  variacion del sonido 
import time
import grovepi
import urllib2 as ul 
import json 
import os
import smtplib
import subprocess
from paho.mqtt import client as mqtt_client
# paquete del modulo de  email necesarios
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from subprocess import call

#Configuracion ThinSpeak
# Set de variables globales que permiten a los 15 segundos  tomar info y
# actualizar el channel cada 15 segundos
lastConnectionTime = time.time() #  ultima conexion
lastUpdateTime = time.time() #  ultima actualizacion 
postingInterval = 15 # Post de actualizacion
updateInterval = 15 # Update cada 15 segundos
writeAPIkey = "MGU4Q4CP8DDEBC0O"
channelID = "1413681"
# ThingSpeak server settings
url = "https://api.thingspeak.com/channels/"+channelID+"/bulk_update.json"
messageBuffer = []
#MQTT Server settings
broker="192.168.1.13"
port=1883
#topic ="dispositivo_IOT_Deteccion"
username = 'pi'
password = 'mpastrana'
# Establece los pines a ser conectados
sound_sensor = 0    # A0
bombillopin = 4     # D4
buzzer = 8          # D8 
relay =  3          # D3
numleds = 1  #Si solo se tiene un 1 LED, cabiar el valor a 1

#Configuracion de variables para el envio de correo
SMTP_USERNAME = 'dhrsolutions.sas@gmail.com'  # email que envia
SMTP_PASSWORD = 'H3yD0c2020'  # Pasword de la cuenta que envia
SMTP_RECIPIENT = 'alexander15950@gmail.com' # email que recibe
SMTP_SERVER = 'smtp.gmail.com'  # SMTP
SSL_PORT = 465 #Puerto para envio de correos

# Establecer el modo de lectura y escritura de cada pin
grovepi.pinMode(sound_sensor,"INPUT")
grovepi.pinMode(bombillopin,"OUTPUT")
grovepi.pinMode(buzzer,"OUTPUT")
grovepi.pinMode(relay,"OUTPUT")

# El umbral o threshold para encender el led  215.00 * 5 / 1024 = 1.05v
threshold_value = 355

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

#Metodo para conectar al servidor MQTT
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client("dispositivo_IOT_Deteccion")
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def getData():
    #Estableciendo que variables son Globales
    global sound
    global led
    global rel
    global buzz
    releer = True

    client = connect_mqtt()

    while releer:
              try:
                  #obtener valor sensor de sonido
                  sensor_value = grovepi.analogRead(sound_sensor)
                  print ("Lectura de sensor sonido = ")
                  print (sensor_value)
                  client.publish("sensorSonidoSalida",sensor_value)
                  
                  # si el umbral es superado se enciende la alarma
                  if sensor_value > threshold_value:
                     print ("encender alarma")
		     client.publish("sensorSonidoSalida",sensor_value)
         	     turn_on_led(0,0,255,0) # Enciende Led
		     client.publish("ledSalida",1)
                     grovepi.digitalWrite(buzzer,1) #Activa Buzzer
                     time.sleep(0.1)
                     grovepi.digitalWrite(buzzer,0) #Desactiva el Buzzer
                     client.publish("buzzerSalida",1)
         	     grovepi.digitalWrite(relay,1) #Activa Relay
		     time.sleep(0.1)
		     grovepi.digitalWrite(relay,0)
		     client.publish("relaySalida",1)
		     #Hace set de los valores del sensor y actuadores para enviarlos a thingSpeak
                     sound = sensor_value
		     led = 1
		     rel = 1
		     buzz = 1
                     time.sleep(0.1)
		     #Enviar email por deteccion de intruso 
                     p = subprocess.Popen(["runlevel"], stdout=subprocess.PIPE)
                     out, err=p.communicate()    # Conectar al servidor del email
                     if out[2] == '0':
                         print('Halt detected')
                         exit(0)
                     if out [2] == '6':
                         print('Shutdown detected')
                         exit(0)
                     print("Conectado al email")

                     # Create the container (outer) email message
                     TO = SMTP_RECIPIENT
                     FROM = SMTP_USERNAME
                     TEXT =  """El dispositivo a detectado un intruso en el cuarto."""
                     SUBJECT = """Alerta de seguridad."""
                     msg = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
                     
                     # Enviar email via Gmail
                     print("Sending the mail")
                     server = smtplib.SMTP_SSL(SMTP_SERVER, SSL_PORT)
                     server.login(SMTP_USERNAME, SMTP_PASSWORD)
                     server.sendmail(FROM, [TO], msg)
                     server.quit()
                     print("Mail sent")

                  else:
    	 	       print("apagar alarma")
                       client.publish("sensorSonidoSalida",sensor_value)
    	 	       turn_off_led(0)
		       client.publish("ledSalida",0)
    	 	       grovepi.digitalWrite(buzzer,0)
		       client.publish("buzzerSalida",0)
    	 	       grovepi.digitalWrite(relay,0)
		       client.publish("relaySalida",0)
		       #Valores capturados del sensor y actuadores a enviar a thingSpeak
                       sound = sensor_value
		       led = 0
                       rel = 0
		       buzz = 0

		       #Terminar bucle correctamente
	               releer = False 
              except:  
                     print ("Error en la lectura del sensor... volviendo a leer")
	             time.sleep(0.5)
    print ("led")
    print (led)                 
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
	sound, led, relay, buzzer = getData()
        print ("LED")
        print (led)

	message['field1'] = sound
	message['field2'] = led
	message['field3'] = relay
	message['field4'] = buzzer
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
