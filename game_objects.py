from pyglet.image import Animation
from drawables import Drawable
from datalib import DataLib


class GameObject:
    def __init__(self, name, drawable: Drawable, env=None):
        self._env = env
        self.name = name
        self._attributes = []
        self.x = 0
        self.y = 0
        self._drawable = drawable
        self._drawable.x = self.x
        self._drawable.y = self.y
        self.dx = 0
        self.dy = 0
        self.data_lib = DataLib()
        self.__component_list = []
        self._tick = 0
        self._max_tick = 10000
        self.flagged_for_removal = False

    @property
    def env(self):
        return self._env

    def set_env(self, env):
        if env:
            for cpmnt in self.__component_list:
                cpmnt.set_env(env)
        self._env = env

    def has_attribute(self, attribute):
        return attribute in self._attributes

    def update(self, dt):
        if self._tick > 10000:
            self._tick = 0
        self._tick += 1

        for cmp in self.__component_list:
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

    def _add_component(self, component):
        if self.env:
            component.set_env(self.env)
        self.__component_list.append(component)

    def on_collision(self, obj):
        pass
