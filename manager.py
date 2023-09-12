import socket
import selectors
import threading
import time

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from functools import partial

Builder.load_file('manager.kv')


class Manager(BoxLayout):

    image_box = ObjectProperty()

    conn = socket.socket()
    sel = selectors.DefaultSelector()
    stop_flag = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect_thread()

    def stop(self):
        pass

    def connect_thread(self):
        #if not (self.t_listen.is_alive()):
        self.t_connect = threading.Thread(target = self.__connect)
        self.t_connect.daemon = True
        self.t_connect.start()

    def __connect(self, address = ('127.0.0.1', 65003)):
        
        # Initiate connection
        while True:
            try:
                print ('Connecting to dial window...')
                # Connect to localhost socket
                self.conn.connect(address)
                self.conn.setblocking(False)
                print ('Connected to dial window')
                # Updating the image
                Clock.schedule_once(partial(self.update_image, 'images/williot.png'), 0)
                self.sel.register(self.conn, selectors.EVENT_READ, data = None)
                while not self.stop_flag:
                    events = self.sel.select(timeout = None) #this blocks
                    for key, mask in events:
                        self.__service_connection(key, mask)
                # Updating the image
                Clock.schedule_once(partial(self.update_image, 'images/no_opt.png'), 0)

            except Exception as e:
                print (f'Failed connecting to dial window: {e}')
                # Updating the image
                Clock.schedule_once(partial(self.update_image, 'images/connecting.png'), 0)
                # Wait for 2 seconds before retry
                time.sleep(2)
        
    def __service_connection (self, key, mask):
        # Receive data from dial window
        sock = key.fileobj
        data = int.from_bytes(sock.recv(1024), 'big')
        Clock.schedule_once(partial(self.data_callback, data), 0)

    def update_image(self, source, *args):
        self.image_box.source = source

    def data_callback(self, data=0, *args):
        '''
        Application logic should be implemented here. 
        The following are sample to update the image based on data received from dial window
        '''
        print (data)

        if data == 3 or data == 8:
            # Freshness
            # Updating the image
            Clock.schedule_once(partial(self.update_image, 'images/freshness.png'), 0)

        elif data == 1 or data == 6:
            # Carbon
            # Updating the image
            Clock.schedule_once(partial(self.update_image, 'images/carbon.png'), 0)

        elif data == 2 or data == 7:
            # Temperature
            # Updating the image
            Clock.schedule_once(partial(self.update_image, 'images/temperature.png'), 0)

        elif data == 4 or data == 9:
            # Food
            # Updating the image
            Clock.schedule_once(partial(self.update_image, 'images/food.png'), 0)

        elif data == 0 or data == 5 or data == 10:
            # Williot
            # Updating the image
            Clock.schedule_once(partial(self.update_image, 'images/williot.png'), 0)
