import random
from laropy.component import GameComponent
from laropy.datalib import LibKey
from laropy.environment import CantFindObjectError
from laropy.game_objects import GameObject
from laropy.pathing import StraightPathing, PathingStates
from samples.simpy.exceptions import InvalidHungerSettingException


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
        self.random = random.Random()
        self.cur_step = 0
        self.pathing = StraightPathing()
        self.path = []
        self.max_distance = 100
        self.max_x = 0
        self.max_y = 0

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
        self.path = []
        self.pathing = StraightPathing()
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
                    self.path = self.pathing.create_path(obj.x, obj.y, closest_obj.x, closest_obj.y, self.run_speed)
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