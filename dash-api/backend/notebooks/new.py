import os
import math
import warnings
from datetime import datetime, timedelta
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import gridspec
from scipy.stats import zscore
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.exceptions import DataConversionWarning
import gymnasium as gym
from gymnasium import spaces
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.policies import ActorCriticPolicy
import time
from datetime import datetime
import os
import zipfile
import tempfile
import shutil

def read_and_merge_csvs(folder_path):
    # Find all CSV files in the folder
    all_csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    # Read all CSVs into a list of DataFrames
    df_list = [pd.read_csv(file) for file in all_csv_files]

    # Merge all DataFrames (concatenating them)
    merged_df = pd.concat(df_list, ignore_index=True)

    return merged_df

warnings.filterwarnings("ignore", category=UserWarning, message=".*precision lowered by casting to float32.*")
warnings.filterwarnings("ignore", category=UserWarning, message="X does not have valid feature names*")
warnings.filterwarnings("ignore", category=FutureWarning, message=".*torch.load.*weights_only=False.*")


mesa_df = read_and_merge_csvs("/kaggle/input/microgrid-data/other/default/1/2025-03-19-mesa-de-sol-microgrid-data")
price_df = pd.read_csv("/kaggle/input/microgrid-data/other/default/1/2025-03-24-ieso-hourly-ontario-energy-price/PUB_PriceHOEPPredispOR_2024.csv")
wind_df = pd.read_csv("/kaggle/input/microgrid-data/other/default/1/2025-03-30-dwse-wind-data/Wind Time Series Dataset(10min).csv")
critical_load_df = pd.read_csv("/kaggle/input/microgrid-data/other/default/1/2025-03-29-uscd-microgrid-data/BuildingLoad/CenterHall.csv")
non_critical_load_df = pd.read_csv("/kaggle/input/microgrid-data/other/default/1/2025-03-29-uscd-microgrid-data/BuildingLoad/EastCampus.csv")
essential_load_df = pd.read_csv("/kaggle/input/microgrid-data/other/default/1/2025-03-29-uscd-microgrid-data/BuildingLoad/GalbraithHall.csv")
temperature_df = pd.read_csv("/kaggle/input/microgrid-data/other/default/1/2025-04-09-ontario-hourly-temperature/hourly-temperature.csv", usecols=['LOCAL_DATE', 'TEMP'])


# Preprocess and align all datasets to 5-minute intervals (ignores year)
def preprocess_data(mesa_data, price_data, wind_data, critical_load_data, non_critical_load_data, essential_load_data, temperature_data):
    """
    Preprocess and align price and wind data to mesa's timeline.
    Matches based on month, day, hour, and minute, ignoring the year.
    """
    # Create a primary matching key for mesa data
    mesa_data['Timestamp'] = pd.to_datetime(mesa_data['Timestamp'], format='%Y/%m/%d %H:%M:%S', errors='coerce')
    mesa_data = mesa_data.set_index('Timestamp')
    mesa_resampled = mesa_data.resample('5min').mean().interpolate()
    mesa_resampled = mesa_resampled.reset_index()
    mesa_resampled['matching_key'] = mesa_resampled['Timestamp'].dt.strftime('%m-%d %H:%M')
    mesa_unique = mesa_resampled.drop_duplicates(subset=['matching_key'])

    price_data['datetime'] = pd.to_datetime(price_data['Date']) + pd.to_timedelta(price_data['Hour'] - 1, unit='h')
    price_data = price_data.drop(columns=['Date', 'Hour'])
    price_resampled = price_data.set_index('datetime').resample('5min').ffill().reset_index()
    price_resampled['matching_key'] = price_resampled['datetime'].dt.strftime('%m-%d %H:%M')
    price_unique = price_resampled.drop_duplicates(subset=['matching_key'])

    wind_data['Time'] = pd.to_datetime(wind_data['Time'])
    wind_resampled = wind_data.set_index('Time').resample('5min').interpolate().reset_index()
    wind_resampled['matching_key'] = wind_resampled['Time'].dt.strftime('%m-%d %H:%M')
    wind_unique = wind_resampled.drop_duplicates(subset=['matching_key'])
    wind_unique.rename(columns={'Power': 'Wind_Power'}, inplace=True)
    wind_unique.rename(columns={'WindSpeed': 'Wind_Speed'}, inplace=True)
    
    critical_load_data['DateTime'] = pd.to_datetime(critical_load_data['DateTime'])
    critical_load_data = critical_load_data.set_index('DateTime').resample('5min').mean().interpolate()
    critical_load_data = critical_load_data.reset_index()
    critical_load_data['matching_key'] = critical_load_data['DateTime'].dt.strftime('%m-%d %H:%M')
    critical_load_data = critical_load_data.drop_duplicates(subset=['matching_key'])
    critical_load_data.rename(columns={'RealPower': 'Critical_Power_Load'}, inplace=True)
    critical_load_data.drop('ReactivePower', axis=1, inplace=True)
    
    non_critical_load_data['DateTime'] = pd.to_datetime(non_critical_load_data['DateTime'])
    non_critical_load_data = non_critical_load_data.set_index('DateTime').resample('5min').mean().interpolate()
    non_critical_load_data = non_critical_load_data.reset_index()
    non_critical_load_data['matching_key'] = non_critical_load_data['DateTime'].dt.strftime('%m-%d %H:%M')
    non_critical_load_data = non_critical_load_data.drop_duplicates(subset=['matching_key'])
    non_critical_load_data.rename(columns={'RealPower': 'Non_Critical_Power_Load'}, inplace=True)
    non_critical_load_data.drop('ReactivePower', axis=1, inplace=True)
    
    essential_load_data['DateTime'] = pd.to_datetime(essential_load_data['DateTime'])
    essential_load_data = essential_load_data.set_index('DateTime').resample('5min').mean().interpolate()
    essential_load_data = essential_load_data.reset_index()
    essential_load_data['matching_key'] = essential_load_data['DateTime'].dt.strftime('%m-%d %H:%M')
    essential_load_data = essential_load_data.drop_duplicates(subset=['matching_key'])
    essential_load_data.rename(columns={'RealPower': 'Essential_Power_Load'}, inplace=True)
    essential_load_data.drop('ReactivePower', axis=1, inplace=True)
    
    temperature_data['LOCAL_DATE'] = pd.to_datetime(temperature_data['LOCAL_DATE'])
    temperature_data = temperature_data.set_index('LOCAL_DATE').resample('5min').mean().interpolate()
    temperature_data = temperature_data.reset_index()
    temperature_data['matching_key'] = temperature_data['LOCAL_DATE'].dt.strftime('%m-%d %H:%M')
    temperature_data = temperature_data.drop_duplicates(subset=['matching_key'])
    temperature_data.rename(columns = {'TEMP': 'Temperature'}, inplace = True)
    
    # Merge datasets based on the matching key
    merged_data = pd.merge(
        mesa_unique, 
        price_unique.drop(columns=['datetime']), 
        on='matching_key', 
        how='left'
    )
    merged_data = pd.merge(
        merged_data, 
        wind_unique.drop(columns=['Time']), 
        on='matching_key', 
        how='left'
    )
    merged_data = pd.merge(
        merged_data, 
        critical_load_data.drop(columns=['DateTime']), 
        on='matching_key', 
        how='left'
    )
    merged_data = pd.merge(
        merged_data, 
        non_critical_load_data.drop(columns=['DateTime']), 
        on='matching_key', 
        how='left'
    )
    merged_data = pd.merge(
        merged_data, 
        essential_load_data.drop(columns=['DateTime']), 
        on='matching_key', 
        how='left'
    )
    merged_data = pd.merge(
        merged_data, 
        temperature_data.drop(columns=['LOCAL_DATE']), 
        on='matching_key', 
        how='left'
    )
    
    # Set the original mesa timestamps as index
    merged_data = merged_data.set_index('Timestamp').drop(columns=['matching_key'])
    
    # Handle any remaining NaN values
    merged_data = merged_data.interpolate().ffill().bfill()
    
    # Define columns that can logically have negative values
    can_be_negative = [
       'Battery_Active_Power', 
       'Battery_Active_Power_Set_Response',
       'Island_mode_MCCB_Active_Power',
       'Temperature',
    ]
    
    # Set bounds for extreme values
    lower_bound = -9999
    upper_bound = 9999
    
    # Process each column
    for column in merged_data.columns:
       if pd.api.types.is_numeric_dtype(merged_data[column]):
           if column in can_be_negative:
               # For columns that can be negative, only remove extreme values
               mask = (merged_data[column] <= lower_bound) | (merged_data[column] >= upper_bound)
           else:
               # For columns that shouldn't be negative, remove negative values and extremes
               mask = (merged_data[column] < 0) | (merged_data[column] >= upper_bound)
           
           merged_data.loc[mask, column] = np.nan
    
    # Use interpolation to fill missing values (maintains time series patterns)
    merged_data = merged_data.interpolate(method='linear')
    
    # Use forward fill and backward fill for any remaining NaN values at the edges
    merged_data = merged_data.fillna(method='ffill').fillna(method='bfill')
    
    # Use median for any columns that still have NaN values
    for column in merged_data.columns:
       if pd.api.types.is_numeric_dtype(merged_data[column]):
           merged_data[column] = merged_data[column].fillna(merged_data[column].median())


    # Scaling data
    # scale_factor = 1000.0
    # merged_data['Critical_Power_Load'] = df['Critical_Power_Load'] / scale_factor
    # merged_data['Non_Critical_Power_Load'] = df['Non_Critical_Power_Load'] / scale_factor
    # merged_data['Essential_Power_Load'] = df['Essential_Power_Load'] / scale_factor
    

    # Removing major outliers
    columns = ['MG-LV-MSB_AC_Voltage', 'Island_mode_MCCB_AC_Voltage', 'Island_mode_MCCB_AC_Voltage', 'HOEP', 'MG-LV-MSB_Frequency']
    percentile = 90
    for col in columns:
        threshold = merged_data[col].quantile(percentile / 100)
        mean_val = merged_data[col].mean()
        merged_data[col] = merged_data[col].apply(lambda x: mean_val if x > threshold else x)
    
    # Removing columns
    excluded_cols = [
        'OR 10 Min Sync', 'OR 10 Min non-sync', 'OR 30 Min',
        'Hour 1 Predispatch', 'Hour 2 Predispatch', 'Hour 3 Predispatch',
        'Inlet_Temperature_of_Chilled_Water', 'Outlet_Temperature'
    ]
    
    merged_data.drop(columns=excluded_cols, inplace=True)
    
    return merged_data