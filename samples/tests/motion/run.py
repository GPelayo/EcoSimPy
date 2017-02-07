import pyglet

from laropy.environment import Environment, MouseInputType
from samples.tests.motion.game_objects import WanderBuddy, ClickBuddy, HoverBuddy

w = pyglet.window.Window()
env = Environment(w)
env.add_object(WanderBuddy())
env.add_object(ClickBuddy())
env.add_object(HoverBuddy())


@w.event
def on_mouse_press(x, y, button=None, modifiers=None):
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

pyglet.clock.schedule_interval(update_environment, 1/100.0)
pyglet.app.run()
