from pyglet.image import Animation
from drawables import Drawable


class DataLibrary:
    def __init__(self):
        self.data_list = {}

    def add_data(self, component, field_name, data):
        self.data_list[field_name] = (data, id(component))

    def get_entry(self, field_name):
        return self.data_list[field_name][0]


class GameObject:
    def __init__(self, name, drawable: Drawable):
        self.name = name
        self.x = 0
        self.y = 0
        self._drawable = drawable
        self._drawable.x = self.x
        self._drawable.y = self.y
        self.dx = 0
        self.dy = 0
        self.data_lib = DataLibrary()
        self._component_list = []
        self._tick = 0
        self._max_tick = 10000

    def update(self, dt):
        if self._tick > 10000:
            self._tick = 0
        self._tick += 1

        for cmp in self._component_list:
            cmp.update(self, self._tick)

    def draw(self):
        self._drawable.draw()

    def resize(self, width, length):
        self._drawable.resize(width, length)

    def move(self, x, y):
        self.dy = y - self.y
        self.dx = x - self.x
        self.x = x
        self.y = y
        self._drawable.move(x, y)

    def move_offset(self, x, y):
        self.dy = y
        self.dx = x
        self.x += x
        self.y += y
        self._drawable.move_offset(x, y)

    def rotate(self, degrees):
        if isinstance(self._drawable, Animation):
            self._drawable.rotation = degrees

