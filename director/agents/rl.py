from .classes import Action, PriorityQueue
from scipy.optimize import linear_sum_assignment
import numpy as np
from .model import ActorCritic
from .utils import get_other_cars_map, get_available_customers, get_my_cars_map
import torch.nn as nn
import sys
import torch.optim as optim
import torch

class RLAgent():
    agent_type = "RL"

    def __init__(self, name, team_id, path):
        self.name = name
        self.team_id = team_id
        model = ActorCritic(6, 5, 3, 100, small_input=True)
        model.load_state_dict(torch.load(path))
        self.model = model

    def get_name(self):
        return self.name

    def get_team_id(self):
        return self.team_id

    def act(self, obs):
        width = len(obs.grid)
        size = (width, width)

        inp = np.array([[
            obs.grid,
            get_other_cars_map(obs, self.team_id, size),
            get_available_customers(obs, size),
            *get_my_cars_map(obs, self.team_id, size)
        ]], dtype=float)

        actions = self.model.act_no_memory(inp)
        actions = actions.numpy()[0]
        actions_objs = []
        my_team = list(filter(lambda t: t.id == self.team_id, obs.teams))[0]
        car_ids = sorted(list(map(lambda c: c.id, my_team.cars)))
        assert len(car_ids) == actions.shape[0]
        for i, car_id in enumerate(car_ids):
            # print(car_id, actions[i])
            if(int(actions[i]) > 3):
                a = Action(car_id, None)
            else:
                a = Action(car_id, int(actions[i]))
            actions_objs.append(a)
        return actions_objs