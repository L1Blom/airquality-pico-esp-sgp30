import machine
from machine import UART, Pin
import uos
from umqttsimple import MQTTClient

class ESP_mqtt:

    def __init__(self, client_id,server):
      self.topic_sub = b'SGP30'
      self.topic_mgt = b'SGP30_mgt'
      self.state = "init"
      self.uart = ""
      self.message = ""
      self.client = MQTTClient(client_id, server)
      self.client.set_callback(self.sub_cb)
      self.client.connect()
      self.client.subscribe(self.topic_mgt)
      print('Connected to %s MQTT broker, subscribed to %s topic' % (server, self.topic_mgt))

    def sub_cb(self,topic, msg):
      if topic == self.topic_mgt and msg == b'webrepl':
        print(self.topic_mgt+": repl connected to webrepl")
        import webrepl
        webrepl.start()
        uos.dupterm(None, 1)
        self.uart = UART(0,115200) # uart on uart1 with baud of 115200
        self.state = "webrepl"
      else:  
          if topic == self.topic_mgt and msg == b'repl':
            uos.dupterm(UART(0, 115200), 1)
            print(self.topic_mgt+": repl connected to repl")
            self.state = "repl"
          else:
              if topic == self.topic_mgt and msg == b'uart':
                print(self.topic_mgt+": repl connected to uart")
                uos.dupterm(None, 1)
                self.uart = UART(0, 115200)
                self.state = "uart"
              else:
                  if topic == self.topic_mgt and msg[:2] == b'm:':
                    print(self.topic_mgt+": message: "+msg.decode())
                    self.message = msg.decode()
        
    def restart_and_reconnect(self):
      print('Failed to connect to MQTT broker. Reconnecting...')
      time.sleep(10)
      machine.reset()

