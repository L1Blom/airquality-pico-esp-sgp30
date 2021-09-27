# Complete project details at https://RandomNerdTutorials.com

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import secrets

#esp.osdebug(None)
import gc
gc.collect()

ssid = secrets.ssid
password = secrets.password
mqtt_server = secrets.mqtt_server
client_id = ubinascii.hexlify(machine.unique_id())

last_message = 0
message_interval = 1
counter = 0

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

