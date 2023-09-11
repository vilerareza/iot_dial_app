import math
import time
from itertools import cycle

from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from functools import partial

import socket
import selectors
from threading import Thread, Condition

Builder.load_file('dialbox.kv')


class DialBox(BoxLayout):

    manager = ObjectProperty(None)
    # Dial wheel image widget
    dial_image = ObjectProperty(None)
    # Selected legend image widget
    legend_image = ObjectProperty(None)
    # Set when the wheel is being moved
    moved = BooleanProperty(False)
    # The angle of the wheel. Initiated to 288 (the position where the no-option is rotated to 0 degree)
    theta = NumericProperty(288)
    # Adjusted theta to accomodate angle difference between images
    adjusted_theta = 0
    # Difference between current angle and the point of touch
    delta_theta = 0
    # Angle step for each segment
    segment_step = 36
    step_thresh = 0
    # Current option position (used to trigger the main app)
    option_pos = 0
    
    # Auto selection timeout in sec
    auto_selection_timeout = 300
    

    # Connections to app
    host = '0.0.0.0'
    port = 65003
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sel = selectors.DefaultSelector()
    stop_flag = False
    conn = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Start the listening socket from main app
        self.listen_thread()
        # Start the auto selection thread
        self.auto_select_thread()

    def __accept_wrapper(self,sock):
        # accept new connections
        self.conn, addr = sock.accept()
        self.cam_addr = addr[0]
        print ('accepted connection from ', addr)
        self.conn.setblocking(False)
        self.status = 'Connected'
        print (self.conn)

    def listen_thread(self):
        self.t_listen = Thread(target = self.__listen)
        self.t_listen.daemon = True
        self.t_listen.start()

    def __listen(self):
        self.lsock.bind((self.host,self.port))
        self.lsock.listen()
        print('listening on, ', (self.host,self.port))
        self.lsock.setblocking(False)
        self.sel.register(self.lsock, selectors.EVENT_READ, data = None)
        while not self.stop_flag:
            events = self.sel.select(timeout = None) #this blocks
            for key, _ in events:
                if key.data is None:
                    self.__accept_wrapper(key.fileobj)
                    

    def on_image_touch_move(self, *args):
        if args[0].collide_point(*args[1].pos):

            if args[0] == self.dial_image:
                #print (self.dial_image.center_x, self.dial_image.center_y)
                #print (*args[1].pos)
                x, y = args[1].pos
                delta_x = self.dial_image.center_x - x
                delta_y = self.dial_image.center_y - y
                theta_ = math.atan2(delta_y, delta_x)
                self.theta = int(theta_*(180/math.pi) + 180 - self.delta_theta + self.adjusted_theta)
                if self.theta < 0:
                    self.theta += 360
                elif self.theta > 360:
                    self.theta -= 360

                # print (f'theta move {self.theta}')

                self.dial_image.source = 'images/wheel.png'
                self.moved = True

                # Send data to socket
                # try:
                #     self.conn.send(self.theta.to_bytes(2, 'big'))
                # except Exception as e:
                #     pass


    def on_image_touch_down(self, *args):
        if args[0].collide_point(*args[1].pos):
            if args[0] == self.dial_image:
                x, y = args[1].pos
                delta_x = self.dial_image.center_x - x
                delta_y = self.dial_image.center_y - y
                theta_ = math.atan2(delta_y, delta_x)
                theta_ = int(theta_*(180/math.pi) + 180)
                if theta_ < 0:
                    theta_ += 360
                self.delta_theta = theta_ - self.theta
                if self.delta_theta < 0:
                    self.delta_theta += 360
                
                self.legend_image.opacity= 0
                #print (f'delta theta {self.delta_theta}' )


    def on_image_release(self, *args):

        # print (self.theta)
        if self.moved:

            if self.theta >=0 and self.theta <18-self.step_thresh:
                # Snap
                self.theta=0
                # Reset adjusted theta (offset)
                self.adjusted_theta = 0
                # Change the image
                self.dial_image.source = 'images/wheel_1.png'
                # Change the legend image
                self.legend_image.source = 'images/legend_wheel_1.png'
                self.legend_image.opacity= 1
                # Update position and send position data to socket
                self.option_pos = 0
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 1 {self.theta}')

            elif self.theta >=18+self.step_thresh and self.theta <54-self.step_thresh:
                # Snap
                self.theta = 36
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the image
                self.dial_image.source = 'images/wheel_5.png'
                # Change the legend image
                self.legend_image.source = 'images/legend_wheel_5.png'
                self.legend_image.opacity= 1
                # Update position and send position data to socket
                self.option_pos = 1
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 2 {self.theta}')

            elif self.theta >=54+self.step_thresh and self.theta <90-self.step_thresh:
                # Snap
                self.theta = 72
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*2
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the image
                self.dial_image.source = 'images/wheel_4.png'
                # Change the legend image
                self.legend_image.source = 'images/legend_wheel_4.png'
                self.legend_image.opacity= 1
                # Update position and send position data to socket
                self.option_pos = 2
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 3 {self.theta}')

            elif self.theta >=90+self.step_thresh and self.theta <126-self.step_thresh:
                # Snap
                self.theta = 108
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*3
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the image
                self.dial_image.source = 'images/wheel_3.png'
                self.legend_image.opacity= 0
                # Update position and send position data to socket
                self.option_pos = 3
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 4 {self.theta}')

            elif self.theta >=126+self.step_thresh and self.theta <162-self.step_thresh:
                # Snap
                self.theta = 144
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*4
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the image
                self.dial_image.source = 'images/wheel_2.png'
                # Change the legend image
                self.legend_image.source = 'images/legend_wheel_2.png'
                self.legend_image.opacity= 1
                # Update position and send position data to socket
                self.option_pos = 4
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 5 {self.theta}')

            elif self.theta >=162+self.step_thresh and self.theta <198-self.step_thresh:
                # Snap
                self.theta = 180
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*5
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the image
                self.dial_image.source = 'images/wheel_1.png'
                # Change the legend image
                self.legend_image.source = 'images/legend_wheel_1.png'
                self.legend_image.opacity= 1
                # Update position and send position data to socket
                self.option_pos = 5
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 6 {self.theta}')

            elif self.theta >=198+self.step_thresh and self.theta <234-self.step_thresh:
                # Snap
                self.theta = 216
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*6
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the image
                self.dial_image.source = 'images/wheel_5.png'
                # Change the legend image
                self.legend_image.source = 'images/legend_wheel_5.png'
                self.legend_image.opacity= 1
                # Update position and send position data to socket
                self.option_pos = 6
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 7 {self.theta}')

            elif self.theta >=234+self.step_thresh and self.theta <270-self.step_thresh:
                # Snap
                self.theta = 252
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*7
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the image
                self.dial_image.source = 'images/wheel_4.png'
                # Change the legend image
                self.legend_image.source = 'images/legend_wheel_4.png'
                self.legend_image.opacity= 1
                # Update position and send position data to socket
                self.option_pos = 7
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 8 {self.theta}')

            elif self.theta >=270+self.step_thresh and self.theta <306-self.step_thresh:
                # Snap
                self.theta = 288
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*8
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the image
                self.dial_image.source = 'images/wheel_3.png'
                self.legend_image.opacity= 0
                # Update position and send position data to socket
                self.option_pos = 8
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 9 {self.theta}')

            elif self.theta >=306+self.step_thresh and self.theta <342-self.step_thresh:
                # Snap
                self.theta = 324
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*9
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the image
                self.dial_image.source = 'images/wheel_2.png'
                # Change the legend image
                self.legend_image.source = 'images/legend_wheel_2.png'
                self.legend_image.opacity= 1
                # Update position and send position data to socket
                self.option_pos = 9
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 10 {self.theta}')

            elif self.theta >=342+self.step_thresh and self.theta <360-self.step_thresh:
                # Snap
                self.theta = 0
                # Offset the theta to produce continuous image
                self.adjusted_theta = 0
                # Change the image
                self.dial_image.source = 'images/wheel_1.png'
                # Change the legend image
                self.legend_image.source = 'images/legend_wheel_1.png'
                self.legend_image.opacity= 1
                # Update position and send position data to socket
                self.option_pos = 10
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta releaes 11 {self.theta}')

        self.moved = False


    def auto_select_thread(self):
        self.t_auto_select = Thread(target = self.__auto_select)
        self.t_auto_select.daemon = True
        self.t_auto_select.start()


    def __auto_select(self):

        # List of wheel thetas. Skip the no-option position
        theta__ = [0, 36, 72, 144, 180, 216, 252, 324]

        for theta_ in cycle(theta__):

            time.sleep(self.auto_selection_timeout)
            
            # Break when stopped
            if self.stop_flag:
                break

            # Check if wheel is being moved
            if self.moved:
                continue

            # Rotate the wheel to theta_   
            self.theta = theta_

            if self.theta >=0 and self.theta <18-self.step_thresh:
                # Reset adjusted theta (offset)
                self.adjusted_theta = 0
                # Change the wheel and legend image
                Clock.schedule_once(partial(self.update_images, 'images/wheel_1.png', 'images/legend_wheel_1.png'), 0)
                # Update position and send position data to socket
                self.option_pos = 0
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass

            elif self.theta >=18+self.step_thresh and self.theta <54-self.step_thresh:
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the wheel and legend image
                Clock.schedule_once(partial(self.update_images, 'images/wheel_5.png', 'images/legend_wheel_5.png'), 0)
                # Update position and send position data to socket
                self.option_pos = 1
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 2 {self.theta}')

            elif self.theta >=54+self.step_thresh and self.theta <90-self.step_thresh:
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*2
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the wheel and legend image
                Clock.schedule_once(partial(self.update_images, 'images/wheel_4.png', 'images/legend_wheel_4.png'), 0)
                # Update position and send position data to socket
                self.option_pos = 2
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 3 {self.theta}')

            elif self.theta >=126+self.step_thresh and self.theta <162-self.step_thresh:
                # Snap
                self.theta = 144
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*4
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the wheel and legend image
                Clock.schedule_once(partial(self.update_images, 'images/wheel_2.png', 'images/legend_wheel_2.png'), 0)
                # Update position and send position data to socket
                self.option_pos = 4
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 5 {self.theta}')

            elif self.theta >=162+self.step_thresh and self.theta <198-self.step_thresh:
                # Snap
                self.theta = 180
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*5
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the wheel and legend image
                Clock.schedule_once(partial(self.update_images, 'images/wheel_1.png', 'images/legend_wheel_1.png'), 0)
                # Update position and send position data to socket
                self.option_pos = 5
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 6 {self.theta}')

            elif self.theta >=198+self.step_thresh and self.theta <234-self.step_thresh:
                # Snap
                self.theta = 216
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*6
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the wheel and legend image
                Clock.schedule_once(partial(self.update_images, 'images/wheel_5.png', 'images/legend_wheel_5.png'), 0)
                # Update position and send position data to socket
                self.option_pos = 6
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 7 {self.theta}')

            elif self.theta >=234+self.step_thresh and self.theta <270-self.step_thresh:
                # Snap
                self.theta = 252
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*7
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the wheel and legend image
                Clock.schedule_once(partial(self.update_images, 'images/wheel_4.png', 'images/legend_wheel_4.png'), 0)
                # Update position and send position data to socket
                self.option_pos = 7
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 8 {self.theta}')

            elif self.theta >=306+self.step_thresh and self.theta <342-self.step_thresh:
                # Snap
                self.theta = 324
                # Offset the theta to produce continuous image
                self.adjusted_theta = self.segment_step*9
                theta_ = self.theta - self.adjusted_theta
                if theta_ < 0:
                    theta_ += 360
                self.theta = theta_
                # Change the wheel and legend image
                Clock.schedule_once(partial(self.update_images, 'images/wheel_2.png', 'images/legend_wheel_2.png'), 0)
                # Update position and send position data to socket
                self.option_pos = 9
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta release 10 {self.theta}')

            elif self.theta >=342+self.step_thresh and self.theta <360-self.step_thresh:
                # Snap
                self.theta = 0
                # Offset the theta to produce continuous image
                self.adjusted_theta = 0
                # Change the wheel and legend image
                Clock.schedule_once(partial(self.update_images, 'images/wheel_1.png', 'images/legend_wheel_1.png'), 0)
                # Update position and send position data to socket
                self.option_pos = 10
                try:
                    self.conn.send(self.option_pos.to_bytes(2, 'big'))
                except Exception as e:
                    pass
                # print (f'theta releaes 11 {self.theta}')


    def update_images(self, dial_img_source, legend_img_source, *args):
        # Change the image
        self.dial_image.source = dial_img_source
        # Change the legend image
        self.legend_image.source = legend_img_source
        self.legend_image.opacity= 1