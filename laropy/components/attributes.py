from .common import GameComponent


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
