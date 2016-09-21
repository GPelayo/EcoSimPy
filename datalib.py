class DataLib:
    def __init__(self):
        self.__lib = {}

    def has_field(self, field):
        return field in self.__lib

    def get_value(self, field):
        return self.__lib[field][0]

    def set_value(self, field, value, component_name):
        self.__lib[field] = (value, component_name)

    def get_last_component_of_value(self, field):
        return self.__lib[field][1]


class LibKey:
    PATHING_STATE = 0
    HUNGER_STATE = 1
