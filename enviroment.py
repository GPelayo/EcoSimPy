class Environment:
    game_objects = []

    def __init__(self, window):
        self.width = window.width
        self.length = window.height

    def add_object(self, obj):
        self.game_objects.append(obj)

    def update_objects(self, dt):
        for obj in self.game_objects:
            obj.update(dt)

    def draw_objects(self):
        for obj in self.game_objects:
            obj.draw()
