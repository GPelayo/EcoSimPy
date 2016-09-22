class DataLib:
    class DataValue:
        def __init__(self, value, comment):
            self.value = value
            self.comment = comment

    def __init__(self):
        self.__lib = {}

    def has_field(self, field):
        return field in self.__lib

    def get_value(self, field, default=None):
        try:
            return self.__lib[field].value
        except KeyError:
            return default

    def add_value(self, field, value):
        self.__lib[field].value += value
        return self.__lib[field].value

    def set_value(self, field, value, comment):
        self.__lib[field] = self.DataValue(value, comment)

    def get_value_comment(self, field):
        return self.__lib[field].comment

    def pop_value(self, field):
        return self.__lib.pop(field).value


class LibKey:
    PATHING_STATE = 0
    HUNGER_STATE = 1
