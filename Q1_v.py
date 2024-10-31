import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Constants for base power of motors
BASE_POWER_PORT = 500  # kW for Port motor
BASE_POWER_STARBOARD = 500  # kW for Starboard motor

# Efficiency constants
eta_propulsion_motor = 0.97
eta_switchboard = 0.99
eta_VSD = 0.97
eta_generator = 0.96

genset_power = 450  # [kW]
gensets_total_power = 900  # [kW]

# Efficiency in typical combustion engine, x - Percentage of rated power
def eta_engine(x): 
    return -0.0024*x**2 + 0.402*x + 27.4382

# Load the data
df = pd.read_csv('data.csv', sep=';')

# Convert timestamp column to datetime format with UTC timezone
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Filter data to keep only LoadFeedback for Port and Starboard motors
df_Port = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_port_mp/LoadFeedback']
df_Stbd = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_stbd_mp/LoadFeedback']

#Merge Port and Starboard data on 'timestamp'
df_merged = pd.merge(df_Port[['timestamp', 'value']], 
                     df_Stbd[['timestamp', 'value']], 
                     on='timestamp', suffixes=('_port', '_stbd'))

#Calculate propulsion power for each motor
df_merged['Port_motor_power'] = df_merged['value_port'] / 100 * BASE_POWER_PORT
df_merged['Starboard_motor_power'] = df_merged['value_stbd'] / 100 * BASE_POWER_STARBOARD
df_merged['total_propulsion_power'] = df_merged['Port_motor_power'] + df_merged['Starboard_motor_power']

#Create a new DataFrame for efficiencies: 
df_efficiencies_power = df_merged[['timestamp', 'Port_motor_power', 'Starboard_motor_power', 'total_propulsion_power']].copy()

#Step 1: Calculate Power out of VSD:
df_efficiencies_power['VSD_Port_Power'] = df_efficiencies_power['Port_motor_power'] / eta_propulsion_motor
df_efficiencies_power['VSD_Stbd_Power'] = df_efficiencies_power['Starboard_motor_power'] / eta_propulsion_motor
df_efficiencies_power['VSD_Total_Power'] = df_efficiencies_power['total_propulsion_power'] / eta_propulsion_motor

#Step 2: Calculate Power out of SwitchBoard:
df_efficiencies_power['SW_Port_Power'] = df_efficiencies_power['VSD_Port_Power'] / eta_VSD
df_efficiencies_power['SW_Stbd_Power'] = df_efficiencies_power['VSD_Stbd_Power'] / eta_VSD
df_efficiencies_power['SW_Total_Power'] = df_efficiencies_power['VSD_Total_Power'] / eta_VSD

#Step 3: Calculate Power out of Generator:
df_efficiencies_power['Generator_Port_Power'] = df_efficiencies_power['SW_Port_Power'] / eta_switchboard
df_efficiencies_power['Generator_Stbd_Power'] = df_efficiencies_power['SW_Stbd_Power'] / eta_switchboard
df_efficiencies_power['Generator_Total_Power'] = df_efficiencies_power['SW_Total_Power'] / eta_switchboard

#Step 4: Calculate Power out of Engine:
df_efficiencies_power['Engine_Port_Power'] = df_efficiencies_power['Generator_Port_Power'] / eta_generator
df_efficiencies_power['Engine_Stbd_Power'] = df_efficiencies_power['Generator_Stbd_Power'] / eta_generator
df_efficiencies_power['Engine_Total_Power'] = df_efficiencies_power['Generator_Total_Power'] / eta_generator

#Step 5: Calculate the rate of Power as a percentage
df_efficiencies_power['Engine_Port_Rated_Power'] = df_efficiencies_power['Engine_Port_Power'] / genset_power * 100
df_efficiencies_power['Engine_Stbd_Rated_Power'] = df_efficiencies_power['Engine_Port_Power'] / genset_power * 100
df_efficiencies_power['Engine_Total_Rated_Power'] = df_efficiencies_power['Engine_Total_Power'] / gensets_total_power * 100

#Step 6: Calculate engine efficiency
df_efficiencies_power['Engine_Port_Efficiency'] = df_efficiencies_power['Engine_Port_Rated_Power'].apply(eta_engine) / 100
df_efficiencies_power['Engine_Stbd_Efficiency'] = df_efficiencies_power['Engine_Stbd_Rated_Power'].apply(eta_engine) / 100
df_efficiencies_power['Engine_Total_Efficiency'] = df_efficiencies_power['Engine_Total_Rated_Power'].apply(eta_engine) / 100

#Step 7: Calculate Power efficiency
df_efficiencies_power['Power_Port_Efficiency'] = df_efficiencies_power['Engine_Port_Efficiency'] * eta_generator * eta_propulsion_motor * eta_switchboard * eta_VSD
df_efficiencies_power['Power_Stbd_Efficiency'] = df_efficiencies_power['Engine_Stbd_Efficiency'] * eta_generator * eta_propulsion_motor * eta_switchboard * eta_VSD
df_efficiencies_power['Power_Total_Efficiency'] = df_efficiencies_power['Engine_Total_Efficiency'] * eta_generator * eta_propulsion_motor * eta_switchboard * eta_VSD

# Step 8: Calculate Mean Energy Efficiency
#Calculate the average of Power_Total_Efficiency over the load profile, which we can assume is the energy efficiency 
energy_efficiency = df_efficiencies_power['Power_Total_Efficiency'].mean() * 100  # Convert to percentage

#Print result
print(f"Energy Efficiency (from fuel to propulsion motors): {energy_efficiency:.2f}%")
