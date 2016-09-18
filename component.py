import random
from game_objects import GameObject
from utils import PathingUtil


def init_empty_gen():
    yield


class GameComponent:
    name = None

    def __init__(self, environment):
        self.env = environment

    def update(self, obj, tick):
        raise NotImplementedError


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

        self.path = PathingUtil.create_path(obj.x, obj.y, self.destination_x, self.destination_y, self.speed)

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

        self.path = PathingUtil.create_path(obj.x, obj.y, self.destination_x, self.destination_y, self.speed)

    def update(self, obj: GameObject, tick):
        next_step = next(self.path, None)
        if next_step:
            obj.move(next_step[0], next_step[1])
        else:
            self.get_path(obj, -self.max_distance, self.max_distance, -self.max_distance, self.max_distance)