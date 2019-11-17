import numpy as np
from agents.model import ActorCritic
from agents.utils import parse_replay, get_available_customers, get_my_cars_map, get_other_cars_map
import os
from copy import deepcopy
import argparse
from tqdm import tqdm
import random
import json.encoder
from agents.a_star import AStarAgent
from agents.a_star_v2 import AStarAgentv2
from agents.a_star_v3 import AStarAgentv3
from agents.runner import run_game

# logging.basicConfig(level=logging.DEBUG)
def create_agent(t, team_name, team_id, json):
    if(t == "A_STAR"):
        a = AStarAgent(team_name, team_id)
    if(t == "A_STAR_V2"):
        a = AStarAgentv2(team_name, team_id)
    if(t == "A_STAR_V3"):
        a = AStarAgentv3(team_name, team_id)
    return a
def main():
    API_PATH = "http://localhost:8081"
    global_scores = {
        "AStar":[],
        "AStarV2":[],
        "AStarV3":[],
    }
    for i in range(10):
        print(f"Playing game {i+1}")
        scores = {
            "AStar":[],
            "AStarV2":[],
            "AStarV3":[],
        }

        def create_a_star(team_id):
            a = AStarAgent("AStar", team_id)
            return a
        def create_a_star_v2(team_id):
            a = AStarAgentv2("AStarV2", team_id)
            return a
        def create_a_star_v3(team_id):
            a = AStarAgentv3("AStarV3", team_id)
            return a
        def a_star_hook(id,w,actions):
            team = None
            for t in w.teams:
                if t.id == id:
                    team = t
            scores["AStar"].append(team.score)
        def a_star_v2_hook(id,w,actions):
            team = None
            for t in w.teams:
                if t.id == id:
                    team = t
            scores["AStarV2"].append(team.score)
        def a_star_v3_hook(id,w,actions):
            team = None
            for t in w.teams:
                if t.id == id:
                    team = t
            scores["AStarV3"].append(team.score)
        new_pairs = []

        agents_and_hooks = {
            "agents": [
                create_a_star,
                create_a_star_v2,
                create_a_star_v3
            ],
            "hooks": [
                a_star_hook,
                a_star_v2_hook,
                a_star_v3_hook
            ]
        }
        teams = run_game(agents_and_hooks, 500, api_base_url=API_PATH)
        global_scores["AStar"].append(sum(scores["AStar"]))
        global_scores["AStarV2"].append(sum(scores["AStarV2"]))
        global_scores["AStarV3"].append(sum(scores["AStarV3"]))
    print(f"AStar: {sum(global_scores['AStar'])}")
    print(f"AStarV2: {sum(global_scores['AStarV2'])}")
    print(f"AStarV3: {sum(global_scores['AStarV3'])}")
    print(global_scores)
if __name__ == "__main__":
    main()