import json
import os
import argparse
from datetime import datetime

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


def create_agent(t, team_name):
    if(t == "A_STAR"):
        a = AStarAgent(team_name)
        return a


def main():
    args = parser.parse_args()
    data = json.load(args.i)
    agents = []
    available_teams = []  # dummy for now
    if(len(available_teams) < agents):
        available_teams.append()  # add the team created by the api later
    # api.start_game()
    for a in data["agents"]:
        team = available_teams.pop()
        agent = create_agent(a["type"], a["name"], team["id"])
        agents.append(agent)
    states = []
    acts = []
    while True:
        world = {}  # api.get_world()
        if not world:
            break
        states.append(world)
        act = []
        for a in agents:
            actions = a.act(world)
            act.append({
                "team": a.get_team_id(),
                "actions": actions
            })
            for action in actions:
                if action.direction:
                    #api.move_car(a.get_team_id(), action.car, action.direction)
                    pass
        acts.append(act)
        # TODO: wait for the tick to pass

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
    replay_name = f"{len(agents)}-agents-{d}"
    with open(os.path.join("replays", replay_name), 'w') as outfile:
        json.dump(replay, outfile)
    print(f"Wrote replay to replays/{replay_name}")

if __name__ == "__main__":
    main()
