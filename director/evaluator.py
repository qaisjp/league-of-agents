import numpy as np
from agents.model import ActorCritic
from agents.utils import parse_replay, get_available_customers, get_my_cars_map, get_other_cars_map
import os
from tqdm import tqdm
import random
import json.encoder
from agents.a_star import AStarAgent
from agents.runner import run_game