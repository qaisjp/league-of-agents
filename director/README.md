# Director
The director's job is to start a bunch of agents (based on a config file)
It then uses the admin API to check if enough teams are available
If not, it creates the number of teams needed to start the game

It then starts the simulation and go through the main game loop. Communication is done using the API library, it also keeps a log of all the states and actions to then save them a json file when the game is done

