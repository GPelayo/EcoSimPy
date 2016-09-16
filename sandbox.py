"""
DON"T COMMIT MEEEEEE
"""

import pyglet
import random
from time import sleep


class GameObject:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.movement_type = Wander()
        self.test_image = pyglet.image.load('images.png')
        self.set_size(100, 100)
        self.test_image.x = 250
        self.test_image.y = 250
        self.sprite = pyglet.sprite.Sprite(self.test_image)

    def update_display_state(self):
        pass

    def set_size(self, width, height):
        self.test_image.get_texture().width = width
        self.test_image.get_texture().height = height
        self.test_image.height = height
        self.test_image.width = width


class Wander:
    def __init__(self):
        self.destination_x = 0
        self.destination_y = 0
        self.random = random.Random()

    def set_destination(self, obj: GameObject):
        self.destination_x = self.random.randint(10, 10)
        self.destination_y = self.random.randint(10, 10)
        obj.x = (self.destination_x - obj.x)

    def move(self, obj: GameObject):
        pass


class Enviroment:
    game_objects = []

    def __init__(self):
        pass

    def add_object(self, obj):
        self.game_objects.append(obj)

    def animate(self):
        for obj in self.game_objects:
            obj.update_display_state()

    def draw_objects(self):
        for obj in self.game_objects:
            obj.sprite.draw()


env = Enviroment()
env.add_object(GameObject())
window = pyglet.window.Window()


@window.event
def on_draw():
    global env
    env.game_objects[0].sprite.draw()


def update_environment(dt):
    window.clear()
    env.animate()

pyglet.clock.schedule_interval(update_environment, 1/1000.0)
pyglet.app.run()

