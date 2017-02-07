from samples.simpy.components import HealthComponent, HungerComponent, WanderComponent
from laropy.game_objects import GameObject, Layer
from laropy.drawables import ImageDrawable, AnimatedDrawable, DrawableRotationSetting
from os import path

ASSET_FOLDER = 'assets'


class Grass(GameObject):
    def __init__(self, x, y):
        drawable = ImageDrawable(path.join(ASSET_FOLDER,'bush.png'), 16, 16)
        super().__init__('grassy', drawable, 16, 16)
        self._attributes = ['plant']
        self.data_lib.set_value('was_eaten', False, 'collision')
        h = HealthComponent(100)
        h.add_health_change_condition('was_eaten', True, -100)
        self.data_lib.set_value(HungerComponent.FOOD_VALUE_KEY, 5, 'Grass.init')
        self._add_component(h)
        self.move(x, y)
        self.layer = Layer.GROUND_FLOOR

    def on_collision(self, obj: GameObject):
        if obj.has_attribute('herbivore'):
            if obj.data_lib.get_value(HungerComponent.IS_HUNGRY_KEY):
                self.data_lib.set_value('was_eaten', True, 'collision')


class HungryBuddy(GameObject):
    def __init__(self):
        drawable = AnimatedDrawable(path.join(ASSET_FOLDER,'sprites.png'), [(210, 180), (210, 210)], 16, 16, scale=2,
                                    rotation_setting=DrawableRotationSetting.ANGULAR)
        super().__init__('octy', drawable, 16, 16)
        self._attributes = ['herbivore']

        hc = HungerComponent(100, 50, 4)
        hc.set_not_hungry_behavior(self, WanderComponent(2))
        self._add_component(hc)
        self.move(250, 250)
        self.layer = Layer.GROUND

    def on_collision(self, obj):
        if obj.has_attribute('plant'):
            if self.data_lib.get_value(HungerComponent.IS_HUNGRY_KEY):
                food_val = obj.data_lib.get_value(HungerComponent.FOOD_VALUE_KEY)
                self.data_lib.set_value(HungerComponent.STOMACH_VALUE_KEY, food_val, 'hgrybdy-collision')


class BadHungryBuddy(GameObject):
    def __init__(self):
        drawable = AnimatedDrawable(path.join(ASSET_FOLDER,'sprites.png'), [(210, 180), (210, 210)], 16, 16, scale=2,
                                    rotation_setting=DrawableRotationSetting.ANGULAR)
        super().__init__('octy', drawable, 16, 16)
        self._attributes = ['herbivore']

        hc = HungerComponent(100, 75, 4, full_hunger=50)
        hc.set_not_hungry_behavior(self, WanderComponent(2))
        self._add_component(hc)
        self.move(250, 250)
        self.layer = Layer.GROUND

    def on_collision(self, obj):
        if obj.has_attribute('plant'):
            if self.data_lib.get_value(HungerComponent.IS_HUNGRY_KEY):
                food_val = obj.data_lib.get_value(HungerComponent.FOOD_VALUE_KEY)
                self.data_lib.set_value(HungerComponent.STOMACH_VALUE_KEY, food_val, 'hgrybdy-collision')

