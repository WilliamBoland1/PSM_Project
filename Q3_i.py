import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

#Constants for base power of motors
BASE_POWER_PORT = 500  # kW for Port motor
BASE_POWER_STARBOARD = 500  # kW for Starboard motor
#Efficiency constants 
eta_propulsion_motor = 0.97
eta_switchboard = 0.99
eta_VSD = 0.97
eta_generator = 0.96

genset_power = 450 #[kW]
gensets_total_power = 900 #[kW]

gross_spesific_energy = 45.4 *(1/3.6) #[kWh/kg]

#Efficiency in typical combustion engine, x - Precentage of rated power
def eta_engine(x): 
    return -0.0024*x**2 + 0.402*x + 27.4382

#Load the data
df = pd.read_csv('data.csv', sep=';')

#Convert timestamp column to datetime format with UTC timezone
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

#Filter data to keep only LoadFeedback for Port and Starboard motors
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
#print(df_merged[['Port_motor_power', 'Starboard_motor_power', 'total_propulsion_power']].head())

#Create a new DataFrame for efficiencies: 

df_efficiencies_power = df_merged[['timestamp', 'Port_motor_power', 'Starboard_motor_power', 'total_propulsion_power']].copy()

#Step 1: Calculate Power out of VSD: 

df_efficiencies_power['VSD_Port_Power'] = df_efficiencies_power['Port_motor_power'] / eta_propulsion_motor
df_efficiencies_power['VSD_Stbd_Power'] = df_efficiencies_power['Starboard_motor_power'] /eta_propulsion_motor
df_efficiencies_power['VSD_Total_Power'] = df_efficiencies_power['total_propulsion_power'] /eta_propulsion_motor
#print(df_efficiencies_power[['VSD_Port_Power', 'VSD_Stbd_Power', 'VSD_Total_Power']].head())

#Step 2: Calculate Power out of SwitchBoard: 
df_efficiencies_power['SW_Port_Power'] = df_efficiencies_power['VSD_Port_Power'] / eta_VSD
df_efficiencies_power['SW_Stbd_Power'] = df_efficiencies_power['VSD_Stbd_Power'] / eta_VSD
df_efficiencies_power['SW_Total_Power'] = df_efficiencies_power['VSD_Total_Power'] / eta_VSD
#print(df_efficiencies_power[['SW_Port_Power', 'SW_Stbd_Power', 'SW_Total_Power']].head())

#Step 3: Calculate Power out of Generator: 
df_efficiencies_power['Generator_Port_Power'] = df_efficiencies_power['SW_Port_Power'] / eta_switchboard
df_efficiencies_power['Generator_Stbd_Power'] = df_efficiencies_power['SW_Stbd_Power'] / eta_switchboard
df_efficiencies_power['Generator_Total_Power'] = df_efficiencies_power['SW_Total_Power'] /eta_switchboard
#print(df_efficiencies_power[['Generator_Port_Power', 'Generator_Stbd_Power', 'Generator_Total_Power']].head())

#Step 3: Calculate Power out of Engine: 
df_efficiencies_power['Engine_Port_Power'] = df_efficiencies_power['Generator_Port_Power'] / eta_generator
df_efficiencies_power['Engine_Stbd_Power'] = df_efficiencies_power['Generator_Stbd_Power'] / eta_generator
df_efficiencies_power['Engine_Total_Power'] = df_efficiencies_power['Generator_Total_Power'] / eta_generator
#print(df_efficiencies_power[['Engine_Port_Power', 'Engine_Stbd_Power', 'Engine_Total_Power']].head())

#Step 4: Calculate the rate of Power as a percentage. 
df_efficiencies_power['Engine_Port_Rated_Power'] = df_efficiencies_power['Engine_Port_Power'] / genset_power *100
df_efficiencies_power['Engine_Stbd_Rated_Power'] = df_efficiencies_power['Engine_Stbd_Power'] / genset_power *100
df_efficiencies_power['Engine_Total_Rated_Power'] = df_efficiencies_power['Engine_Total_Power'] / gensets_total_power *100
#print(df_efficiencies_power[['Engine_Port_Rated_Power', 'Engine_Stbd_Rated_Power', 'Engine_Total_Rated_Power']].head())

#Step 5: Calculate engine efficiency: 
df_efficiencies_power['Engine_Port_Efficiency'] = df_efficiencies_power['Engine_Port_Rated_Power'].apply(eta_engine) /100
df_efficiencies_power['Engine_Stbd_Efficiency'] = df_efficiencies_power['Engine_Stbd_Rated_Power'].apply(eta_engine) /100
df_efficiencies_power['Engine_Total_Efficiency'] = df_efficiencies_power['Engine_Total_Rated_Power'].apply(eta_engine) /100
#print(df_efficiencies_power[['Engine_Port_Efficiency', 'Engine_Stbd_Efficiency', 'Engine_Total_Efficiency']].head())


#Step 6: Calculate Power efficiency 
df_efficiencies_power['Power_Port_Efficiency'] = df_efficiencies_power['Engine_Port_Efficiency'] * eta_generator * eta_propulsion_motor * eta_switchboard * eta_VSD * 100
df_efficiencies_power['Power_Stbd_Efficiency'] = df_efficiencies_power['Engine_Stbd_Efficiency'] * eta_generator * eta_propulsion_motor * eta_switchboard * eta_VSD * 100
df_efficiencies_power['Power_Total_Efficiency'] = df_efficiencies_power['Engine_Total_Efficiency'] * eta_generator * eta_propulsion_motor * eta_switchboard * eta_VSD * 100

# Define time intervals for Route 1 and Route 2
route1_start = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
route1_stop = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
route2_start = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
route2_stop = pd.to_datetime('2024-09-10 07:07:00').tz_localize('UTC')

# Filter data for each route
df_route1 = df_efficiencies_power[(df_efficiencies_power['timestamp'] >= route1_start) & (df_efficiencies_power['timestamp'] <= route1_stop)]
df_route2 = df_efficiencies_power[(df_efficiencies_power['timestamp'] >= route2_start) & (df_efficiencies_power['timestamp'] <= route2_stop)]

df_fuel_consumption = df_efficiencies_power[['timestamp', 'Power_Total_Efficiency', 'total_propulsion_power']].copy()

df_fuel_consumption['Fuel_flow_rate_per_hour'] = df_fuel_consumption['total_propulsion_power'] / ((df_fuel_consumption['Power_Total_Efficiency']/100) * gross_spesific_energy)
df_fuel_consumption['Fuel_flow_rate_per_sec'] = df_fuel_consumption['Fuel_flow_rate_per_hour'] / 3600

# Convert timestamps to datetime format if they are not already
df_fuel_consumption['timestamp'] = pd.to_datetime(df_fuel_consumption['timestamp'])

# Calculate time differences in seconds
df_fuel_consumption['Delta_t'] = df_fuel_consumption['timestamp'].diff().dt.total_seconds().fillna(0)

# Calculate fuel consumption for each time step (Fuel_flow_rate * Delta_t)
# Fuel_flow_rate is in units of fuel per second if it represents an instantaneous rate
df_fuel_consumption['Fuel_Consumed'] = df_fuel_consumption['Fuel_flow_rate_per_sec'] * df_fuel_consumption['Delta_t']

# Calculate cumulative fuel consumption
df_fuel_consumption['Cumulative_Fuel_Consumption'] = df_fuel_consumption['Fuel_Consumed'].cumsum()

# Filter data for each route
df_route1 = df_fuel_consumption[(df_fuel_consumption['timestamp'] >= route1_start) & (df_fuel_consumption['timestamp'] <= route1_stop)].copy()
df_route2 = df_fuel_consumption[(df_fuel_consumption['timestamp'] >= route2_start) & (df_fuel_consumption['timestamp'] <= route2_stop)].copy()

# Calculate cumulative fuel consumption for Route 1 and Route 2 separately
df_route1['Cumulative_Fuel_Consumption'] = df_route1['Fuel_Consumed'].cumsum()
df_route2['Cumulative_Fuel_Consumption'] = df_route2['Fuel_Consumed'].cumsum()

# Display the first few rows to verify
##print(df_fuel_consumption[['Fuel_flow_rate_per_sec', 'Delta_t', 'Fuel_Consumed', 'Cumulative_Fuel_Consumption']].head())
##print(df_fuel_consumption[['Fuel_flow_rate_per_sec', 'Delta_t', 'Fuel_Consumed', 'Cumulative_Fuel_Consumption']].tail())

print(f"Kilograms: {df_fuel_consumption['Cumulative_Fuel_Consumption'].iloc[-1]:.2f} [kg]\n")
print(f"Kilograms: {df_route1['Cumulative_Fuel_Consumption'].iloc[-1]:.2f} [kg]\n")
print(f"Kilograms: {df_route2['Cumulative_Fuel_Consumption'].iloc[-1]:.2f} [kg]\n")