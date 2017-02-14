from random import Random
from laropy.pathing import get_distance
from laropy.game_objects import Layer


class CantFindObjectError(Exception):
    pass


class MouseInputType:
    HOVER = 'HOVER'
    CLICK = 'CLICK'


class Environment:
    class SpawnData:
        def __init__(self, game_object_class, interval):
            self.game_object = game_object_class
            self.interval = interval
            self.dt_of_last_spawn = 0

    _game_objects = []
    _mouse_data = {}
    _spawn_list = []

    def __init__(self, window, max_objects=40):
        self.width = window.width
        self.length = window.height
        self.dt_total = 0
        self.max_objects = max_objects
        self.cps = 0

    def add_object(self, obj):
        if len(self._game_objects) < self.max_objects:
            obj.set_env(self)
            self._game_objects.append(obj)

    def update_mouse_data(self, x, y, input_type: MouseInputType):
        self._mouse_data[input_type] = (x, y)

    def find_closest_obj_coordinates(self, obj, attribute=None):
        closest_obj = None
        closest_dist = self.width + self.length
        for t_obj in self._game_objects:
            if not attribute or t_obj.has_attribute(attribute):
                dist = get_distance(obj.x, obj.y, t_obj.x, t_obj.y)
                if closest_dist > dist:
                    closest_obj = t_obj
                    closest_dist = dist

        if not closest_obj:
            raise CantFindObjectError('There is no objects near {} matching the requirements.'.format(obj))
        return closest_obj

    def get_mouse_data(self, input_type: MouseInputType):
        return self._mouse_data.get(input_type, (0, 0))

    def _check_collisions(self):
        for obj1 in self._game_objects:
            for obj2 in self._game_objects:
                if obj1.has_collision(obj2):
                    obj1.on_collision(obj2)
                if obj2.has_collision(obj1):
                    obj2.on_collision(obj1)

    @staticmethod
    def has_collision(x1, y1, x2, y2):
        return abs(x1 - x2) < 5 and abs(y1 - y2) < 5

    def add_spawn(self, obj_class, interval):
        self._spawn_list.append(self.SpawnData(obj_class, interval))

    def update_objects(self, dt):
        for obj in self._game_objects:
            obj.update(dt)
        self._game_objects = [g_o for g_o in self._game_objects if not g_o.flagged_for_removal]

        for spawn in self._spawn_list:
            if len(self._game_objects) < self.max_objects and spawn.dt_of_last_spawn + dt > spawn.interval:
                rdm = Random()
                x = rdm.randint(0, self.width)
                y = rdm.randint(0, self.length)
                spawn.dt_of_last_spawn -= spawn.interval
                self.add_object(spawn.game_object(x, y))
            else:
                spawn.dt_of_last_spawn += dt
        self.dt_total += dt
        self.cps += 1
        if self.dt_total > 1:
            self.dt_total -= 1
            self.cps = 1

        self._check_collisions()

    def draw_objects(self):
        g = []
        gl = []

        for obj in self._game_objects:
            if obj.layer == Layer.GROUND_FLOOR:
                g.append(obj)
            elif obj.layer == Layer.GROUND:
                gl.append(obj)

        self._draw_obj_list(g)
        self._draw_obj_list(gl)

    @staticmethod
    def _draw_obj_list(obj_list):
        for obj in obj_list:
            obj.draw()
