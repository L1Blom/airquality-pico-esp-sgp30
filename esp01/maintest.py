# Complete project details at https://RandomNerdTutorials.com
from machine import UART, Pin
import uos
import select
from esp_mqtt import ESP_mqtt

def SerialRead(mode=1):
  SerialRecv = ""
  if mode == 0 :
     SerialRecv=str(uart.readline())
  else:
     SerialRecv=str(uart.read(mode))
  return SerialRecv

try:
  esp_mqtt = ESP_mqtt(client_id)
except OSError as e:
  esp_mqtt.restart_and_reconnect()

uos.dupterm(None, 1)
uart = UART(0,115200) # uart on uart1 with baud of 115200
i=100
while i>0:
    
  try:
    esp_mqtt.client.check_msg()
    if (time.time() - last_message) > message_interval:
      msg = b'Hello #%d' % counter
      #print(msg)
      try:
          msg = SerialRead(0)
          print(msg)
      except OSError as pico:
          print(pico)
      esp_mqtt.client.publish(esp_mqtt._topic_sub, msg)
      last_message = time.time()
      counter += 1
      i=i-1
  except OSError as e:
    esp_mqtt.restart_and_reconnect()


