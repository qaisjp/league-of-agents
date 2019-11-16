import json
import os
import argparse
from datetime import datetime
import signal
from copy import copy
import sys
from json import JSONEncoder
import logging
class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__   
from client import API
from agents.a_star import AStarAgent

parser = argparse.ArgumentParser(description='League of Agents director')

parser.add_argument('-i', metavar='in-file', type=argparse.FileType('rt'))

# logging.basicConfig(level=logging.DEBUG)
def create_agent(t, team_name, team_id):
    if(t == "A_STAR"):
        a = AStarAgent(team_name, team_id)
        return a

def team_id_to_token(id, available_teams):
    for t in available_teams:
        if t["id"] == id:
            return t["token"]

def main():
    api = API()
    api.stop_game()
    args = parser.parse_args()
    data = json.load(args.i)
    agents = []
    available_teams = api.get_team_tokens()  # dummy for now
    if(len(available_teams) < len(data["agents"])):
        for _ in range(len(data["agents"]) - len(available_teams)):
            print("Creating team..")
            token, team_name, id = api.create_team()
            available_teams.append({
                "id": id,
                "token": token,
                "name": team_name
            })  # add the team created by the api later
    print("Available teams:")
    print(available_teams)
    og_teams = copy(available_teams)
    api.start_game()
    for a in data["agents"]:
        print(f"Creating {a['name']}")
        team = available_teams.pop()
        agent = create_agent(a["type"], a["name"], team["id"])
        agents.append(agent)
    states = []
    acts = []
    print("Setting up the signal handler...")
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        print('Exiting...')
        config = {
            "agents": [{"type": a.agent_type, "name": a.get_name(), "team_id": a.get_team_id()} for a in agents]
        }
        replay = {
            "config": config,
            "steps": [{"state": states[i], "acts": acts[i]} for i in range(len(states))]
        }
        # Save the replay
        d = "-".join((str(datetime.now()).split()))
        d = "_".join((str(datetime.now()).split(":")))
        replay_name = f"{len(agents)}-agents-{d}.json"
        with open(os.path.join("replays", replay_name), 'w') as outfile:
            json.dump(replay, outfile, cls=MyEncoder)
        print(f"Wrote replay to replays/{replay_name}")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    print("Starting the game...")
    while True:
        # print("Getting the world...")
        world = api.get_world()
        # print("Done!")
        if not world:
            break
        current_tick = world.ticks
        states.append(world)
        act = []
        for a in agents:
            # print("Acting...")
            w = api.get_world(team_id_to_token(a.get_team_id(), og_teams))
            actions = a.act(w)
            act.append({
                "team": a.get_team_id(),
                "actions": actions
            })
            for action in actions:
                # print(vars(action))
                if action.direction and action.direction != -1:
                    print("Moving a car")
                    print(action.car_id, action.direction, team_id_to_token(a.get_team_id(), og_teams))
                    print(action.car_id)
                    print(action.direction)
                    api.move_car(action.car_id, action.direction, team_id_to_token(a.get_team_id(), og_teams))
        acts.append(act)
        while True:
            # print("Waiting for tick...")
            w = api.get_world()
            # print(w, current_tick)
            if not w:
                break
            if w.ticks is not current_tick:
                break
    print("Game is done")
    # Let's create the game config
    config = {
        "agents": [{"type": a.agent_type, "name": a.get_name(), "team_id": a.get_team_id()} for a in agents]
    }
    replay = {
        "config": config,
        "steps": [{"state": states[i], "acts": acts[i]} for i in range(len(states))]
    }
    # Save the replay
    d = "-".join((str(datetime.now()).split()))
    d = "_".join((str(datetime.now()).split(":")))
    replay_name = f"{len(agents)}-agents-{d}.json"
    with open(os.path.join("replays", replay_name), 'w') as outfile:
        json.dump(replay, outfile)
    print(f"Wrote replay to replays/{replay_name}")

if __name__ == "__main__":
    main()
