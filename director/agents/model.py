import torch
import torch.nn as nn
from torch.distributions import Categorical

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class Memory:
    def __init__(self):
        self.actions = []
        self.states = []
        self.logprobs = []
        self.rewards = []
        self.is_terminals = []

    def clear_memory(self):
        del self.actions[:]
        del self.states[:]
        del self.logprobs[:]
        del self.rewards[:]
        del self.is_terminals[:]


class Flatten(nn.Module):
    def forward(self, x):
        return x.view(x.size(0), -1)

class ProjectAction(nn.Module):
    def __init__(self, number_of_actions, number_of_actors):
        super(ProjectAction, self).__init__()
        self.number_of_actions = number_of_actions
        self.number_of_actors = number_of_actors

    def forward(self, x):
        return x.view(x.size(0), self.number_of_actors, self.number_of_actions)

class ActorCritic(nn.Module):
    def __init__(self, num_inputs, number_of_actions, number_of_actors, n_latent_var, small_input = True):
        super(ActorCritic, self).__init__()
        # actor
        if small_input:
            self.action_layer = nn.Sequential(
                nn.Conv2d(num_inputs, 32, 3, stride=2),
                nn.ReLU(),
                nn.Conv2d(32, 64, 2, stride=1),
                nn.ReLU(),
                nn.Conv2d(64, 64, 2, stride=1),
                nn.ReLU(),
                Flatten(),
                nn.Linear(10816, n_latent_var),
                nn.ReLU(),
                nn.Linear(n_latent_var, number_of_actions * number_of_actors),
                ProjectAction(number_of_actions, number_of_actors),
                nn.Softmax(dim=-1),
            )
            # critic
            self.value_layer = nn.Sequential(
                nn.Conv2d(num_inputs, 32, 2, stride=2),
                nn.ReLU(),
                nn.Conv2d(32, 64, 2, stride=1),
                nn.ReLU(),
                Flatten(),
                nn.Linear(1024, n_latent_var),
                nn.ReLU(),
                nn.Linear(n_latent_var, 1),
            )
        else:
            self.action_layer = nn.Sequential(
                nn.Conv2d(num_inputs, 32, 8, stride=4),
                nn.ReLU(),
                nn.Conv2d(32, 64, 4, stride=2),
                nn.ReLU(),
                nn.Conv2d(64, 32, 3, stride=1),
                nn.ReLU(),
                Flatten(),
                nn.Linear(32 * 7 * 7, n_latent_var),
                nn.ReLU(),
                nn.Linear(n_latent_var, number_of_actions * number_of_actors),
                ProjectAction(number_of_actions, number_of_actors),
                nn.Softmax(dim=-1),
            )

            # critic
            self.value_layer = nn.Sequential(
                nn.Conv2d(num_inputs, 32, 8, stride=4),
                nn.ReLU(),
                nn.Conv2d(32, 64, 4, stride=2),
                nn.ReLU(),
                nn.Conv2d(64, 32, 3, stride=1),
                nn.ReLU(),
                Flatten(),
                nn.Linear(32 * 7 * 7, n_latent_var),
                nn.ReLU(),
                nn.Linear(n_latent_var, 1),
            )

    def forward(self, state):
        state = state.float().to(device)
        action_probs = self.action_layer(state)
        return action_probs

    def act_no_memory(self, state):
        state = torch.from_numpy(state).float().to(device)
        action_probs = self.action_layer(state)
        dist = Categorical(action_probs)
        actions = dist.sample()
        return actions

    def act(self, state, memory):
        state = torch.from_numpy(state).float().to(device)
        action_probs = self.action_layer(state)
        dist = Categorical(action_probs)
        actions = dist.sample()

        memory.states.append(state)
        memory.actions.append(actions)
        memory.logprobs.append(dist.log_prob(actions))

        return actions

    def evaluate(self, state, action):
        #TODO
        action_probs = self.action_layer(state)
        dist = Categorical(action_probs)

        action_logprobs = dist.log_prob(action)
        dist_entropy = dist.entropy()

        state_value = self.value_layer(state)

        return action_logprobs, torch.squeeze(state_value), dist_entropy


# def main():
#     ############## Hyperparameters ##############
#     env_name = "LunarLander-v2"
#     # creating environment
#     env = gym.make(env_name)
#     state_dim = env.observation_space.shape[0]
#     action_dim = 4
#     render = False
#     solved_reward = 230  # stop training if avg_reward > solved_reward
#     log_interval = 20  # print avg reward in the interval
#     max_episodes = 50000  # max training episodes
#     max_timesteps = 300  # max timesteps in one episode
#     n_latent_var = 64  # number of variables in hidden layer
#     update_timestep = 2000  # update policy every n timesteps
#     lr = 0.002
#     betas = (0.9, 0.999)
#     gamma = 0.99  # discount factor
#     K_epochs = 4  # update policy for K epochs
#     eps_clip = 0.2  # clip parameter for PPO
#     random_seed = None
#     #############################################

#     if random_seed:
#         torch.manual_seed(random_seed)
#         env.seed(random_seed)

#     memory = Memory()
#     ppo = PPO(state_dim, action_dim, n_latent_var, lr, betas, gamma, K_epochs, eps_clip)
#     print(lr, betas)

#     # logging variables
#     running_reward = 0
#     avg_length = 0
#     timestep = 0

#     # training loop
#     for i_episode in range(1, max_episodes + 1):
#         state = env.reset()
#         for t in range(max_timesteps):
#             timestep += 1

#             # Running policy_old:
#             action = ppo.policy_old.act(state, memory)
#             state, reward, done, _ = env.step(action)

#             # Saving reward and is_terminal:
#             memory.rewards.append(reward)
#             memory.is_terminals.append(done)

#             # update if its time
#             if timestep % update_timestep == 0:
#                 ppo.update(memory)
#                 memory.clear_memory()
#                 timestep = 0

#             running_reward += reward
#             if render:
#                 env.render()
#             if done:
#                 break

#         avg_length += t

#         # stop training if avg_reward > solved_reward
#         if running_reward > (log_interval * solved_reward):
#             print("########## Solved! ##########")
#             torch.save(ppo.policy.state_dict(), "./PPO_{}.pth".format(env_name))
#             break

#         # logging
#         if i_episode % log_interval == 0:
#             avg_length = int(avg_length / log_interval)
#             running_reward = int((running_reward / log_interval))

#             print(
#                 "Episode {} \t avg length: {} \t reward: {}".format(
#                     i_episode, avg_length, running_reward
#                 )
#             )
#             running_reward = 0
#             avg_length = 0


# if __name__ == "__main__":
#     main()
