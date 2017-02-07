import pyglet
from random import Random
from laropy.environment import Environment, MouseInputType
from samples.simpy.game_objects import HungryBuddy, BadHungryBuddy, Grass

w = pyglet.window.Window()
env = Environment(w)
env.add_object(HungryBuddy())
env.add_object(BadHungryBuddy())
env.add_spawn(Grass, 0.3)


@w.event
def on_mouse_press(x, y, button=None, modifiers=None):
    r = Random()

    for i in range(4):
        rx = r.randint(-30, 30)
        ry = r.randint(-30, 30)
        env.add_object(Grass(x + rx, y + ry))

    env.update_mouse_data(x, y, MouseInputType.CLICK)


@w.event
def on_mouse_motion(x, y, dx, dy):
    env.update_mouse_data(x, y, MouseInputType.HOVER)


@w.event
def on_draw():
    global env
    w.clear()
    env.draw_objects()


def update_environment(dt):
    env.update_objects(dt)

pyglet.clock.schedule_interval(update_environment, 1/100)
pyglet.app.run()
