from laropy.game_objects import GameObject


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


class Trigger:
    def check_condition(self, obj):
        raise NotImplementedError


class LibraryValueTrigger(Trigger):
    def __init__(self, library_field, value_to_trigger):
        self.field = library_field
        self.value = value_to_trigger

    def check_condition(self, obj: GameObject):
        return obj.data_lib.get_value(self.field) == self.value