from random import Random
from ..game_objects import GameObject
from ..pathing import StraightPathing
from .common import GameComponent, Trigger


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


class WanderComponent(GameComponent):
    name = 'Wander'

    def __init__(self, speed):
        super().__init__()
        self.speed = speed
        self.destination_x = self.destination_y = None
        self.random = Random()
        self.cur_step = 0
        self.pathing = StraightPathing()
        self.path = []
        self.max_distance = 100
        self.max_x = self.max_y = 0

    def set_env(self, env):
        self._env = env
        self.max_x = self.env.width
        self.max_y = self.env.length

    def reset(self):
        self.path = []

    def get_path(self, obj: GameObject, farthest_left, farthest_right, farthest_south, farthest_north):
        while True:
            self.destination_x = obj.x + self.random.randint(farthest_left, farthest_right)
            self.destination_y = obj.y + self.random.randint(farthest_south, farthest_north)
            dy = self.destination_y - obj.y
            dx = self.destination_x - obj.x
            if dy != 0 and dx != 0 and 0 <= self.destination_x <= self.max_x and 0 <= self.destination_y < self.max_y:
                break
        self.path = self.pathing.create_path(obj.x, obj.y, self.destination_x, self.destination_y, self.speed)

    def update(self, obj: GameObject, tick):
        next_step = next(self.path, None) if self.path else None
        if next_step:
            obj.move(next_step[0], next_step[1])
        else:
            self.get_path(obj, -self.max_distance, self.max_distance, -self.max_distance, self.max_distance)
