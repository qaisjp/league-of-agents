from classes import Action, PriorityQueue
from scipy.optimize import linear_sum_assignment

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
        self.grid = obs.grid
        self.teams = obs.teams
        self.customers = obs.customers

        team = [t for t in obs.teams if t.id == self.id][0]
        cars = team.cars
        # print(map)
        # print(teams)
        # print(customers)
        # print(team)
        customers = obs.customers
        if (len(customers) == 0):
            # print("No customer")
            actions = []
            for c in cars:
                actions.append(Action(c.id))
            return actions
        # Find closest pairs between cars and customers
        assign = self.findPairs(cars, customers, self.grid)

        actions = []
        for (car_index, dest) in assign:
            car = cars[car_index]
            actions += [self.Astar(car, dest, self.grid)]
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
            if (targ[1] - prev[1] == 1):
                action = Action(car.id, 2)
                return action
            else:
                action = Action(car.id, 0)
                return action
        else:
            if (targ[0] - prev[0] == 1):
                action = Action(car.id, 1)
                return action
            else:
                action = Action(car.id, 3)
                return action
        raise Exception('You retards')

    def findPairs(self, cars, customers, grid):

        # List of (car, destination) pairs
        assign = []
        for (i, car) in enumerate(cars):
            assign += [(i, ((int(len(grid)/2)), (int(len(grid)/2))))]
        loaded_cars = []

        # Matrix of distances between cars (rows) and customers (columns)
        distances = []
        for (i, car) in enumerate(cars):
            dist_car = []

            # Car is carrying a customer
            if (car.available_capacity < car.capacity):
                dist_car = [len(grid)*10]*len(customers)
                loaded_cars.append(i)

            # Car is searching for a customer
            else:
                for customer in customers:
                    # dist_car += [heuristic(cars[i].position, customer.position)]
                    dist_car += [Astar(cars[i], customer.position, grid)]
            distances += [dist_car]
        rows, columns = linear_sum_assignment(distances)

        for i in range(len(rows)):
            assign[rows[i]] = (rows[i], customers[columns[i]].position)

        # Head towards the nearest customer destination
        for i in loaded_cars:
            closest_destination = len(grid)*10
            for j in range(len(cars[i].customers)):
                c = get_customer_from_id(cars[i].customers[j], customers)
                dist_cust = heuristic(cars[i].position, c.destination)
                if dist_cust < closest_destination:
                    assign[i] = (i, c.destination)
        return assign

def Astar(car, dest, grid):
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
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

        for dir in directions:
            neighbor = add(curr, dir)
            if neighbor[0] < 0:
                continue
            if neighbor[0] >= len(grid): #TODO
                continue
            if neighbor[1] < 0:
                continue
            if neighbor[1] >= len(grid[0]): #TODO
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
        return len(grid)*10
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
    return abs(x1 - x2) + abs(y1 - y2)