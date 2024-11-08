import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


############################## Q1_iii #######################################

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


#################################### Q3 #####################################

# Constants for base power of motors
BASE_POWER_PORT = 500  # kW for Port motor
BASE_POWER_STARBOARD = 500  # kW for Starboard motor

# Density assumed
density = 0.82

#energy content
energy_fuel = 45.4 #[MJ/kg]

# Load the data
df = pd.read_csv('data.csv', sep=';')
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Filter data for genset (engine load) and propulsion motor LoadFeedback data
df_engine_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/fuel_consumption']
df_engine_3 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/fuel_consumption']
df_Port = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_port_mp/LoadFeedback']
df_Stbd = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_stbd_mp/LoadFeedback']

df_engine_1['value'] = df_engine_1['value']*density #[kg/h]
df_engine_3['value'] = df_engine_3['value']*density

df_engine_1['value'] = df_engine_1['value']*energy_fuel #[MJ/h]
df_engine_3['value'] = df_engine_3['value']*energy_fuel

conversion_ratio_megajoule_to_kilowatt = 3.6

df_engine_1['value'] = df_engine_1['value']/conversion_ratio_megajoule_to_kilowatt #[kW]
df_engine_3['value'] = df_engine_3['value']/conversion_ratio_megajoule_to_kilowatt

#ROUTES CODE
#_____________________________________________
# Define the adjustable start and stop interval for plotting
#route 1
start_time = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
stop_time = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')

#Route 2
# start_time = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
# stop_time = pd.to_datetime('2024-09-10 07:7:00').tz_localize('UTC')

#Max time
start_time = df_engine_1['timestamp'].min()
stop_time = df_engine_1['timestamp'].max()

#Filter data for the chosen interval (adjust here: start_time/start_time_tot, stop_time/stop_time_tot)
df_engine_1 = df_engine_1[(df_engine_1['timestamp'] >= start_time) & (df_engine_1['timestamp'] <= stop_time)]
df_engine_3 = df_engine_3[(df_engine_3['timestamp'] >= start_time) & (df_engine_3['timestamp'] <= stop_time)]

#Filter data for the chosen interval (adjust here: start_time/start_time_tot, stop_time/stop_time_tot)
df_Port = df_Port[(df_Port['timestamp'] >= start_time) & (df_Port['timestamp'] <= stop_time)]
df_Stbd = df_Stbd[(df_Stbd['timestamp'] >= start_time) & (df_Stbd['timestamp'] <= stop_time)]
#_____________________________________________

# Merge engine 1 and engine 3 data on 'timestamp' and calculate total engine load
df_engine_loads = pd.merge(df_engine_1[['timestamp', 'value']], df_engine_3[['timestamp', 'value']], on='timestamp', suffixes=('_engine1', '_engine3'))

# Fill NaN values with 0 for engine 3 if it's sometimes off
# df_engine_loads = df_engine_loads.fillna({'value_engine3': 0})
df_engine_loads = df_engine_loads.rename(columns={'value_engine1': 'engine1_load', 'value_engine3': 'engine3_load'})

# Calculate total engine load as the sum of Engine 1 and Engine 3 loads
df_engine_loads['total_engine_load'] = df_engine_loads['engine1_load'] + df_engine_loads['engine3_load']

# Filter and merge Port and Starboard data on 'timestamp' to get propulsion power
df_merged = pd.merge(df_Port[['timestamp', 'value']], df_Stbd[['timestamp', 'value']], on='timestamp', suffixes=('_port', '_stbd'))
df_merged['Port_motor_power'] = df_merged['value_port'] / 100 * BASE_POWER_PORT
df_merged['Starboard_motor_power'] = df_merged['value_stbd'] / 100 * BASE_POWER_STARBOARD
df_merged['total_propulsion_power'] = df_merged['Port_motor_power'] + df_merged['Starboard_motor_power']

# Merge total engine load with propulsion data on 'timestamp'
df_final = pd.merge(df_merged, df_engine_loads[['timestamp', 'total_engine_load']], on='timestamp', how='inner')

# Calculate efficiency, handling cases where total engine load is zero
df_final['efficiency'] = (df_final['total_propulsion_power'] / df_final['total_engine_load']).where(df_final['total_engine_load'] > 0) * 100

#ENERGY EFFICIENCY GIVEN AS MEAN OF POWER EFFICIENCY PAGE 152 compendium
mean = df_final['efficiency'].mean()

# Combined Plot for Power Efficiency and Total Efficiency
plt.figure(figsize=(12, 6))

# Plot Power Efficiency from Genset to Propulsion Motors
plt.plot(df_final['timestamp'], df_final['efficiency'], label='Power Efficiency Q2', color='purple')

# Plot Total Efficiency
plt.plot(df_efficiencies_power['timestamp'], df_efficiencies_power['Power_Total_Efficiency'], label='Power Efficiency Q1', color='blue')

# Adding labels, title, and formatting
plt.xlabel('Time')
plt.ylabel('Efficiency (%)')
plt.title('Power Efficiency Q2 and Power Efficiency Q1 Over Time')
plt.legend(loc='upper right')
plt.grid(True)
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.tight_layout()

# Show plot
plt.show()

# Plot efficiency over time
plt.figure(figsize=(12, 6))
plt.plot(df_final['timestamp'], df_final['efficiency'], label='Power Efficiency', color='purple')
plt.xlabel('Time')
plt.ylabel('Efficiency ηp [%]')
plt.title('Power Efficiency from Genset to Propulsion Motors Over Time')
plt.legend(loc='upper right')
plt.grid(True)
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.tight_layout()
plt.show()

#Step 7: Plot power efficiency
plt.figure(figsize=(12, 6)) 
plt.plot(df_efficiencies_power['timestamp'], df_efficiencies_power['Power_Total_Efficiency'], label='Total Efficiency')
plt.title('Q1 Engine Power Efficiencies Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Efficiency (%)')
plt.legend()
plt.grid(True)
plt.show()


# Route 1 plot
plt.figure(figsize=(12, 6))
#plt.plot(df_route1['timestamp'], df_route1['Power_Port_Efficiency'], label='Port Efficiency')
#plt.plot(df_route1['timestamp'], df_route1['Power_Stbd_Efficiency'], label='Stbd Efficiency')
plt.plot(df_route1['timestamp'], df_route1['Power_Total_Efficiency'], label='Total Efficiency')
plt.title('Q1 Engine Power Efficiencies Over Time - Route 1')
plt.xlabel('Timestamp')
plt.ylabel('Efficiency (%)')
plt.legend()
plt.grid(True)
plt.show()

# Route 2 plot
plt.figure(figsize=(12, 6))
#plt.plot(df_route2['timestamp'], df_route2['Power_Port_Efficiency'], label='Port Efficiency')
#plt.plot(df_route2['timestamp'], df_route2['Power_Stbd_Efficiency'], label='Stbd Efficiency')
plt.plot(df_route2['timestamp'], df_route2['Power_Total_Efficiency'], label='Total Efficiency')
plt.title(' Q1 Engine Power Efficiencies Over Time - Route 2')
plt.xlabel('Timestamp')
plt.ylabel('Efficiency (%)')
plt.legend()
plt.grid(True)
plt.show()