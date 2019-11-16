#!/usr/bin/env python3

import enum
import json
import logging
import random
import time

import names
import requests

import lxml.html as lh

from collections import defaultdict

LOG_LEVEL = logging.INFO

def log_request(method, url, data=None):
    logging.debug('Sending %s request to %s with data: %s', method, url, data)

def log_response(response):
    logging.debug(
        'Server responded with status code %d, data: %s',
        response.status_code, response.text)

def index_to_coordinates(index, width):
    x = index % width
    y = index // width
    return x, y

def coordinates_to_index(x, y, width):
    return x + width * y

# TODO move into CarDirection
def get_position_after_move(from_x, from_y, direction):
    after_x, after_y = from_x, from_y

    if direction == CarDirection.north:
        after_y += 1
    elif direction == CarDirection.east:
        after_x += 1
    elif direction == CarDirection.south:
        after_y -= 1
    elif direction == CarDirection.west:
        after_x -= 1

    return after_x, after_y

def position_is_passable(x, y, world):
    index = coordinates_to_index(x, y, world['width'])
    grid = world['grid']
    return grid[index]

def position_is_inside_bounds(x, y, world):
    return 0 <= x < world['width'] and 0 <= y < world['height']

def directions_are_opposites(d1, d2):
    # This is based on the values assigned to the enum ¯\_(ツ)_/¯
    if (d1.value + d2.value) % 2 == 0:
        logging.debug('%s and %s are opposites', d1, d2)
        return True
    logging.debug('%s and %s are not opposites', d1, d2)
    return False

class CarDirection(enum.Enum):
    north = 0
    east = 1
    south = 2
    west = 3

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
    return {
        "id": idx,
        "name": t["name"],
        "cars": [],
        "score": t["score"],
    }

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

    def get_world(self):
        """
        Queries the API for the world, and returns an observation
        """
        r = requests.get(self.url.world)
        world = r.json()

        # If game has ended, world just contains an informative message which is
        # not useful here, just return False in that case
        if 'grid' not in world:
            return False

        width = world["width"]

        def their_customer_to_ours(tupl):
            idx, c = tupl
            return {
                "id": idx,
                "position": index_to_coordinates(width, c["origin"]),
                "destination": index_to_coordinates(width, c["destination"]),
            }

        def their_cars_to_our_teamcars(cars, carcustomers):
            teamcars = defaultdict(list)
            for idx, c in cars.items():
                our_c = {
                    "id": idx,
                    "position": index_to_coordinates(width, c["position"]),
                    "capacity": c["capacity"],
                    "available_capacity": c["capacity"] - c["used_capacity"],
                    "customers": carcustomers[idx],
                }
                teamcars[str(c["team_id"])].append(our_c)
            return teamcars

        carcustomers = their_customers_to_our_carcustomers(world["customers"])
        teamcars = their_cars_to_our_teamcars(world["cars"], carcustomers)

        observation = {
            "map": [],
            "teams": list(map(their_team_to_ours, world["teams"].items())),
            "customers": list(map(their_customer_to_ours, world["customers"].items())),
            "ticks": world["ticks"]
        }

        # Fill team.cars
        for team in observation["teams"]:
            team_id = team["id"]
            # print("teamcars", teamcars)
            team["cars"] = teamcars[team_id]

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
        logging.debug('Moving car ID %d to the %s', car_id, direction.name)
        request_content = json.dumps({
            'type': 'move',
            'action': {
                'message': 'Moving car ID %s to the %s' % (car_id, direction.name),
                'carId': int(car_id),
                'moveDirection': direction.value
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

def get_next_direction(world, position, previous_direction):
    """Returns the direction to be followed in the next turn

    If it's possible to continue moving in the current one, that will be
    chosen. Otherwise a different, random direction will be tried until one
    that is possible is found. If a move is not possible in any direction,
    return None.
    """

    logging.debug(
        'Checking available directions from %s, starting from %s',
        repr(index_to_coordinates(position, world['width'])),
        previous_direction.name)

    possible_directions = []
    for direction in CarDirection:
        if move_in_direction_is_possible(position, direction, world):
            logging.debug('Direction %s is available', direction.name)
            possible_directions.append(direction)

    if len(possible_directions) == 0:
        # Dynamic constraint must have trapped the car somewhere
        logging.info('No directions are available')
        return None

    if len(possible_directions) == 1:
        logging.debug('Only direction %s is available, returning it')
        return possible_directions[0]

    if len(possible_directions) == 2:
        if previous_direction in possible_directions:
            logging.debug('Only forward and backward directions available, '
                          'returning %s (forward)', previous_direction)
            return previous_direction
        logging.info('90-degree turn, finding non-backwards direction')
        if directions_are_opposites(previous_direction, possible_directions[0]):
            return possible_directions[1]
        else:
            return possible_directions[0]
    if len(possible_directions) == 3 or len(possible_directions) == 4:
        # 3/4-way intersection, return any direction that's not the opposite
        # of the current one
        random.shuffle(possible_directions)
        for direction in possible_directions:
            if not directions_are_opposites(previous_direction, direction):
                return direction


def move_in_direction_is_possible(from_position, direction, world):
    from_x, from_y = index_to_coordinates(from_position, world['width'])
    logging.debug(
        'Checking if it is possible to move %s from (%d, %d)', direction.name,
        from_x, from_y)

    new_x, new_y = get_position_after_move(from_x, from_y, direction)

    if not position_is_inside_bounds(new_x, new_y, world):
        logging.debug(
            'Cannot move %s because new position would be outside the grid',
            direction.name)
        return False

    if not position_is_passable(new_x, new_y, world):
        logging.debug(
            'Cannot move %s because the new position (%d, %d) is not passable',
            direction.name, new_x, new_y)
        return False

    logging.debug(
        'Yes, new position would be (%d, %d)', new_x, new_y)
    return True

def move_cars(api, token, world, previous_car_directions=None):
    """Try to move all cars forward in their current direction. If not
    possible, change direction and move.

    Returns the new directions
    """

    cars = {car_id: world['cars'][car_id]
            for car_id, car in world['cars'].items()}

    logging.debug('Previous car directions: %s', previous_car_directions)
    if not previous_car_directions:
        previous_car_directions = {
            car_id: CarDirection.north for car_id in cars.keys()}

    new_directions = {}
    for car_id, car in cars.items():
        if car_id not in previous_car_directions:
            continue
        previous_direction = previous_car_directions[car_id]
        new_direction = None

        new_direction = get_next_direction(
            world, car['position'], previous_direction)

        if new_direction:
            old_coordinates = index_to_coordinates(
                car['position'], world['width'])

            old_x, old_y = old_coordinates
            new_coordinates = get_position_after_move(
                old_x, old_y, new_direction)

            team_name = world['teams'][str(car['team_id'])]['name']
            logging.info(
                'Moving car %s of team %s %s (from %s to %s)', car_id,
                team_name, new_direction.name, repr(old_coordinates),
                repr(new_coordinates))

            api.move_car(car_id, new_direction, token)

            new_directions[car_id] = new_direction

        else:
            # The car cannot be moved anywhere! A dynamic constraint must have
            # appeared. Just leave its previous direction as it was
            new_directions[car_id] = previous_direction
            logging.info('Car %s cannot move anywhere', car_id)

    logging.debug('After moving, car directions are: %s', new_directions)

    return new_directions

def main():
    # Setup
    logging.basicConfig(level=LOG_LEVEL)
    logging.info('Setup complete')
    if LOG_LEVEL != logging.DEBUG:
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    api = API()
    try:
        token = api.create_team()
    except GameRunningError:
        api.stop_game()
        token = api.create_team()

    print(api.get_team_tokens())

    api.start_game()
    world = api._get_world_legacy()

    previous_car_directions = {}
    while True:
        logging.info('Starting new iteration')
        world = api._get_world_legacy()
        if not world:
            # Game must have ended, start it again
            logging.info('Game ended, starting again')
            api.start_game()
            continue

        new_car_directions = move_cars(api, token, world, previous_car_directions)
        previous_car_directions = new_car_directions
        time.sleep(1)
        print("SLEEP")
        oworld = api.get_world()
        print(oworld)

if __name__ == '__main__':
    main()
