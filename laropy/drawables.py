import math
import pyglet
from pyglet.image import AnimationFrame, Animation


class GLShape:
    def draw(self):
        raise NotImplementedError


class Rectangle(GLShape):
    def __init__(self, left_x, top_y, length, width):
        self.x = left_x
        self.y = top_y
        self._length = length
        self._width = width

    def draw(self):
        pyglet.graphics.vertex_list(4, ('v2f', [self.x, self.y,
                                                self.x + self._width, self.y,
                                                self.x + self._width, self.y + self._length,
                                                self.x, self.y + self._length]))


class Drawable:
    def __init__(self, width, length):
        self.x = 0
        self.y = 0
        self._length = width
        self._width = length

    def draw(self):
        pass

    @property
    def length(self):
        return self._length

    @property
    def width(self):
        return self._width

    def resize(self, width, length):
        self._length = width
        self._width = length

    def move(self, x, y):
        self.x = x
        self.y = y

    def move_offset(self, x, y):
        self.x += x
        self.y += y


class GLDrawnDrawable(Drawable):
    def __init__(self, width, length):
        super().__init__(width, length)
        self.shape_list = []

    def add_shape(self, shape: GLShape):
        self.shape_list.append(shape)


def init_empty_gen():
    yield


class ZeroDistanceError(Exception):
    message = "Distance is zero."


class DrawableRotationSetting:
    STATIC = 0
    ANGULAR = 3


class AnimatedDrawable(Drawable):
    DEFAULT_ANIMATION_DURATION = 0.25
    test_int = 0

    def __init__(self, sprite_sheet_filepath, coordinates, width, length, scale=1,
                 rotation_setting=DrawableRotationSetting.STATIC, default_direction=0):
        super().__init__(width, length)
        sprite_sheet = pyglet.image.load(sprite_sheet_filepath)
        self._images = []

        for cood in coordinates:
            img = sprite_sheet.get_region(cood[0], cood[1], width, length)
            img.anchor_x = width//2 * scale
            img.anchor_y = length//2 * scale
            self._images.append(img)
        antn_list = [AnimationFrame(img, self.DEFAULT_ANIMATION_DURATION) for img in self._images]
        self._animation = Animation(antn_list)
        self._sprite = pyglet.sprite.Sprite(self._animation)
        self.default_angle = default_direction
        self.rotation_setting = rotation_setting
        self.dx = 0
        self.dy = 0
        if scale > 1:
            self.resize(width*scale, length*scale)
        else:
            self.resize(width, length)

    def draw(self):
        self._sprite.draw()

    def resize(self, width, length):
        for img in self._images:
            img.get_texture().width = width
            img.get_texture().height = length
        antn_list = [AnimationFrame(img, self.DEFAULT_ANIMATION_DURATION) for img in self._images]
        self._animation = Animation(antn_list)
        self._width = width
        self._length = length

    def move(self, x, y):
        self.dx = x - self.x
        self.dy = y - self.y
        self.rotate()
        self._change_coordinates(x, y)

    def move_offset(self, x, y):
        self.dx += x
        self.dy += y
        self.rotate()
        super().move_offset(x, y)

    def _change_coordinates(self, x, y):
        self.x = x
        self.y = y
        self._sprite.set_position(x, y)

    def rotate(self):
        self.test_int = self.test_int % 360 + 10
        if self.rotation_setting == DrawableRotationSetting.ANGULAR:
            try:
                if self.dx < 0:
                    rotation_angle = -math.atan(self.dy/self.dx) * 60 + 180
                else:
                    rotation_angle = -math.atan(self.dy/self.dx) * 60
            except ZeroDivisionError:
                if self.dy < 0:
                    rotation_angle = 90
                else:
                    rotation_angle = 270
            self._sprite.rotation = rotation_angle


class ImageDrawable(Drawable):
    def __init__(self, image_location: str, width, length):
        super().__init__(width, length)
        self._image = pyglet.image.load(image_location)
        self._image.anchor_x = width//2
        self._image.anchor_y = length//2
        self._sprite = pyglet.sprite.Sprite(self._image)
        self.resize(width, length)

    def draw(self):
        self._sprite.draw()

    def resize(self, width, length):
        self._image.get_texture().width = width
        self._image.get_texture().height = length
        self._image.height = length
        self._image.width = width
        self._width = width
        self._length = length
        self._sprite = pyglet.sprite.Sprite(self._image)

    def move(self, x, y):
        super().move(x, y)
        self._sprite.set_position(x, y)

    def move_offset(self, x, y):
        super().move_offset(x, y)
        self._sprite.set_position(self.x + x, self.y + y)
