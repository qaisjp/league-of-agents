import torch
import numpy as np
from model import ActorCritic
from utils import parse_replay, get_available_customers, get_my_cars_map, get_other_cars_map
import os
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import random
import torch.utils.data as utils
import json.encoder

REPLAY = "2-agents-2019-11-16 22_16_45.483047.json"

def process_steps(steps, team_id):
    pairs = []
    for s in steps:
        state = s["state"]
        acts = s["acts"]
        width = len(state.grid)
        size = (width, width)

        inp = np.array([
            state.grid,
            get_other_cars_map(state, team_id, size),
            get_available_customers(state, size),
            *get_my_cars_map(state, team_id, size)
        ], dtype=float)
        team_actions = None
        for a in acts:
            if a["team"] == team_id:
                team_actions = a["actions"]

        output = np.zeros((len(team_actions), 5), dtype=float)
        for i, a in enumerate(sorted(team_actions, key= lambda a: a.car_id)):
            if a.direction == 0:
                output[i] = [1,0,0,0,0]
            if a.direction == 1:
                output[i] = [0,1,0,0,0]
            if a.direction == 2:
                output[i] = [0,0,1,0,0]
            if a.direction == 3:
                output[i] = [0,0,0,1,0]
            if not a.direction:
                output[i] = [0,0,0,0,1]
        pairs.append((inp, output))
    random.shuffle(pairs)
    return list(map(lambda p: p[0], pairs)), list(map(lambda p: p[1], pairs))

def main():
    # 1) Read the json
    replay = open(
        os.path.join(
            os.path.dirname(__file__), os.pardir, "replays", REPLAY
        ),
        "rt",
    )
    obs = json.load(replay)
    replay.close()
    # 2) Parse it and create a dataset of observation -> actions
    rep = parse_replay(obs)
    print(f"Loaded {len(rep['steps'])} steps")
    x, y = process_steps(rep["steps"], '0')
    num_inputs = x[0].shape[0] 
    num_actors = y[0].shape[0]
    tensor_x = torch.stack([torch.Tensor(i) for i in x]) # transform to torch tensors
    tensor_y = torch.stack([torch.Tensor(i) for i in y])
    my_dataset = utils.TensorDataset(tensor_x,tensor_y) # create your datset
    dataloader = utils.DataLoader(my_dataset, batch_size=4,
                        shuffle=True) # create your dataloader
    # 3) Somehow find a way to do supervised learning that way
    model = ActorCritic(num_inputs, 5, num_actors, 100, small_input=True)
    optimizer = optim.Adam(model.parameters())
    criterion = nn.MSELoss()

    for e in range(10):
        losses = []
        for i_batch, sample_batched in tqdm(enumerate(dataloader), total=len(dataloader)): 
            optimizer.zero_grad()
            xx, yy = sample_batched
            predicted_action = model(xx)
            loss = criterion(predicted_action, yy)
            losses.append(loss.item())
            loss.backward()
            optimizer.step()
        losses = np.array(losses)
        print(f"Loss: {losses.mean()}")
    # 4) See if it works
    # 5) Expand and make Dagger later
    torch.save(model.state_dict(), "supervised.th")


if __name__ == "__main__":
    main()
