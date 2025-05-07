import numpy as np
from pydantic import BaseModel
from typing import List, Union
from stable_baselines3 import PPO

class RLRequest(BaseModel):
    state: List[float]

class RLAgent:
    def __init__(self, model_path: str):
        self.model = PPO.load(
            model_path,
            custom_objects={
                "lr_schedule": lambda _: 0.0,
                "clip_range":  lambda _: 0.0,
                "clip_range_vf":lambda _: 0.0,
            },
            force_reset=True,
        )

    def act(self, state: List[float]) -> Union[int, float, List]:
        # prepare a batch of size 1
        obs = np.array(state, dtype=np.float32).reshape(1, -1)
        action, _ = self.model.predict(obs, deterministic=True)
        # action might be e.g. array([2]) or array([[a,b,c]])
        action = np.array(action)[0]
        # if scalar:
        if action.shape == ():
            return action.item()
        # else list:
        return action.tolist()

# instantiate with your trained policy
agent = RLAgent("models/ppo_refined_iteration_3_2025-04-15_16-29-13.zip")
