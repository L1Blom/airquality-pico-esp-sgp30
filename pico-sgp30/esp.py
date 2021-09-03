from machine import UART
import machine
import _thread
import time


def ESP8266Webserver(HTMLFile):
    #Set variables
    recv=""
    recv_buf="" 
    uart = UART(1,115200) # uart on uart1 with baud of 115200
    # wifi credentials (if needed)
    wifi_ssid = ("HHweg")
    wifi_password = ("ditisleenblom")
    
    #Function to handle reading from the uart serial to a buffer
    def SerialRead(mode):
        SerialRecv = ""
        if mode == "0" :
            SerialRecv=str(uart.readline())
        else:
            SerialRecv=str(uart.read(mode))
        #replace generates less errors than .decode("utf-8")
        SerialRecv=SerialRecv.replace("b'", "")
        SerialRecv=SerialRecv.replace("\\r", "")
        SerialRecv=SerialRecv.replace("\\n", "\n")
        SerialRecv=SerialRecv.replace("'", "")
        return SerialRecv

    print ("Setting up Webserver...")
    time.sleep(2)
# Connect to wifi, this only needs to run once, ESP will retain the CWMODE and wifi details and reconnect after power cycle, leave commented out unless this has been run once.
    print ("  - Setting AP Mode...")
    uart.write('AT+CWMODE=1'+'\r\n')
    time.sleep(2)
    print ("  - Connecting to WiFi...")
    uart.write('AT+CWJAP="'+wifi_ssid+'","'+wifi_password+'"'+'\r\n')
    time.sleep(15)
    uart.write('AT+CIFSR'+'\r\n')
    print(uart.read())
    print ("  - Setting Connection Mode...")
    uart.write('AT+CIPMUX=1'+'\r\n')
    time.sleep(2)
    print ("  - Starting Webserver..")
    uart.write('AT+CIPSERVER=1,80'+'\r\n') #Start webserver on port 80
    time.sleep(2)
    print ("Webserver Ready!")
    print("")

    while True:
        while True:
            #read a byte from serial into the buffer
            recv=SerialRead(1)
            recv_buf=recv_buf+recv
                       
            if '+IPD' in recv_buf: # if the buffer contains IPD(a connection), then respond with HTML handshake
                HTMLFileObject = open (HTMLFile, "r")
                HTMLFileLines = HTMLFileObject.readlines()
                HTMLFileObject.close()
                uart.write('AT+CIPSEND=0,17'+'\r\n')
                time.sleep(0.1)
                uart.write('HTTP/1.1 200 OK'+'\r\n')
                time.sleep(0.1)
                uart.write('AT+CIPSEND=0,25'+'\r\n')
                time.sleep(0.1)
                uart.write('Content-Type: text/html'+'\r\n')
                time.sleep(0.1)
                uart.write('AT+CIPSEND=0,19'+'\r\n')
                time.sleep(0.1)            
                uart.write('Connection: close'+'\r\n')
                time.sleep(0.1)
                uart.write('AT+CIPSEND=0,2'+'\r\n')
                time.sleep(0.1)
                uart.write('\r\n')
                time.sleep(0.1)
                uart.write('AT+CIPSEND=0,17'+'\r\n')
                time.sleep(0.1)
                uart.write('<!DOCTYPE HTML>'+'\r\n')
                time.sleep(0.1)
                # After handshake, read in html file from pico and send over serial line by line with CIPSEND
                for line in HTMLFileLines:
                        cipsend=line.strip()
                        ciplength=str(len(cipsend)+2) # calculates byte length of send plus newline
                        uart.write('AT+CIPSEND=0,' + ciplength +'\r\n')
                        time.sleep(0.1)
                        uart.write(cipsend +'\r\n')
                        time.sleep(0.1) # The sleep commands prevent the send coming through garbled and out of order..
                uart.write('AT+CIPCLOSE=0'+'\r\n') # once file sent, close connection
                time.sleep(4)
                recv_buf="" #reset buffer
                
            

    
#Place in main code
website = ("/webpage.html") # this is the path to the html file on the pico filesystem
_thread.start_new_thread(ESP8266Webserver(website), ()) # starts the webserver in a _thread