#!/usr/bin/env python3

import json
import logging
import names

import requests

import lxml.html as lh

from collections import defaultdict
from agents.classes import State, Team, Car, Customer

def log_request(method, url, data=None):
    logging.debug('Sending %s request to %s with data: %s', method, url, data)

def log_response(response):
    logging.debug(
        'Server responded with status code %d, data: %s',
        response.status_code, response.text)

def index_to_coordinates(index, width):
    x = index % width
    y = index // width
    return x, width - y - 1

class Endpoints():
    def __init__(self, base_url):
        super().__init__()

        self.base = base_url

        self.admin = self.base + '/admin'
        self.game_start = self.admin + '/start'
        self.game_stop = self.admin + '/stop'
        self.team = self.admin + '/team'

        self.v1 = self.base + '/api/v1'
        self.world = self.v1 + '/world'
        self.actions = self.v1 + '/actions'

class GameRunningError(Exception):
    pass

def their_team_to_ours(tupl):
    idx, t = tupl
    return Team(idx, t["name"], [], t["score"])

def their_customers_to_our_carcustomers(customers):
    carcustomers = defaultdict(list)
    for idx, c in customers.items():
        carcustomers[str(c["car_id"])].append(idx)
    return carcustomers

class API():
    def __init__(self, base_url="http://localhost:8080"):
        super().__init__()

        self.url = Endpoints(base_url)

    def __send_get_request(self, url, data=None):
        log_request('GET', url)
        r = requests.get(url)
        log_response(r)
        return r

    def __send_put_request(self, url, data=None):
        log_request('PUT', url, data)
        r = requests.put(url, data)
        log_response(r)

    def __send_post_request(self, url, data=None, token=None):
        log_request('POST', url, data)
        if token:
            r = requests.post(url, data, headers={'Authorization': token})
        else:
            r = requests.post(url, data)
        log_response(r)
        return r

    def get_world(self, token=None):
        """
        Queries the API for the world, and returns an observation
        """
        if token:
            r = requests.get(self.url.world, headers={'Authorization': token})
        else:
            r = requests.get(self.url.world)
        world = r.json()

        # If game has ended, world just contains an informative message which is
        # not useful here, just return False in that case
        if 'grid' not in world:
            return False

        width = world["width"]
        assert width == world["height"]

        def their_customer_to_ours(tupl):
            idx, c = tupl
            c = Customer(
                idx,
                index_to_coordinates(c["origin"], width),
                index_to_coordinates(c["destination"], width)
            )
            return c

        def their_cars_to_our_teamcars(cars, carcustomers):
            teamcars = defaultdict(list)
            for idx, c in cars.items():
                our_c = Car(
                    idx,
                    index_to_coordinates(c["position"], width),
                    c["capacity"],
                    c["capacity"] - c["used_capacity"],
                    carcustomers[idx],
                )
                teamcars[str(c["team_id"])].append(our_c)
            return teamcars

        carcustomers = their_customers_to_our_carcustomers(world["customers"])
        teamcars = their_cars_to_our_teamcars(world["cars"], carcustomers)
        grid = []

        k = -1
        for i, b in enumerate(world["grid"]):
            if i % width == 0:
                grid.append([])
                k += 1
                # curr = grid[:-1]
            # print(b)
            grid[k].append(b)

        assert sum(map(len, grid)) == width * width
        assert sum(map(sum, grid)) == sum(world["grid"])

        observation = State(
            grid,
            list(map(their_team_to_ours, world["teams"].items())),
            list(map(their_customer_to_ours, world["customers"].items())),
            world["ticks"]
        )

        # Fill team.cars
        for team in observation.teams:
            team_id = team.id
            # print("teamcars", teamcars)
            team.cars = teamcars[team_id]

        logging.debug('Our world data: %s', observation)
        return observation

    def start_game(self):
        self.__send_put_request(self.url.game_start)
        logging.info('Requested game start')

    def stop_game(self):
        self.__send_put_request(self.url.game_stop)
        logging.info('Requested game start')

    def create_team(self, team_name=None):
        """
        create_team will, given a name, create a team and return its assosciated token.
        """

        if team_name is None:
            team_name = names.get_first_name() + '-and-' + names.get_first_name()

        body = self.__send_post_request(self.url.team, {'team_name': team_name})

        # Store the contents of the website under doc
        doc = lh.fromstring(body.text)
        if body.text.strip() == "Game already running, wait until stops":
            raise GameRunningError()

        tr_elements = doc.xpath('//tr')
        for e in tr_elements:
            if e[1].text_content() == team_name:
                token = e[2].text_content()
                id = e[0].text_content()

        logging.info('Created team %s', team_name)

        return token, team_name, id

    def get_team_tokens(self):
        body = self.__send_get_request(self.url.admin)

        # Store the contents of the website under doc
        doc = lh.fromstring(body.text)
        if body.text.strip() == "Game already running, wait until stops":
            raise GameRunningError()

        tr_elements = doc.xpath('//tr')
        assert tr_elements[0][0].text_content().strip() == "Team ID"
        assert tr_elements[0][1].text_content().strip() == "Team Name"
        assert tr_elements[0][2].text_content().strip() == "Token"

        tokens = []
        for e in tr_elements[1:]:
            tokens.append({
                "id": e[0].text_content().strip(),
                "name": e[1].text_content().strip(),
                "token": e[2].text_content().strip(),
            })
        return tokens

    def move_car(self, car_id, direction, token):
        logging.debug('Moving car ID %d to the %s', car_id, direction)
        request_content = json.dumps({
            'type': 'move',
            'action': {
                'message': 'Moving car ID %s to the %s' % (car_id, direction),
                'CarId': int(car_id),
                'MoveDirection': direction
            }
        })
        self.__send_post_request(self.url.actions, request_content, token)

    def _get_world_legacy(self):
        """
        Queries the API for the world and returns it verbatim
        """
        r = requests.get(self.url.world)
        world = r.json()

        # If game has ended, world just contains an informative message which is
        # not useful here, just return False in that case
        if 'grid' not in world:
            return False

        logging.debug('Updated world data: %s', world)
        return world
