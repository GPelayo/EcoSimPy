import pyglet
from enviroment import Environment
from drawables import AnimatedDrawable, DrawableRotationSetting
from game_objects import GameObject
from component import WanderComponent


class TestObj(GameObject):
    def __init__(self):
        global env
        super().__init__(self, AnimatedDrawable('sprites.png', [(90, 210), (90, 180)], 16, 16, scale=2,
                                                rotation_setting=DrawableRotationSetting.ANGULAR))
        self._component_list.append(WanderComponent(2, env))
        self.move(250, 250)

w = pyglet.window.Window()
env = Environment(w)
env.add_object(TestObj())


@w.event
def on_draw():
    global env
    w.clear()
    env.draw_objects()


def update_environment(dt):
    env.update_objects(dt)

pyglet.clock.schedule_interval(update_environment, 1/100.0)
pyglet.app.run()
