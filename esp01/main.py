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
    esp_mqtt = ESP_mqtt(client_id,mqtt_server)
except OSError as e:
    esp_mqtt.restart_and_reconnect()

#print ("Waiting for uart switch")
#while esp_mqtt.state == "init":
#    esp_mqtt.client.check_msg()
#    time.sleep(1)

esp_mqtt.sub_cb(esp_mqtt.topic_mgt, b'uart')
uart = esp_mqtt.uart

while esp_mqtt.state == "uart":
    try:
        esp_mqtt.client.check_msg()
        if esp_mqtt.message != "":
            uart.write(esp_mqtt.message)
            esp_mqtt.message = ""            
        if uart.any():
            data = ""
            try:
                msg = str(uart.readline())
            except OSError as pico:
                esp_mqtt.client.publish(esp_mqtt.topic_mgt, pico)
            data = str(msg,'UTF-8')
            if data[:3] == "b'm":
                esp_mqtt.client.publish(esp_mqtt.topic_mgt, data)
            else:
                esp_mqtt.client.publish(esp_mqtt.topic_sub, data)
    except OSError as e:
        esp_mqtt.sub_cb(esp_mqtt.topic_sub, b'repl')
        print("Error: "+e)
#        esp_mqtt.restart_and_reconnect()
        
    time.sleep(0.5)

