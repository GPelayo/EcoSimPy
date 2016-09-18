import pyglet
from pyglet.image import Animation, AnimationFrame
import random
import math


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

    def update(self, tick):
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


class GameComponent:
    name = None

    def __init__(self, environment):
        self.env = environment

    def update(self, obj: GameObject, tick):
        raise NotImplementedError


def init_empty_gen():
    yield


class ZeroDistanceError(Exception):
    message = "Distance is zero."


def create_path(org_x, org_y, dest_x, dest_y, speed):
    distance = math.sqrt(math.pow(dest_x - org_x, 2) + math.pow(dest_y - org_y, 2))
    time_to_dest = distance/speed

    if time_to_dest <= 0:
        raise ZeroDistanceError

    step_size_y = (dest_y - org_y) / time_to_dest
    step_size_x = (dest_x - org_x) / time_to_dest

    test_path = [(step_size_x * step + org_x, step_size_y * step + org_y)
                 for step in range(1, math.floor(time_to_dest) + 1)]

    return (path for path in test_path)


class WanderComponent(GameComponent):
    name = 'Wander'

    def __init__(self, speed, environment):
        super().__init__(environment)
        self.speed = speed
        self.destination_x = 0
        self.destination_y = 0
        self.random = random.Random()
        self.cur_step = 0
        self.path = init_empty_gen()
        self.max_distance = 100
        self.max_x = environment.width
        self.max_y = environment.length

    def get_path(self, obj: GameObject, farthest_left, farthest_right, farthest_south, farthest_north):
        while True:
            self.destination_x = obj.x + self.random.randint(farthest_left, farthest_right)
            self.destination_y = obj.y + self.random.randint(farthest_south, farthest_north)
            dy = self.destination_y - obj.y
            dx = self.destination_x - obj.x
            if dy != 0 and dx != 0 and 0 <= self.destination_x <= self.max_x and 0 <= self.destination_y < self.max_y:
                break

        self.path = create_path(obj.x, obj.y, self.destination_x, self.destination_y, self.speed)

    def update(self, obj: GameObject, tick):
        next_step = next(self.path, None)
        if next_step:
            obj.move(next_step[0], next_step[1])
        else:
            self.get_path(obj, -self.max_distance, self.max_distance, -self.max_distance, self.max_distance)


class UserMoveComponent(GameComponent):
    name = 'Wander'

    def __init__(self, speed, environment):
        super().__init__(environment)
        self.speed = speed
        self.destination_x = 0
        self.destination_y = 0
        self.random = random.Random()
        self.cur_step = 0
        self.path = init_empty_gen()
        self.max_distance = 100
        self.max_x = environment.width
        self.max_y = environment.length

    def get_path(self, obj: GameObject, farthest_left, farthest_right, farthest_south, farthest_north):
        while True:
            self.destination_x = obj.x + self.random.randint(farthest_left, farthest_right)
            self.destination_y = obj.y + self.random.randint(farthest_south, farthest_north)
            if self.destination_y - obj.y != 0 and self.destination_x - obj.x != 0 \
                    and 0 <= self.destination_x <= self.max_x and 0 <= self.destination_y < self.max_y:
                    break

        self.path = create_path(obj.x, obj.y, self.destination_x, self.destination_y, self.speed)

    def update(self, obj: GameObject, tick):
        next_step = next(self.path, None)
        if next_step:
            obj.move(next_step[0], next_step[1])
        else:
            self.get_path(obj, -self.max_distance, self.max_distance, -self.max_distance, self.max_distance)


class Environment:
    game_objects = []

    def __init__(self, window):
        self.width = window.width
        self.length = window.height

    def add_object(self, obj):
        self.game_objects.append(obj)

    def update_objects(self, dt):
        for obj in self.game_objects:
            obj.update(dt)

    def draw_objects(self):
        for obj in self.game_objects:
            obj.draw()


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
        self._sprite = pyglet.sprite.Sprite(self._images[0])
        self.default_angle = default_direction
        self.rotation_setting = rotation_setting
        self.dx = 0
        self.dy = 0
        if scale > 1:
            self.resize(width*2, length*2)
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


class DataLibrary:
    def __init__(self):
        self.data_list = {}

    def add_data(self, component, field_name, data):
        self.data_list[field_name] = (data, id(component))

    def get_entry(self, field_name):
        return self.data_list[field_name][0]


class Tangle(GameObject):
    def __init__(self):
        global env
        super().__init__(self, AnimatedDrawable('sprites.png', [(90, 210), (90, 180)], 16, 16, scale=2,
                                                rotation_setting=DrawableRotationSetting.ANGULAR))
        self._component_list.append(WanderComponent(2, env))
        self.move(250, 250)

w = pyglet.window.Window()
env = Environment(w)
env.add_object(Tangle())


@w.event
def on_draw():
    global env
    w.clear()
    env.draw_objects()


def update_environment(dt):
    env.update_objects(dt)

pyglet.clock.schedule_interval(update_environment, 1/100.0)
pyglet.app.run()
