import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Normal

# Create a custom environment for microgrid simulation
class MicrogridEnv(gym.Env):
    def __init__(self, historical_data, weather_data, market_data):
        super(MicrogridEnv, self).__init__()
        
        # Store historical data for simulation
        self.historical_data = historical_data
        self.weather_data = weather_data
        self.market_data = market_data
        
        # Define action space (battery charging/discharging, grid import/export)
        self.action_space = gym.spaces.Box(
            low=np.array([-1.0, -1.0]),  # Normalized actions
            high=np.array([1.0, 1.0]),   # Normalized actions
            dtype=np.float32
        )
        
        # Define observation space (all state variables)
        self.observation_space = gym.spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),  # Simplified for example
            high=np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1]), # Normalized state
            dtype=np.float32
        )
        
        # Initialize state
        self.reset()
    
    def reset(self):
        # Reset environment to initial state
        self.current_step = 0
        self.battery_soc = 0.5  # Start at 50% state of charge
        self.time_of_day = 0
        # Initialize other state variables
        
        return self._get_observation()
    
    def step(self, action):
        # Process actions (denormalize from [-1, 1] range)
        battery_action = action[0]  # -1: full discharge, 1: full charge
        grid_action = action[1]     # -1: export max, 1: import max
        
        # Update environment state based on actions and dynamics
        # Simulate renewable generation based on weather
        solar_gen = self._get_solar_generation()
        wind_gen = self._get_wind_generation()
        
        # Simulate load demand
        demand = self._get_demand()
        
        # Update battery state
        self._update_battery(battery_action, solar_gen, wind_gen, demand)
        
        # Calculate grid interaction
        grid_import, grid_export = self._calculate_grid_interaction(grid_action, solar_gen, wind_gen, demand)
        
        # Calculate costs and check constraints
        energy_cost = self._calculate_energy_cost(grid_import, grid_export)
        
        # Calculate reward
        reward = self._calculate_reward(energy_cost, grid_import, self.battery_soc)
        
        # Update time
        self.current_step += 1
        done = self.current_step >= self.max_steps
        
        return self._get_observation(), reward, done, {}
    
    def _get_observation(self):
        # Compile all state variables into observation vector
        obs = np.array([
            self.battery_soc,
            self.solar_forecast,
            self.wind_forecast,
            self.demand_forecast,
            self.market_price,
            self.time_of_day,
            # Add other relevant state variables
        ])
        
        return obs
    
    # Additional helper methods for simulation
    def _get_solar_generation(self):
        # Get solar generation based on time and weather
        pass
    
    def _get_wind_generation(self):
        # Get wind generation based on time and weather
        pass
    
    def _get_demand(self):
        # Get demand based on time of day and other factors
        pass
    
    def _update_battery(self, action, solar_gen, wind_gen, demand):
        # Update battery state of charge based on action and energy balance
        pass
    
    def _calculate_grid_interaction(self, action, solar_gen, wind_gen, demand):
        # Calculate grid import/export based on action and energy balance
        pass
    
    def _calculate_energy_cost(self, grid_import, grid_export):
        # Calculate cost based on market prices
        pass
    
    def _calculate_reward(self, energy_cost, grid_import, battery_soc):
        # Calculate reward based on cost, renewable utilization, and battery health
        cost_component = -energy_cost  # Negative cost as part of reward
        
        # Penalize extreme battery states (too full or too empty)
        battery_health_component = -abs(battery_soc - 0.5) * 2
        
        # Reward renewable utilization (less grid import)
        renewable_component = -grid_import * 0.5
        
        # Combine components with appropriate weights
        reward = (cost_component * 0.6 + 
                 battery_health_component * 0.2 + 
                 renewable_component * 0.2)
        
        return reward
    


class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(ActorCritic, self).__init__()
        
        # Shared feature extractor
        self.features = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU()
        )
        
        # Actor network (policy)
        self.actor_mean = nn.Linear(128, action_dim)
        self.actor_log_std = nn.Parameter(torch.zeros(1, action_dim))
        
        # Critic network (value function)
        self.critic = nn.Linear(128, 1)
        
    def forward(self, state):
        features = self.features(state)
        
        # Actor: Output mean and std of a Gaussian distribution for each action
        action_mean = self.actor_mean(features)
        action_std = self.actor_log_std.exp()
        
        # Critic: Output value function estimate
        value = self.critic(features)
        
        return action_mean, action_std, value
    
    def get_action(self, state, deterministic=False):
        state = torch.FloatTensor(state).unsqueeze(0)
        action_mean, action_std, _ = self.forward(state)
        
        if deterministic:
            return action_mean.detach().numpy()[0]
        
        # Create normal distribution
        normal = Normal(action_mean, action_std)
        
        # Sample action and calculate log probability
        action = normal.sample()
        log_prob = normal.log_prob(action).sum(dim=-1)
        
        return action.detach().numpy()[0], log_prob.detach().numpy()[0]
    

class PPO:
    def __init__(self, state_dim, action_dim, lr=3e-4, gamma=0.99, epsilon=0.2, 
                 value_coef=0.5, entropy_coef=0.01):
        self.actor_critic = ActorCritic(state_dim, action_dim)
        self.optimizer = optim.Adam(self.actor_critic.parameters(), lr=lr)
        
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # PPO clipping parameter
        self.value_coef = value_coef  # Value loss coefficient
        self.entropy_coef = entropy_coef  # Entropy coefficient
    
    def update(self, memory):
        # Convert collected experiences to tensors
        states = torch.FloatTensor(memory.states)
        actions = torch.FloatTensor(memory.actions)
        old_log_probs = torch.FloatTensor(memory.log_probs)
        rewards = torch.FloatTensor(memory.rewards)
        dones = torch.FloatTensor(memory.dones)
        
        # Compute returns and advantages
        returns = []
        advantages = []
        value = 0
        
        # Compute GAE (Generalized Advantage Estimation)
        for i in reversed(range(len(rewards))):
            _, _, next_value = self.actor_critic(states[i])
            delta = rewards[i] + self.gamma * next_value * (1 - dones[i]) - value
            advantage = delta + self.gamma * 0.95 * advantage * (1 - dones[i])
            returns.append(value)
            advantages.append(advantage)
        
        returns = torch.tensor(list(reversed(returns)))
        advantages = torch.tensor(list(reversed(advantages)))
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # PPO update
        for _ in range(10):  # Multiple epochs per update
            # Get random indices for minibatches
            indices = np.random.permutation(len(states))
            batch_size = 64
            
            for start in range(0, len(states), batch_size):
                end = start + batch_size
                idx = indices[start:end]
                
                # Get action distributions and values
                action_means, action_stds, values = self.actor_critic(states[idx])
                dist = Normal(action_means, action_stds)
                
                # Calculate new log probabilities
                new_log_probs = dist.log_prob(actions[idx]).sum(dim=-1)
                
                # Calculate ratio for PPO
                ratio = torch.exp(new_log_probs - old_log_probs[idx])
                
                # Calculate surrogate losses
                surr1 = ratio * advantages[idx]
                surr2 = torch.clamp(ratio, 1.0 - self.epsilon, 1.0 + self.epsilon) * advantages[idx]
                
                # Calculate policy loss, value loss, and entropy
                policy_loss = -torch.min(surr1, surr2).mean()
                value_loss = 0.5 * ((values.squeeze() - returns[idx]) ** 2).mean()
                entropy = dist.entropy().mean()
                
                # Combined loss
                loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy
                
                # Perform optimization step
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()



# Memory buffer for collecting experiences
class Memory:
    def __init__(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.dones = []
    
    def add(self, state, action, log_prob, reward, done):
        self.states.append(state)
        self.actions.append(action)
        self.log_probs.append(log_prob)
        self.rewards.append(reward)
        self.dones.append(done)
    
    def clear(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.dones = []

# Training function
def train_ppo(env, state_dim, action_dim, num_episodes=1000):
    ppo = PPO(state_dim, action_dim)
    memory = Memory()
    
    for episode in range(num_episodes):
        state = env.reset()
        episode_reward = 0
        done = False
        
        while not done:
            # Get action from policy
            action, log_prob = ppo.actor_critic.get_action(state)
            
            # Take step in environment
            next_state, reward, done, _ = env.step(action)
            
            # Store experience
            memory.add(state, action, log_prob, reward, done)
            
            # Move to next state
            state = next_state
            episode_reward += reward
            
            # If enough steps collected or episode ended, update policy
            if len(memory.states) >= 2048 or done:
                ppo.update(memory)
                memory.clear()
        
        print(f"Episode {episode}, Reward: {episode_reward}")

def process_data(ieso_data_path, weather_data_path):
    # Load data
    ieso_data = pd.read_csv(ieso_data_path)
    weather_data = pd.read_csv(weather_data_path)
    
    # Synchronize timestamps
    combined_data = pd.merge(ieso_data, weather_data, on='timestamp')
    
    # Normalize all features to [0, 1] range for RL
    for column in combined_data.columns:
        if column != 'timestamp':
            combined_data[column] = (combined_data[column] - combined_data[column].min()) / \
                                   (combined_data[column].max() - combined_data[column].min())
    
    # Create forecast features (e.g., 24-hour ahead predictions)
    for feature in ['solar_irradiance', 'wind_speed', 'load_demand', 'market_price']:
        for i in range(1, 25):
            combined_data[f'{feature}_forecast_{i}h'] = combined_data[feature].shift(-i)
    
    # Drop rows with NaN values (from creating forecast features)
    combined_data = combined_data.dropna()
    
    return combined_data