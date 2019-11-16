import heapq

class State():
    def __init__(self, grid, teams, customers, ticks):
        self.grid = grid
        self.teams = teams
        self.customers = customers
        self.ticks = ticks

class Team():
    def __init__(self, id, name, cars, score):
        self.id = id
        self.name = name
        self.cars = cars
        self.score = score


class Car():
    def __init__(self, id, position, capacity, available_capacity, customers):
        self.id = id
        self.position = position
        self.capacity = capacity
        self.available_capacity = available_capacity
        self.customers = customers


class Customer():
    def __init__(self, id, position, destination):
        self.id = id
        self.position = position
        self.destination = destination


class Action():
    def __init__(self, car_id, direction=None):
        self.car_id = car_id
        self.direction = direction


class PriorityQueue():
    def __init__(self):
        self.elems = []

    def is_empty(self):
        return len(self.elems) == 0

    def push(self, elem, priority):
        heapq.heappush(self.elems, (priority, elem))

    def pop(self):
        return heapq.heappop(self.elems)[1]
