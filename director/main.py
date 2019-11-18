import json
import os
import time
import argparse
from datetime import datetime
import signal
import random
from copy import copy
import sys
from json import JSONEncoder
import logging
from dashing import HSplit, VSplit, HBrailleChart, Log, Text


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


from agents.client import API
from agents.a_star import AStarAgent
from agents.a_star_v2 import AStarAgentv2
from agents.a_star_v3 import AStarAgentv3
from agents.vezos import Vezos
from agents.rl import RLAgent
from agents.classes import State

parser = argparse.ArgumentParser(description="League of Agents director")

parser.add_argument("-i", metavar="in-file", type=argparse.FileType("rt"))

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
    if t == "RL":
        a = RLAgent(team_name, team_id, json["path"])
    return a


def team_id_to_token(id, available_teams):
    for t in available_teams:
        if t["id"] == id:
            return t["token"]


def create_ui(number_agents):
    ui = VSplit(
        Text("Hello World,\nthis is dashing.", border_color=2),
        Log(title="logs", border_color=5),
        *([HBrailleChart(border_color=2, color=2) for _ in range(number_agents)]),
        title="League of Agents",
    )
    text = ui.items[0]
    log = ui.items[1]
    bcharts = list(ui.items[2:])
    return ui, text, log, bcharts


def create_logger(logs, ui):
    def log(text):
        logs.append(text)
        ui.display()

    return log


def create_charter(chart, ui):
    def c(value):
        chart.append(max(min((float(value) / 100) + 50, 100), 0))
        ui.display()

    return c


def create_displayer(text, ui):
    def d(t):
        text.text = t
        ui.display()

    return d


def find_agent_from_team_id(team_id, agents):
    for a in agents:
        if a.get_team_id() == team_id:
            return a
    raise Exception("No agent with that team id")


def merge_ws(ws):
    _, firs_w = ws[0]
    grid = firs_w.grid
    ticks = firs_w.ticks
    customers = []
    teams = []
    for a, w in ws:
        for t in w.teams:
            if t.id == a.get_team_id():
                teams.append(t)
                for c in w.customers:
                    if c.id not in map(lambda c: c.id, customers):
                        customers.append(c)
    return State(grid, teams, customers, ticks)


def main():
    api = API()
    # api = API(base_url="https://citysimlocal.eu.ngrok.io/")
    try:
        api.stop_game()
    except Exception:
        pass
    args = parser.parse_args()
    data = json.load(args.i)
    agents = []
    available_teams = api.get_team_tokens()
    ui, text, logs, bcharts = create_ui(len(data["agents"]))
    log = create_logger(logs, ui)
    display = create_displayer(text, ui)
    charters = {}
    for i in range(len(data["agents"])):
        chart = create_charter(bcharts[i], ui)
        charters[i] = chart
    log("Starting...")
    ui.display()
    if len(available_teams) < len(data["agents"]):
        for _ in range(len(data["agents"]) - len(available_teams)):
            log("Creating team..")
            token, team_name, id = api.create_team()
            log(f"Created team {team_name}")
            available_teams.append(
                {"id": id, "token": token, "name": team_name}
            )  # add the team created by the api later
    log("Available teams:")
    log(str(available_teams))
    og_teams = copy(available_teams)
    api.start_game()
    for a in data["agents"]:
        log(f"Creating {a['name']}")
        team = available_teams.pop()
        agent = create_agent(a["type"], a["name"], team["id"], a)
        agents.append(agent)
    states = []
    acts = []
    log("Setting up the signal handler...")

    def signal_handler(sig, frame):
        log("You pressed Ctrl+C!")
        log("Exiting...")
        config = {
            "agents": [
                {"type": a.agent_type, "name": a.get_name(), "team_id": a.get_team_id()}
                for a in agents
            ]
        }
        replay = {
            "config": config,
            "steps": [
                {"state": states[i], "acts": acts[i]}
                for i in range(min(len(states), len(acts)))
            ],
        }
        # Save the replay
        d = "-".join((str(datetime.now()).split()))
        d = "_".join((str(datetime.now()).split(":")))
        replay_name = f"{len(agents)}-agents-{d}.json"
        with open(os.path.join("replays", replay_name), "w") as outfile:
            json.dump(replay, outfile, cls=MyEncoder)
        print(f"Wrote replay to replays/{replay_name}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    log("Starting the game...")
    while True:
        # print("Getting the world...")
        world = api.get_world()
        # print("Done!")
        if not world:
            break
        # TODO: remove this API call
        act = []
        ws = []
        for a in agents:
            # print("Acting...")
            w = api.get_world(team_id_to_token(a.get_team_id(), og_teams))
            ws.append((a, w))
            actions = a.act(w)
            act.append({"team": a.get_team_id(), "actions": actions})
            for action in actions:
                if action.direction is not None:
                    # log("Moving a car")
                    # log(f"{action.car_id} -> {action.direction}. Token: {team_id_to_token(a.get_team_id(), og_teams)}")
                    api.move_car(
                        action.car_id,
                        action.direction,
                        team_id_to_token(a.get_team_id(), og_teams),
                    )

        current_tick = w.ticks
        states.append(merge_ws(ws))
        acts.append(act)
        text = "Teams:\n"
        for i, t in enumerate(world.teams):
            a = find_agent_from_team_id(t.id, agents)
            text += f"<{a.agent_type}>: {a.name} ({t.name}): {t.score}\n"
            charters[i](t.score)
        display(text)
        while True:
            # print("Waiting for tick...")
            w = api.get_world()
            # print(w, current_tick)
            if not w:
                break
            if w.ticks is not current_tick:
                if w.ticks > current_tick + 1:
                    log("Unsynced")
                    log(f"{w.ticks - current_tick}")
                break
    log("Game is done")
    # Let's create the game config
    config = {
        "agents": [
            {"type": a.agent_type, "name": a.get_name(), "team_id": a.get_team_id()}
            for a in agents
        ]
    }
    replay = {
        "config": config,
        "steps": [
            {"state": states[i], "acts": acts[i]}
            for i in range(min(len(states), len(acts)))
        ],
    }
    # Save the replay
    d = "-".join((str(datetime.now()).split()))
    d = "_".join((str(datetime.now()).split(":")))
    replay_name = f"{len(agents)}-agents-{d}.json"
    with open(os.path.join("replays", replay_name), "w") as outfile:
        json.dump(replay, outfile, cls=MyEncoder)
    print(f"Wrote replay to replays/{replay_name}")


if __name__ == "__main__":
    main()
