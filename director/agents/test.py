import time
import random
from a_star_v3 import *
from classes import *

# Test situation on the given map
grid = [[True, True,  True,  True,  True,  True,  True,  True,  True,  True ],
        [True, False, False, True,  True,  False, True,  False, True,  True ],
        [True, True,  True,  True,  False, False, False, False, True,  True ],
        [True, False, False, True,  False, True,  True,  False, False, True ],
        [True, False, True,  True,  True,  True,  True,  True,  True,  True ],
        [True, False, True,  False, False, True,  True,  False, True,  False],
        [True, False, True,  True,  False, True,  True,  False, True,  True ],
        [True, False, False, True,  False, False, False, False, False, True ],
        [True, True,  True,  True,  False, True,  False, True,  True,  True ],
        [True, True,  False, True,  True,  True,  True,  True,  False, True ]]

car1pos = (5, 5)
car1 = Car("<C1>", car1pos, 4, 4, [])
car2pos = (6, 2)
car2 = Car("<C2>", car2pos, 4, 4, [])
cars = [car1]

cus1pos = (9, 9)
customer1 = Customer("*C1*", cus1pos, (3,8))
cus2pos = (3, 5)
customer2 = Customer("*C2*", cus2pos, (3,8))
cus3pos = (8, 1)
customer3 = Customer("*C3*", cus3pos, (3,8))
#customers = [customer2]
customers = [customer1]

grid[car1pos[1]][car1pos[0]] = car1.id
#grid[car2pos[1]][car2pos[0]] = car2.id
grid[cus1pos[1]][cus1pos[0]] = customer1.id
#grid[cus2pos[0]][cus2pos[1]] = customer2.id
#grid[cus3pos[0]][cus3pos[1]] = customer3.id

score = 0
team = Team("TEAM1", "Bezos", cars, score)
teams = [team]
s = State(grid, teams, customers, 300)

agent = AStarAgentv3("Agent", "TEAM1")

k=1
while(True):
    actions = agent.act(s)
    direction1 = actions[0].direction
    if (direction1==0):
        print("Direction: UP")
        car1pos = (car1pos[0],car1pos[1]-1)
    elif (direction1==1):
        print("Direction: RIGHT")
        car1pos = (car1pos[0]+1,car1pos[1])
    elif (direction1==2):
        print("Direction: DOWN")
        car1pos = (car1pos[0],car1pos[1]+1)
    elif (direction1==3):
        print("Direction: LEFT")
        car1pos = (car1pos[0]-1,car1pos[1])
    else:
        print("Direction: NONE")
    car1.position = car1pos
    """
    direction2 = actions[1].direction
    print("<C2>")
    if (direction2==0):
        print("Direction: UP")
        car2pos = (car2pos[0],car2pos[1]-1)
    elif (direction2==1):
        print("Direction: RIGHT")
        car2pos = (car2pos[0]+1,car2pos[1])
    elif (direction2==2):
        print("Direction: DOWN")
        car2pos = (car2pos[0],car2pos[1]+1)
    elif (direction2==3):
        print("Direction: LEFT")
        car2pos = (car2pos[0]-1,car2pos[1])
    else:
        print("Direction: NONE")
    car2.position = car2pos
    """
    grid = [[True, True,  True,  True,  True,  True,  True,  True,  True,  True ],
            [True, False, False, True,  True,  False, True,  False, True,  True ],
            [True, True,  True,  True,  False, False, False, False, True,  True ],
            [True, False, False, True,  False, True,  True,  False, False, True ],
            [True, False, True,  True,  True,  True,  True,  True,  True,  True ],
            [True, False, True,  False, False, True,  True,  False, True,  False],
            [True, False, True,  True,  False, True,  True,  False, True,  True ],
            [True, False, False, True,  False, False, False, False, False, True ],
            [True, True,  True,  True,  False, True,  False, True,  True,  True ],
            [True, True,  False, True,  True,  True,  True,  True,  False, True ]]
    grid[car1pos[1]][car1pos[0]] = car1.id
    if (car1pos==cus1pos or (k%8)==0):
        k = 0
        cus1pos = (int(9*random.random()), int(9*random.random()))
        customer1.position = cus1pos
        while grid[cus1pos[1]][cus1pos[0]] is False:
            cus1pos = (int(9*random.random()), int(9*random.random()))
            customer1.position = cus1pos
    grid[cus1pos[1]][cus1pos[0]] = customer1.id
    print("\n")
    for i in range(10):
        print("    ", end="")
        for j in range(10):
            if (grid[i][j]==True):
                print("    ", end = " ")
            elif (grid[i][j]==False):
                print("☐☐☐☐", end = " ")
            else:
                print(grid[i][j], end = " ")
        print("\n")
    k += 1
    time.sleep(0.2)
