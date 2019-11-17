#
# THIS ALOGRITHM IS PROTECTED BY A PATENT FROM LEAGUE OF AGENTS. FORM RIOTED INC
#

from .classes import Action, PriorityQueue
from .utils import customers_waiting
from scipy.optimize import linear_sum_assignment
import time


class Vezos:
    agent_type = "VEZOS"

    def __init__(self, name, team_id):
        self.name = name
        self.id = team_id

    def get_name(self):
        return self.name

    def get_team_id(self):
        return self.id

    def act(self, obs):
        # Obtain variables
        self.grid = obs.grid
        self.teams = obs.teams
        self.obs = obs
        self.customers = customers_waiting(obs)

        team = [t for t in obs.teams if t.id == self.id][0]
        cars = team.cars
        customers = customers_waiting(obs)
        if len(customers) == 0:
            # print("No customer")
            actions = []
            for c in cars:
                actions.append(Action(c.id))
            return actions

        
        
        assign = self.findPairs(cars, customers, self.grid)
        
        threshold = len(self.grid) / (
            2 ** (0.6)
        )


        actions = []

        for (car_index, dest, dist) in assign:
            car = cars[car_index]
            if dist < threshold:
                actions += [self.Astar(car, dest, self.grid)]
            else:
                actions += [Action(car.id)]
        return actions

    def Astar(self, car, dest, grid):
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        # directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        start = car.position
        route = []

        pq = PriorityQueue()
        pq.push(start, 0)

        parent = {}
        cost = {}
        parent[start] = None
        cost[start] = 0

        while not pq.is_empty():
            curr = pq.pop()

            if curr == dest:
                break

            for i, dir in enumerate(directions):
                neighbor = add(curr, dir)
                if neighbor[0] < 0:
                    continue
                if neighbor[0] >= len(grid):
                    continue
                if neighbor[1] < 0:
                    continue
                if neighbor[1] >= len(grid[0]):
                    continue
                if grid[neighbor[1]][neighbor[0]] == False:
                    continue

                n_cost = cost[curr] + 1
                if neighbor not in cost.keys() or n_cost < cost[neighbor]:
                    cost[neighbor] = n_cost
                    priority = n_cost + heuristic(neighbor, dest)
                    pq.push(neighbor, priority)
                    parent[neighbor] = curr

        if dest not in parent.keys():
            action = Action(car.id)
            return action

        if dest == start:
            action = Action(car.id)
            return action

        prev = dest
        targ = None
        while not prev == start:
            route = [prev] + route
            targ = prev
            prev = parent[prev]
        if (targ[0] - prev[0]) == 0:
            if targ[1] - prev[1] == 1:
                action = Action(car.id, 2)
                return action
            else:
                action = Action(car.id, 0)
                return action
        else:
            if targ[0] - prev[0] == 1:
                action = Action(car.id, 1)
                return action
            else:
                action = Action(car.id, 3)
                return action
        raise Exception("You retards")

    def findPairs(self, cars, customers, grid):

        # List of (car, destination) pairs
        assign = []
        for (i, car) in enumerate(cars):
            assign += [(i, (car.position[0], car.position[1]))]

        costumer_d = [Astar(c.position, c.destination, grid) for c in customers]

        # Matrix of distances between cars (rows) and customers (columns)
        distances = []
        c_indices = [c.id for c in customers]
        for car in cars:
            # Initialize all distances as infeasible
            dist_car = [len(grid) * 10 for i in range(len(customers))]
            # If the car can carry more people, add heuristic distances from car to customers
            if not car.available_capacity == 0:
                # TODO: Potentially multiply heuristic by const
                dist_car = [
                    10
                    * Astar(car.position, c.position, grid)
                    / (costumer_d[i] + 0.00001)
                    for i, c in enumerate(customers)
                ]
            c_indices += [c for c in car.customers]
            for other_car in cars:
                if car.id == other_car.id:
                    # Add distances from car to customers destinations
                    car_customers = [
                        get_customer_from_id(id, self.obs.customers)
                        for id in other_car.customers
                    ]
                    dist_car += [
                        Astar(car.position, c.destination, grid) for c in car_customers
                    ]
                else:
                    # Add array of infeasible distances for customers of other cars
                    dist_car += [
                        len(grid) * 10 for i in range(len(other_car.customers))
                    ]

            distances += [dist_car]
        # Some debugging?

        rows, columns = linear_sum_assignment(distances)

        for i in range(len(rows)):
            if c_indices[columns[i]] in cars[rows[i]].customers:
                assign += [
                    (
                        rows[i],
                        get_customer_from_id(
                            c_indices[columns[i]], self.obs.customers
                        ).destination,
                    )
                ]
            else:
                assign += [
                    (
                        rows[i],
                        get_customer_from_id(
                            c_indices[columns[i]], self.obs.customers
                        ).position,
                    )
                ]

        return assign


MAX_DEPTH = 40


def Astar(start, dest, grid):
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    pq = PriorityQueue()
    pq.push(start, 0)

    current_max_depth = 0

    parent = {}
    cost = {}
    depth = {}
    parent[start] = None
    cost[start] = 0
    depth[start] = 0
    while not pq.is_empty():

        curr = pq.pop()

        if curr == dest:
            break

        for dir in directions:
            neighbor = add(curr, dir)
            if neighbor[0] < 0:
                continue
            if neighbor[0] >= len(grid):  # TODO
                continue
            if neighbor[1] < 0:
                continue
            if neighbor[1] >= len(grid[0]):  # TODO
                continue
            if grid[neighbor[1]][neighbor[0]] == False:
                continue

            n_cost = cost[curr] + 1
            if neighbor not in cost.keys() or n_cost < cost[neighbor]:
                cost[neighbor] = n_cost
                priority = n_cost + heuristic(neighbor, dest)
                pq.push(neighbor, priority)
                parent[neighbor] = curr
                if neighbor not in depth.keys():
                    depth[neighbor] = depth[parent[neighbor]] + 1
                    if depth[neighbor] > current_max_depth:
                        current_max_depth = depth[neighbor]
                    if current_max_depth > MAX_DEPTH:
                        distance_heuristic = heuristic(neighbor, dest)
                        distance_start = cost[neighbor]
                        return distance_heuristic + distance_start


    if dest not in parent.keys():
        return len(grid) * 10
    return cost[dest]


def add(x, y):
    s1 = x[0] + y[0]
    s2 = x[1] + y[1]
    return (s1, s2)


def get_customer_from_id(id, customers):
    for c in customers:
        if c.id == id:
            return c
    raise Exception(f"No customer with id {id}")


def heuristic(pos1, pos2):
    (x1, y1) = pos1
    (x2, y2) = pos2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2
