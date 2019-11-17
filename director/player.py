# TODO: Have a flag to force one specific type of bot


import json
import os
import time
import argparse
from datetime import datetime
from time import sleep
import signal
import random
from copy import copy
import sys
from json import JSONEncoder
import logging

from agents.client import API
from agents.a_star import AStarAgent
from agents.a_star_v2 import AStarAgentv2
from agents.a_star_v3 import AStarAgentv3
from agents.vezos import Vezos
from agents.classes import State

parser = argparse.ArgumentParser(description="League of Agents player")

parser.add_argument('-api', dest='api', action='store',
                    type=str,
                    help='Api base url')

parser.add_argument('-token', dest='token', action='store',
                    type=str,
                    help='Token')

parser.add_argument('-id', dest='id', action='store',
                    type=str,
                    default=None,
                    help='Team id')

parser.add_argument('-vezos', dest='vezos', action='store_const',
                    const=True,
                    default=False,
                    help='Force Vezos')

parser.add_argument('-v3', dest='v3', action='store_const',
                    const=True,
                    default=False,
                    help='Force V3')

parser.add_argument('-v2', dest='v2', action='store_const',
                    const=True,
                    default=False,
                    help='Force V2')

parser.add_argument('-v1', dest='v1', action='store_const',
                    const=True,
                    default=False,
                    help='Force V1')

# logging.basicConfig(level=logging.DEBUG)
def create_agent(t, team_name, team_id, json):
    if t == "A_STAR":
        a = AStarAgent(team_name, team_id)
    if t == "A_STAR_V2":
        a = AStarAgentv2(team_name, team_id)
    if t == "A_STAR_V3":
        a = AStarAgentv3(team_name, team_id, float(json["alpha"]), float(json["beta"]))
    if t == "VEZOS":
        a = Vezos(team_name, team_id)
    return a


def team_id_to_token(id, available_teams):
    for t in available_teams:
        if t["id"] == id:
            return t["token"]


def main():
    args = parser.parse_args()
    api = API(base_url=args.api)
    print("Waiting for the game to start")
    while True:
        # print("Getting the world...")
        world = api.get_world()
        # print("Done!")
        if not world:
            sleep(1)
            print(".", end="")
        else:
            break
    print("The game is running")
    team_id = None
    for t in world.teams:
        if t.name == "page":
            team_id = t.id
    if(args.vezos):
        print("Using Vezos")
        a = create_agent("VEZOS", "Rioted", args.id if team_id is None else team_id, {})
    elif(args.v3):
        print("Using V3")
        a = create_agent("A_STAR_V3", "Rioted", args.id if team_id is None else team_id, {"alpha": 0.0001, "beta": -0.6})
    elif(args.v2):
        print("Using V2")
        a = create_agent("A_STAR_V2", "Rioted", args.id if team_id is None else team_id, {})
    elif(args.v1):
        print("Using V1")
        a = create_agent("A_STAR", "Rioted", args.id if team_id is None else team_id, {})
    else:
        white_squares = sum(map(sum, world.grid))
        width = len(world.grid)
        print(f"Size is {width}x{width}")
        print(f"{white_squares} squares and {width ** 2 - white_squares} black squares")
        if(width ** 2 - white_squares > 0.6 * width ** 2 and width > 50):
            print("Choosing V3 because a lot of walls (also big map)")
            a = create_agent("A_STAR_V3", "Rioted", args.id if team_id is None else team_id, {"alpha": 0.0001, "beta": -0.6})
        else:
            print("Choosing Vezos/V2 because a lot of open space")
            if(width < 40):
                print("Choosing V2")
                print("Small map")
                a = create_agent("A_STAR_V2", "Rioted", args.id if team_id is None else team_id, {})
            else:
                print("Choosing Vezos")
                a = create_agent("VEZOS", "Rioted", args.id if team_id is None else team_id, {})
    print("ID:")
    print(a.get_team_id())
    previous_w = None
    while True:
        w = api.get_world(args.token)
        if(not w):
            break
        actions = a.act(w)
        for action in actions:
            if action.direction is not None:
                # log("Moving a car")
                # log(f"{action.car_id} -> {action.direction}. Token: {team_id_to_token(a.get_team_id(), og_teams)}")
                api.move_car(
                    action.car_id,
                    action.direction,
                    args.token,
                )

        current_tick = w.ticks
        previous_w = w
        while True:
            # print("Waiting for tick...")
            w = api.get_world()
            sleep(0.1)
            # print(w, current_tick)
            if not w:
                break
            if w.ticks is not current_tick:
                if w.ticks > current_tick + 1:
                    print("Unsynced")
                    print(f"{w.ticks - current_tick}")
                break
    print("Game is done")
    for t in previous_w.teams:
        print(f"=={t.name}==")
        print(t.score)


if __name__ == "__main__":
    main()
