# v0.4.8
from kivy.properties import BooleanProperty, ListProperty
from kivy.core.window import Window

class HoverBehavior(object):
    hovered = BooleanProperty(False)
    hover_color = ListProperty([1, 0, 0, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            return
        self.hovered = inside
        if inside:
            self.on_enter()
        else:
            self.on_leave()

    def on_enter(self):
        pass

    def on_leave(self):
        pass
