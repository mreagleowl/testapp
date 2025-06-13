# hover.py
# v0.4.9

from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
from kivy.core.window import Window

class HoverBehavior(object):
    hovered = BooleanProperty(False)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        self.hovered = inside
        if hasattr(self, 'on_enter') and inside:
            self.on_enter()
        elif hasattr(self, 'on_leave') and not inside:
            self.on_leave()
