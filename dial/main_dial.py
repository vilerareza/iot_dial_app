from kivy.app import App
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.properties import ObjectProperty, BooleanProperty

from manager_dial import Manager


class DialApp(MDApp):
    
    manager = ObjectProperty(None)
    stop_flag = BooleanProperty(False)

    def __init__(self, rot_angle, **kwargs):
        super().__init__(**kwargs)
        self.rot_angle = rot_angle

    def build(self):
        Window.minimum_width, Window.minimum_height = (500, 500)
        # Window.fullscreen = 'auto'
        Window.rotation = self.rot_angle
        self.icon = 'images/icon.png'
        self.manager = Manager()
        return self.manager
    
    def on_stop(self):
        self.stop_flag = True
        self.manager.stop()


def main(rot_angle):
    DialApp(rot_angle=rot_angle).run()


if __name__ == '__main__':

    # Rotation angle
    dial_rot = 0

    # Run
    main(rot_angle=dial_rot)