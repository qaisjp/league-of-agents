import json
import os
import argparse
from datetime import datetime
from client import API

parser = argparse.ArgumentParser(description='League of Agents director')

parser.add_argument('-i', metavar='in-file', type=argparse.FileType('rt'))


# Dummy
class AStarAgent:
    agent_type = "A_STAR"

    def __init__(self, name, team_id):
        self.name = name
        self.team_id = team_id

    def get_name(self):
        return self.name

    def get_team_id(self):
        return self.team_id

    def act(self, _):
        return []


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
    args = parser.parse_args()
    data = json.load(args.i)
    agents = []
    available_teams = api.  # dummy for now
    # if(len(available_teams) < agents):
    #     available_teams.append()  # add the team created by the api later
    api.start_game()
    for a in data["agents"]:
        print(f"Creating {a['name']}")
        team = available_teams.pop()
        agent = create_agent(a["type"], a["name"], team["id"])
        agents.append(agent)
    states = []
    acts = []
    while True:
        world = api.get_world()
        if not world:
            break
        current_tick = world["ticks"]
        states.append(world)
        act = []
        for a in agents:
            print("Acting...")
            actions = a.act(world)
            act.append({
                "team": a.get_team_id(),
                "actions": actions
            })
            for action in actions:
                if action.direction:
                    api.move_car(action.car, action.direction, team_id_to_token(a.get_team_id(), available_teams))
        acts.append(act)
        while True:
            print("Waiting for tick...")
            w = api.get_world()
            print(w, current_tick)
            if not w:
                break
            if w["ticks"] is not current_tick:
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
    replay_name = f"{len(agents)}-agents-{d}.json"
    with open(os.path.join("replays", replay_name), 'w') as outfile:
        json.dump(replay, outfile)
    print(f"Wrote replay to replays/{replay_name}")

if __name__ == "__main__":
    main()
