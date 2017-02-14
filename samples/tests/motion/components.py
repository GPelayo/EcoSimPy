import random
from laropy.game_objects import GameObject
from laropy.component import GameComponent


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


class WanderComponent(GameComponent):
    name = 'Wander'

    def __init__(self, speed):
        super().__init__()
        self.speed = speed
        self.destination_x = 0
        self.destination_y = 0
        self.random = random.Random()
        self.cur_step = 0
        self.path = []
        self.max_distance = 100
        self.max_x = 0
        self.max_y = 0

    def set_env(self, env):
        self._env = env
        self.max_x = self.env.width
        self.max_y = self.env.length

    def reset(self):
        self.path = create_empty_generator()

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
