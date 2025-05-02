from stable_baselines3 import PPO
import os
import numpy as np

def load_agent(model_path="../mesa-del-sol-ppo/ppo_refined"):
    """Load the trained PPO model for microgrid control.
    
    Args:
        model_path: Path to the model file without .zip extension
    Returns:
        PPO model instance
    """
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct full path to the model file, ensuring .zip extension
    full_model_path = os.path.normpath(os.path.join(current_dir, f"{model_path}.zip"))
    
    # Check if file exists
    if not os.path.exists(full_model_path):
        raise FileNotFoundError(f"Model file not found at {full_model_path}")
        
    try:
        model = PPO.load(full_model_path)
        return model
    except Exception as e:
        raise Exception(f"Error loading model from {full_model_path}: {str(e)}")
