import math


class ZeroDistanceError(Exception):
    pass


class PathingStates:
    IDLE = 0
    CALCULATING = 1
    MOVING = 2


def get_distance(org_x, org_y, dest_x, dest_y):
    return math.sqrt(math.pow(dest_x - org_x, 2) + math.pow(dest_y - org_y, 2))


class Pathing:
    destination_x = 0
    destination_y = 0

    @staticmethod
    def create_path(org_x, org_y, dest_x, dest_y, speed):
        raise NotImplementedError


class StraightPathing:
    @staticmethod
    def create_path(org_x, org_y, dest_x, dest_y, speed):
        distance = get_distance(org_x, org_y, dest_x, dest_y)
        time_to_dest = distance/speed

        if time_to_dest <= 0:
            raise ZeroDistanceError

        step_size_y = (dest_y - org_y) / time_to_dest
        step_size_x = (dest_x - org_x) / time_to_dest

        test_path = [(step_size_x * step + org_x, step_size_y * step + org_y)
                     for step in range(1, math.floor(time_to_dest) + 1)]

        return (path for path in test_path)
