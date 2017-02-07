from laropy.datalib import DataLib
from laropy.drawables import Drawable
from pyglet.image import Animation


class Layer:
    GROUND_FLOOR = 0
    GROUND = 1


class GameObject:
    def __init__(self, name, drawable: Drawable, width, height, env=None):
        self._env = env
        self.name = name
        self._attributes = []
        self.x = 0
        self.y = 0
        self.hitbox_width = width
        self.hitbox_length = height
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
        self.layer = Layer.GROUND

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

    def change_drawable(self, drawable):
        self._drawable = drawable

    def update(self, dt):
        if self._tick > 10000:
            self._tick = 0
        self._tick += 1

        for cmp in self.__component_list:
            cmp.update(self, dt)

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

    def has_collision(self, obj):
        return (self.top_hitbox > obj.top_hitbox > self.bottom_hitbox
                or self.top_hitbox > obj.bottom_hitbox > self.bottom_hitbox) \
                and (self.left_hitbox < obj.left_hitbox < self.right_hitbox
                     or self.left_hitbox < obj.right_hitbox < self.right_hitbox)

    @property
    def top_hitbox(self):
        return self.x + self.hitbox_length / 2

    @property
    def bottom_hitbox(self):
        return self.x - self.hitbox_length / 2

    @property
    def right_hitbox(self):
        return self.y + self.hitbox_width / 2

    @property
    def left_hitbox(self):
        return self.y - self.hitbox_width / 2

    def on_collision(self, obj):
        pass
