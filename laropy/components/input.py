from pyglet.window import key
from laropy.datalib import LibKey
from laropy.pathing import StraightPathing, PathingStates
from laropy.environment import MouseInputType
from laropy.game_objects import GameObject
from .common import GameComponent


class InputComponent(GameComponent):
    def __init__(self):
        super().__init__()
        self.mouse_input = None
        self.keyboard_handler = None

    def set_env(self, env):
        super().set_env(env)
        #TODO impl loose mouse_input
        # self.mouse_input = None
        self.keyboard_handler = self.env.keyboard_handler

    def update(self, obj, tick):
        raise NotImplementedError


class MouseMoveComponent(InputComponent):
    name = 'MouseMove'

    def __init__(self, speed, mouse_input: MouseInputType):
        super().__init__()
        self.speed = speed
        self.destination_x = 0
        self.destination_y = 0
        self.cur_step = 0
        self.path = []
        self.pathing = StraightPathing()
        self.pathing_state = PathingStates.IDLE
        self.mouse_input = mouse_input

    def update(self, obj: GameObject, tick):
        mouse_cood = self.env.get_mouse_data(self.mouse_input)
        if mouse_cood == (self.destination_x, self.destination_y) and \
                self.pathing_state != PathingStates.MOVING:
            self.pathing_state = PathingStates.IDLE
        elif self.pathing_state == PathingStates.IDLE or self.pathing_state == PathingStates.MOVING:
            self.pathing_state = PathingStates.CALCULATING
            self.path = self.pathing.create_path(obj.x, obj.y, mouse_cood[0], mouse_cood[1], self.speed)
            self.destination_x = mouse_cood[0]
            self.destination_y = mouse_cood[1]
            self.pathing_state = PathingStates.MOVING

        if self.pathing_state == PathingStates.MOVING:
            next_step = next(self.path, None)
            if next_step:
                obj.move(next_step[0], next_step[1])

        obj.data_lib.set_value(LibKey.PATHING_STATE, PathingStates.MOVING, self.name)


class KeyboardMoveComponent(InputComponent):
    name = 'MouseMove'

    def __init__(self, speed):
        super().__init__()
        self.speed = speed
        self.path = []
        self.pathing_state = PathingStates.IDLE

    def update(self, obj: GameObject, tick):
        pressed_keys = self.keyboard_handler.pressed_keys
        dx = dy = 0

        if key.UP in pressed_keys:
            dy = self.speed
        elif key.DOWN in pressed_keys:
            dy = -self.speed

        if key.LEFT in pressed_keys:
            dx = -self.speed
        elif key.RIGHT in pressed_keys:
            dx = self.speed
        obj.move_offset(dx, dy)
