import pyglet
from environment import Environment, MouseInputType
from drawables import AnimatedDrawable, DrawableRotationSetting
from game_objects import GameObject
from component import WanderComponent, MouseMoveComponent


class ClickBuddy(GameObject):
    def __init__(self):
        super().__init__(self, AnimatedDrawable('sprites.png', [(90, 180), (90, 210)], 16, 16, scale=2,
                                                rotation_setting=DrawableRotationSetting.ANGULAR))
        self._add_component(MouseMoveComponent(4, MouseInputType.CLICK))
        self.move(250, 250)


class HoverBuddy(GameObject):
    def __init__(self):
        super().__init__(self, AnimatedDrawable('sprites.png', [(210, 180), (210, 210)], 16, 16, scale=2,
                                                rotation_setting=DrawableRotationSetting.ANGULAR))
        self._add_component(MouseMoveComponent(2, MouseInputType.HOVER))
        self.move(250, 250)


class WanderBuddy(GameObject):
    def __init__(self):
        drawable = AnimatedDrawable('sprites.png', [(380, 30), (380, 0)], 16, 16, scale=2,
                                    rotation_setting=DrawableRotationSetting.STATIC)
        super().__init__(self, drawable)
        self._add_component(WanderComponent(1))
        self.move(250, 250)

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
