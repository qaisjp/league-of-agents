import json
import os
import time
import argparse
from datetime import datetime
import signal
import random
from copy import copy
import sys
import logging

from .client import API
from .classes import State

def team_id_to_token(id, available_teams):
    for t in available_teams:
        if t["id"] == id:
            return t["token"]

def find_agent_from_team_id(team_id, agents):
    for a in agents:
        if a.get_team_id() == team_id:
            return a
    raise Exception("No agent with that team id")

def run_game(agents_and_hooks, max_ticks):
    api = API()
    api.stop_game()
    available_teams = api.get_team_tokens()
    agents = []
    hooks = agents_and_hooks["hooks"]
    if(len(available_teams) < len(agents_and_hooks["agents"])):
        for _ in range(len(agents_and_hooks["agents"]) - len(available_teams)):
            token, team_name, id = api.create_team()
            available_teams.append({
                "id": id,
                "token": token,
                "name": team_name
            })  # add the team created by the api later

    og_teams = copy(available_teams)
    api.start_game()
    for create_agent in agents_and_hooks["agents"]:
        team = available_teams.pop()
        agent = create_agent(team["id"])
        agents.append(agent)
    states = []
    acts = []
    starting_tick = None
    while True:
        # print("Getting the world...")
        world = api.get_world()
        # print("Done!")
        if not world:
            break
        act = []
        ws = []
        if starting_tick is None:
            starting_tick = world.ticks
        for a, h in zip(agents, hooks):
            w = api.get_world(team_id_to_token(a.get_team_id(), og_teams))
            actions = a.act(w)
            h(w, actions)
            for action in actions:
                if action.direction is not None:
                    api.move_car(action.car_id, action.direction, team_id_to_token(a.get_team_id(), og_teams))
        
        current_tick = w.ticks
        if current_tick - starting_tick > max_ticks:
            api.stop_game()
            return
        while True:
            # print("Waiting for tick...")
            w = api.get_world()
            # print(w, current_tick)
            if not w:
                break
            if w.ticks is not current_tick:
                break
