
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
        # print(map)
        # print(teams)
        # print(customers)
        # print(team)
        if(len(customers) == 0):
            print("No customer")
            actions = []
            for c in cars:
                actions.append(Action(c.id))
            return actions
        # Find closest pairs between cars and customers
        assign = self.findPairs(cars, customers, map)

        actions = []
        for (car_index, dest) in assign:
            car = cars[car_index]
            actions += [self.Astar(car, dest, map)]
        return actions

    def Astar(self, car, dest, map):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
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

        bt = dest
        targ = start
        while not bt == start:
            targ = bt
            bt = parent[bt]

        if (targ[0] - bt[0]) == 0:
            if (targ[1] - bt[1] == 1):
                action = Action(car.id, 0)
                return action
            else:
                action = Action(car.id, 2)
                return action
        else:
            if (targ[0] - bt[0] == 1):
                action = Action(car.id, 1)
                return action
            else:
                action = Action(car.id, 3)
                return action

        action = Action(car.id)
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
                    # distances[i][j] = self.Astar(car, customer.position, map)
                    distances[i][j] = heuristic(car.position, customer.position)

        # Finds the (car, customer) pairs with the minimum
        # distance and adds them to assigned destinations
        # print(map)
        while (seeking_cars > 0):
            min_car, min_customer = min_pair(distances)
            # print(assign)
            # print(min_car)
            # print(min_customer)
            # print(customers)
            assign[min_car] = (min_car, customers[min_customer].position)
            for i in range(len(customers)):
                distances[min_car][i] = float("Inf")
            seeking_cars -= 1
        # print(assign)
        return assign


# Helpers for Agent class
def min_pair(distances):
    min_dist = float("Inf")
    min_car = None
    min_customer = 0
    for (car, dists) in enumerate(distances):
        for (customer, dist) in enumerate(dists):
            # print("yo")
            # print(distances)
            # print(distances[car][customer])
            if distances[car][customer] < min_dist:
                min_car = car
                min_customer = customer
    if min_car is None:
        raise Exception("Min car is none")
    return min_car, min_customer


def add(x, y):
    s1 = x[0] + y[0]
    s2 = x[1] + y[1]
    return (s1, s2)


def heuristic(pos1, pos2):
    (x1, y1) = pos1
    (x2, y2) = pos2
    return abs(x1 - x2) + abs(y1 - y2)