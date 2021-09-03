"""
 From https://github.com/L1Blom
 My first experiment with a Pico
 Combo: ESP-01, Raspberry Pico and Adafruit SGP30
 Result: air quality sensor
 Putting measurements on mqtt (by ESP-01)
"""
from machine import UART
from machine import I2C
import machine
import _thread
import time
import adafruit_sgp30
import gc

gc.enable() # we really need this on a Pico!

#Set variables
output = "" # used to send measurements of sensor
inmgt  = "" # used to receive management info

#Function to handle reading from the uart serial to a buffer
uart = UART(1,115200) # uart on uart1 with baud of 115200

# We create a semaphore (A.K.A lock) to message between threads
baton = _thread.allocate_lock()

# Reads the uart 
def SerialRead(mode=1):
    SerialRecv = ""
    with baton: # thread safe
        if mode == 0 :
            SerialRecv=str(uart.readline())
        else:
            SerialRecv=str(uart.read(mode))
    return SerialRecv

# in thread we send the output and read from outside world
def ServerLoop():
    global output, inmgt
    while True: # Loop always
        with baton: # lock
            try:
                if output != "": # buffer to put on uart
                    uart.write(output)
                    output = "" # clear buffer to prevent sending multiple times
            except OSError as e:
                print("Error: "+str(e)) # no one will see this, but loop continues
        if uart.any(): # read any command from ESP
            inmgt = SerialRead(0)
        time.sleep(0.1)

_thread.start_new_thread(ServerLoop, ()) # starts the webserver in a _thread

"""
Example for using the SGP30 with MicroPython and the Adafruit library.

Uses instructions from "SGP30 Driver Integration (for Software I²C)" to handle
self-calibration of the sensor:
    - if no baseline found, wait 12h before storing baseline,
    - if baseline found, store baseline every hour.

Baseline is writen in co2eq_baseline.txt and tvoc_baseline.txt.

Note that if the sensor is shut down during more than one week, then baselines
must be manually deleted.
"""

i2c = I2C(0,scl=machine.Pin(9), sda=machine.Pin(8),  freq=100000)

# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

# Initialize SGP-30 internal drift compensation algorithm.
sgp30.iaq_init()
# Wait 15 seconds for the SGP30 to properly initialize
time.sleep(15)

# Retrieve previously stored baselines, if any (helps the compensation algorithm).
has_baseline = False
try:
    f_co2 = open('co2eq_baseline.txt', 'r')
    f_tvoc = open('tvoc_baseline.txt', 'r')

    co2_baseline = int(f_co2.read())
    tvoc_baseline = int(f_tvoc.read())
    #Use them to calibrate the sensor
    sgp30.set_iaq_baseline(co2_baseline, tvoc_baseline)

    f_co2.close()
    f_tvoc.close()

    has_baseline = True
    output = "m:"+"Baselines used"
except:
    print('Impossible to read SGP30 baselines!') # informational

#Store the time at which last baseline has been saved
baseline_time = time.time()
counter = 0

try:
    while True: # loop always
        mem = gc.mem_alloc()
        if mem>20000: # if memory fills up, collect unused space
            output = "m:"+str(mem)+":"+str(counter) # report how many cyclus can be done without gc.collect()
            gc.collect()
            time.sleep(0.5)
            if counter == 1:
                output = "m:"+"Memory full, reset Pico!"
                time.sleep(3)   # wait a few seconds to let the message being send
                machine.reset() # apparently the memory doesn't shrink anymore
            counter = 0 # reset the counter
        else:
            counter = counter + 1 # update counter

        with baton:
            if inmgt != "": # read the commands from ESP, if any
               #print("Message in: "+inmgt)
               output = "m:"+inmgt
               time.sleep(1)
               if inmgt == b'm:reset-pico':
                  machine.reset() # reboot on request
               inmgt = ""
        with baton:
            co2eq, tvoc = sgp30.iaq_measure()
            #print('co2eq = ' + str(co2eq) + ' ppm \t tvoc = ' + str(tvoc) + ' ppb')

            # Baselines should be saved after 12 hour the first timen then every hour,
            # according to the doc.
            if (has_baseline and (time.time() - baseline_time >= 3600)) \
                    or ((not has_baseline) and (time.time() - baseline_time >= 43200)):

                #print('Saving baseline!')
                baseline_time = time.time()

                try:
                    f_co2 = open('co2eq_baseline.txt', 'w')
                    f_tvoc = open('tvoc_baseline.txt', 'w')

                    bl_co2, bl_tvoc = sgp30.get_iaq_baseline()
                    f_co2.write(str(bl_co2))
                    f_tvoc.write(str(bl_tvoc))

                    f_co2.close()
                    f_tvoc.close()

                    has_baseline = True
                    output = "m:"+"Baselines saved"
                except:
                    output = "m:"+"Baselines couldn't saved"
                    print('Impossible to write SGP30 baselines!')
                time.sleep(1)

            #A measurement should be done every 60 seconds, according to the doc.
            try:
                output = "t:"+str(co2eq)+':'+str(tvoc) # fill output buffer
                #print("Sending: "+output)
            except Exception as e:
                #print("Error: "+str(e.__class__))
                output = "m:"+str(e.__class__)
        time.sleep(1)
except Exception as e: # let us hope we never come here, has to repower 
    output = "m:"+str(e.__class__)
    filename = "error.txt"
    file = open(filename, "w")
    file.write("Error: "+str(e.__class__))
    file.write(str(e))
    file.close()
    #print("Error: "+str(e.__class__))
 


