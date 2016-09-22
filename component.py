import random
from game_objects import GameObject
from environment import MouseInputType
from utils import PathingUtil
from datalib import LibKey, DataLib


def init_empty_gen():
    yield


class GameComponent:
    name = None

    def __init__(self):
        self._env = None
        self.dt_remainder = 0

    @property
    def env(self):
        return self._env

    def set_env(self, env):
        self._env = env

    def update(self, obj, tick):
        raise NotImplementedError

    def reset(self):
        pass


class WanderComponent(GameComponent):
    name = 'Wander'

    def __init__(self, speed):
        super().__init__()
        self.speed = speed
        self.destination_x = 0
        self.destination_y = 0
        self.random = random.Random()
        self.cur_step = 0
        self.path = init_empty_gen()
        self.max_distance = 100
        self.max_x = 0
        self.max_y = 0

    def set_env(self, env):
        self._env = env
        self.max_x = self.env.width
        self.max_y = self.env.length

    def reset(self):
        self.path = init_empty_gen()

    def get_path(self, obj: GameObject, farthest_left, farthest_right, farthest_south, farthest_north):
        while True:
            self.destination_x = obj.x + self.random.randint(farthest_left, farthest_right)
            self.destination_y = obj.y + self.random.randint(farthest_south, farthest_north)
            dy = self.destination_y - obj.y
            dx = self.destination_x - obj.x
            if dy != 0 and dx != 0 and 0 <= self.destination_x <= self.max_x and 0 <= self.destination_y < self.max_y:
                break

        self.path = PathingUtil.create_path(obj.x, obj.y, self.destination_x, self.destination_y, self.speed)

    def update(self, obj: GameObject, tick):
        next_step = next(self.path, None)
        if next_step:
            obj.move(next_step[0], next_step[1])
        else:
            self.get_path(obj, -self.max_distance, self.max_distance, -self.max_distance, self.max_distance)


class PathingStates:
    IDLE = 0
    CALCULATING = 1
    MOVING = 2


class MouseMoveComponent(GameComponent):
    name = 'MouseMove'

    def __init__(self, speed, mouse_input: MouseInputType):
        super().__init__()
        self.speed = speed
        self.destination_x = 0
        self.destination_y = 0
        self.cur_step = 0
        self.path = init_empty_gen()
        self.pathing_state = PathingStates.IDLE
        self.mouse_input = mouse_input

    def update(self, obj: GameObject, tick):
        mouse_cood = self.env.get_mouse_data(self.mouse_input)
        if mouse_cood == (self.destination_x, self.destination_y) and \
                self.pathing_state != PathingStates.MOVING:
            self.pathing_state = PathingStates.IDLE
        elif self.pathing_state == PathingStates.IDLE or self.pathing_state == PathingStates.MOVING:
            self.pathing_state = PathingStates.CALCULATING
            self.path = PathingUtil.create_path(obj.x, obj.y, mouse_cood[0], mouse_cood[1], self.speed)
            self.destination_x = mouse_cood[0]
            self.destination_y = mouse_cood[1]
            self.pathing_state = PathingStates.MOVING

        if self.pathing_state == PathingStates.MOVING:
            next_step = next(self.path, None)
            if next_step:
                obj.move(next_step[0], next_step[1])
        obj.data_lib.set_value(LibKey.PATHING_STATE, PathingStates.MOVING, self.name)


class Trigger:
    def check_condition(self, obj):
        raise NotImplementedError


class LibraryValueTrigger(Trigger):
    def __init__(self, library_field, value_to_trigger):
        self.field = library_field
        self.value = value_to_trigger

    def check_condition(self, obj: GameObject):
        return obj.data_lib.get_value(self.field) == self.value


class BehaviorComponent(GameComponent):
    class Behavior:
        component = None
        trigger = None

    behavior_table = []

    def add_behavior(self, component: GameComponent, trigger: Trigger):
        bvr = self.Behavior()
        bvr.component = component
        bvr.trigger = trigger
        self.behavior_table.append(bvr)

    def update(self, obj: GameObject, tick):
        for bvr in self.behavior_table:
            if bvr.trigger.check_condition(obj):
                bvr.update(obj, tick)
