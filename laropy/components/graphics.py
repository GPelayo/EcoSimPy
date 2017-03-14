from .common import GameComponent
from laropy.game_objects import GameObject


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
