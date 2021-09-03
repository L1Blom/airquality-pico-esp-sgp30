# Complete project details at https://RandomNerdTutorials.com

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import secrets
import wifimgr

#esp.osdebug(None)
import gc
gc.collect()

try:
  import usocket as socket
except:
  import socket

wlan = wifimgr.get_connection()

if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D

# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("ESP OK")

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

