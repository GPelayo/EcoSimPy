from laropy.components.ai import WanderComponent
from laropy.components.input import MouseMoveComponent
from laropy.environment import MouseInputType
from laropy.game_objects import GameObject
from laropy.drawables import AnimatedDrawable, DrawableRotationSetting
from os import path

ASSET_FOLDER = 'assets'


class ClickBuddy(GameObject):
    def __init__(self):
        super().__init__(self, AnimatedDrawable(path.join(ASSET_FOLDER, 'sprites.png'), [(90, 180), (90, 210)], 16, 16, scale=2,
                                                rotation_setting=DrawableRotationSetting.ANGULAR), 16, 16)
        self._add_component(MouseMoveComponent(4, MouseInputType.CLICK))
        self.move(250, 250)


class HoverBuddy(GameObject):
    def __init__(self):
        super().__init__(self, AnimatedDrawable(path.join(ASSET_FOLDER, 'sprites.png'), [(210, 180), (210, 210)], 16, 16, scale=2,
                                                rotation_setting=DrawableRotationSetting.ANGULAR), 16, 16)
        self._add_component(MouseMoveComponent(2, MouseInputType.HOVER))
        self.move(250, 250)


class WanderBuddy(GameObject):
    def __init__(self):
        drawable = AnimatedDrawable(path.join(ASSET_FOLDER, 'sprites.png'), [(380, 30), (380, 0)], 16, 16, scale=2,
                                    rotation_setting=DrawableRotationSetting.STATIC)
        super().__init__(self, drawable, 16, 16)
        self._add_component(WanderComponent(1))
        self.move(250, 250)