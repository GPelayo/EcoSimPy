import pyglet
from pyglet.image import Animation, AnimationFrame
from environment import Environment, MouseInputType, CantFindObjectError
from drawables import AnimatedDrawable, DrawableRotationSetting, ImageDrawable
from game_objects import GameObject, Layer
from component import WanderComponent, BehaviorComponent, LibraryValueTrigger, PathingStates, \
    GameComponent, init_empty_gen
from datalib import LibKey
from utils import PathingUtil
from random import Random


class InvalidHungerSettingException(Exception):
    pass


class HealthComponent(GameComponent):
    def __init__(self, max_hp):
        super().__init__()
        self.hp = max_hp
        self.damage_condition = []

    def add_health_change_condition(self, datalib_field, value, damage):
        self.damage_condition.append((datalib_field, value, damage))

    def update(self, obj, tick):
        for dc in self.damage_condition:
            if obj.data_lib.has_field(dc[0]) and obj.data_lib.get_value(dc[0]) == dc[1]:
                self.hp += dc[2]
        if self.hp < 0:
            obj.flagged_for_removal = True


class AnimationChangeComponent(GameComponent):
    class AnimationCondition:
        def __init__(self, field, value, drawable):
            self.field = field
            self.value = value
            self.drawable = drawable

    drawable_list = []

    def add_drawable(self, data_lib_field, value, drawable):
        new_ani = self.AnimationCondition(data_lib_field, value, drawable)
        self.drawable_list.append(new_ani)

    def update(self, obj: GameObject, tick):
        for ani in self.drawable_list:
            if ani.value == obj.data_lib.get_value(ani.field):
                obj.change_drawable(ani)


class Grass(GameObject):
    def __init__(self, x, y):
        drawable = ImageDrawable('bush.png', 16, 16)
        super().__init__('grassy', drawable, 16, 16)
        self._attributes = ['plant']
        self.data_lib.set_value('was_eaten', False, 'collision')
        h = HealthComponent(100)
        h.add_health_change_condition('was_eaten', True, -100)
        self.data_lib.set_value(HungerComponent.FOOD_VALUE_KEY, 5, 'Grass.init')
        self._add_component(h)
        self.move(x, y)
        self.layer = Layer.GROUND_FLOOR

    def on_collision(self, obj: GameObject):
        if obj.has_attribute('herbivore'):
            if obj.data_lib.get_value(HungerComponent.IS_HUNGRY_KEY):
                self.data_lib.set_value('was_eaten', True, 'collision')


class HungerComponent(GameComponent):
    FOOD_VALUE_KEY = 'food_value'
    IS_HUNGRY_KEY = 'is_hungry'
    STOMACH_VALUE_KEY = 'stomach'
    name = 'hunger'
    run_speed = 5

    def __init__(self, max_hunger, hunt_hunger, hunger_speed, full_hunger=None):
        if full_hunger:
            self.full_hunger = full_hunger
        else:
            self.full_hunger = 0

        if hunt_hunger > max_hunger:
            raise InvalidHungerSettingException('Hunting hunger value is larger than Max hunger value.')
        if self.full_hunger > hunt_hunger:
            raise InvalidHungerSettingException('Full Hunger value is larger than Hunting hunger value.')

        super().__init__()
        self.hunger_val = 100
        self.hunger_speed = hunger_speed
        self.max_hunger = max_hunger
        self.hunt_hunger = hunt_hunger
        self.not_hunger_behavior = None
        self.path = None
        self.destination_x = 0
        self.destination_y = 0
        self.cur_step = 0
        self.path = init_empty_gen()
        self.max_distance = 100
        self.max_x = 0
        self.max_y = 0
        self.pathing_state = PathingStates.IDLE

    def set_env(self, environment):
        self._env = environment
        self.not_hunger_behavior.set_env(environment)

    def set_not_hungry_behavior(self, obj, component: GameComponent):
        self.not_hunger_behavior = component

    def update(self, obj: GameObject, tick):
        self.dt_remainder += tick
        if obj.data_lib.has_field(self.STOMACH_VALUE_KEY):
            self.hunger_val -= obj.data_lib.pop_value(self.STOMACH_VALUE_KEY)

        if self.hunt_hunger <= self.hunger_val:
            obj.data_lib.set_value(self.IS_HUNGRY_KEY, True, self.name)

        if self.full_hunger >= self.hunger_val:
            obj.data_lib.set_value(self.IS_HUNGRY_KEY, False, self.name)

        if obj.data_lib.get_value(self.IS_HUNGRY_KEY):
            try:
                closest_obj = obj.env.find_closest_obj_coordinates(obj, 'plant')
                if obj.has_collision(closest_obj) and \
                        self.pathing_state != PathingStates.MOVING:
                    self.pathing_state = PathingStates.IDLE
                elif self.pathing_state == PathingStates.IDLE or self.pathing_state == PathingStates.MOVING:
                    self.not_hunger_behavior.reset()
                    self.pathing_state = PathingStates.CALCULATING
                    self.path = PathingUtil.create_path(obj.x, obj.y, closest_obj.x, closest_obj.y, self.run_speed)
                    self.destination_x = closest_obj.x
                    self.destination_y = closest_obj.y
                    self.pathing_state = PathingStates.MOVING
                if self.pathing_state == PathingStates.MOVING:
                    closest_obj = obj.env.find_closest_obj_coordinates(obj, 'plant')
                    if (closest_obj.x, closest_obj.y) == (self.destination_x, self.destination_y):
                        next_step = next(self.path, None)
                        if next_step:
                            obj.move(next_step[0], next_step[1])
                    else:
                        self.pathing_state = PathingStates.IDLE
                        obj.data_lib.set_value(self.IS_HUNGRY_KEY, False, self.name)
                obj.data_lib.set_value(LibKey.PATHING_STATE, PathingStates.MOVING, self.name)
            except CantFindObjectError:
                if self.not_hunger_behavior:
                    obj.data_lib.set_value(self.IS_HUNGRY_KEY, True, self.name)
                    self.not_hunger_behavior.update(obj, tick)
        else:
            if self.not_hunger_behavior:
                self.not_hunger_behavior.update(obj, tick)

        if self.dt_remainder > 1:
            if self.hunger_val + self.hunger_speed > self.max_hunger:
                self.hunger_val = self.max_hunger
            elif self.hunger_val + self.hunger_speed < 0:
                self.hunger_val = 0
            else:
                self.hunger_val += self.hunger_speed
            self.dt_remainder -= 1


class HungryBuddy(GameObject):
    def __init__(self):
        drawable = AnimatedDrawable('sprites.png', [(210, 180), (210, 210)], 16, 16, scale=2,
                                    rotation_setting=DrawableRotationSetting.ANGULAR)
        super().__init__('octy', drawable, 16, 16)
        self._attributes = ['herbivore']

        hc = HungerComponent(100, 50, 4)
        hc.set_not_hungry_behavior(self, WanderComponent(2))
        self._add_component(hc)
        self.move(250, 250)
        self.layer = Layer.GROUND

    def on_collision(self, obj):
        if obj.has_attribute('plant'):
            if self.data_lib.get_value(HungerComponent.IS_HUNGRY_KEY):
                food_val = obj.data_lib.get_value(HungerComponent.FOOD_VALUE_KEY)
                self.data_lib.set_value(HungerComponent.STOMACH_VALUE_KEY, food_val, 'hgrybdy-collision')


class BadHungryBuddy(GameObject):
    def __init__(self):
        drawable = AnimatedDrawable('sprites.png', [(210, 180), (210, 210)], 16, 16, scale=2,
                                    rotation_setting=DrawableRotationSetting.ANGULAR)
        super().__init__('octy', drawable, 16, 16)
        self._attributes = ['herbivore']

        hc = HungerComponent(100, 5000, 4, full_hunger=1000)
        hc.set_not_hungry_behavior(self, WanderComponent(2))
        self._add_component(hc)
        self.move(250, 250)
        self.layer = Layer.GROUND

    def on_collision(self, obj):
        if obj.has_attribute('plant'):
            if self.data_lib.get_value(HungerComponent.IS_HUNGRY_KEY):
                food_val = obj.data_lib.get_value(HungerComponent.FOOD_VALUE_KEY)
                self.data_lib.set_value(HungerComponent.STOMACH_VALUE_KEY, food_val, 'hgrybdy-collision')


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
