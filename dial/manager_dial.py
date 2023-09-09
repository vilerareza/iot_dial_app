import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp
from dialbox import DialBox

Builder.load_file('manager_dial.kv')

class Manager(BoxLayout):

    dial_box = ObjectProperty()

    def stop(self):
        self.dial_box.stop_flag = True