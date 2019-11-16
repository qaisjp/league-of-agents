
from .classes import State, Team, Car, Customer, Action, PriorityQueue

class AStarAgent():
    agent_type = "A_STAR"

    def __init__(self, name, team_id):
        self.name = name
        self.id = team_id

    def get_name(self):
        return self.name

    def get_team_id(self):
        return self.id

    def act(self, obs):
        # Obtain variables
        map = obs.grid
        teams = obs.teams
        customers = obs.customers

        team = [t for t in teams if t.id == self.id][0]
        cars = team.cars

        # Find closest pairs between cars and customers
        assign = self.findPairs(cars, customers, map)

        actions = []
        for (car, dest) in assign:
            actions += [self.Astar(car, dest, map)]

        return actions

    def Astar(self, car, dest, map):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        final_dir = -1
        start = car.position

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
                if neighbor[0] >= len(map):
                    continue
                if neighbor[1] < 0:
                    continue
                if neighbor[1] >= len(map[0]):
                    continue
                if map[neighbor[0]][neighbor[1]] == 0:
                    continue

                n_cost = cost[curr] + 1
                if neighbor not in cost or n_cost < cost[neighbor]:
                    cost[neighbor] = n_cost
                    priority = n_cost + heuristic(neighbor, dest)
                    pq.push(neighbor, priority)
                    parent[neighbor] = curr
                    if curr == start:
                        final_dir = i

        action = Action(car.id, final_dir)
        return action

    def findPairs(self, cars, customers, map):
        # List of (car, destination) pairs
        assign = []
        for car in cars:
            assign += [(0, (0, 0))]
        seeking_cars = 0

        # List of (list of distances from car to customer) for each car
        distances = []
        for car in cars:
            distc = []
            for customer in customers:
                distc += [float("Inf")]
            distances += [distc]

        for (i, car) in enumerate(cars):

            # Car is carrying a customer
            if (car.available_capacity < car.capacity):
                assign[i] = (i, car.customers[0].destination)

            # Car is searching for a customer
            else:
                seeking_cars += 1
                for (j, customer) in enumerate(customers):
                    distances[i][j] = self.Astar(car, customer.position, map)

        # Finds the (car, customer) pairs with the minimum
        # distance and adds them to assigned destinations
        while (seeking_cars > 0):
            min_car, min_customer = min_pair(distances)
            assign[min_car] = (min_car, customers[min_customer].position)
            for i in range(len(customers)):
                distances[min_car][i] = float("Inf")
            seeking_cars -= 1

        return assign


# Helpers for Agent class
def min_pair(distances):
    min_dist = float("Inf")
    min_car = 0
    min_customer = 0
    for (car, dists) in enumerate(distances):
        for (customer, dist) in enumerate(dists):
            if distances[car][customer] < min_dist:
                min_car = car
                min_customer = customer
    return min_car, min_customer


def add(x, y):
    s1 = x[0] + y[0]
    s2 = x[1] + y[1]
    return (s1, s2)


def heuristic(pos1, pos2):
    (x1, y1) = pos1
    (x2, y2) = pos2
    return abs(x1 - x2) + abs(y1 - y2)