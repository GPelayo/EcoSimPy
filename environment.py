from utils import PathingUtil


class CantFindObjectError(Exception):
    pass


class MouseInputType:
    HOVER = 'HOVER'
    CLICK = 'CLICK'


class Environment:
    _game_objects = []
    _mouse_data = {}

    def __init__(self, window):
        self.width = window.width
        self.length = window.height

    def add_object(self, obj):
        obj.set_env(self)
        self._game_objects.append(obj)

    def update_mouse_data(self, x, y, input_type: MouseInputType):
        self._mouse_data[input_type] = (x, y)

    def find_closest_obj_coordinates(self, obj, attribute=None):
        closest_obj = None
        closest_dist = self.width + self.length
        for t_obj in self._game_objects:
            if not attribute or t_obj.has_attribute(attribute):
                dist = PathingUtil.get_distance(obj.x, obj.y, t_obj.x, t_obj.y)
                if closest_dist > dist:
                    closest_obj = t_obj
                    closest_dist = dist

        if not closest_obj:
            raise CantFindObjectError('There is no objects near {} matching the requirements.'.format(obj))
        return closest_obj.x, closest_obj.y

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

    def update_objects(self, dt):
        for obj in self._game_objects:
            obj.update(dt)

        self._game_objects = [g_o for g_o in self._game_objects if not g_o.flagged_for_removal]
        self._check_collisions()

    def draw_objects(self):
        for obj in self._game_objects:
            obj.draw()
