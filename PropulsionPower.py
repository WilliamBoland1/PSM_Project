import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Constants for base power of motors
BASE_POWER_PORT = 500  # kW for Port motor
BASE_POWER_STARBOARD = 500  # kW for Starboard motor

# Load the data
df = pd.read_csv('data.csv', sep=';')

# Convert timestamp column to datetime format with UTC timezone
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Filter data to keep only LoadFeedback for Port and Starboard motors
df_Port = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_port_mp/LoadFeedback']
df_Stbd = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_stbd_mp/LoadFeedback']

# Merge Port and Starboard data on 'timestamp'
df_merged = pd.merge(df_Port[['timestamp', 'value']], 
                     df_Stbd[['timestamp', 'value']], 
                     on='timestamp', suffixes=('_port', '_stbd'))

# Calculate propulsion power for each motor
df_merged['Port_motor_power'] = df_merged['value_port'] / 100 * BASE_POWER_PORT
df_merged['Starboard_motor_power'] = df_merged['value_stbd'] / 100 * BASE_POWER_STARBOARD
df_merged['total_propulsion_power'] = df_merged['Port_motor_power'] + df_merged['Starboard_motor_power']

#Define the start and stop interval for plotting, ensuring they are timezone-aware (UTC), 1 Genset and 2 Genset 
start_time = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
stop_time = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')

#Get the start and stop timestamps for the whole trip
start_time_tot = df_merged['timestamp'].min()
stop_time_tot = df_merged['timestamp'].max()


#Filter data for the specified interval (Change Interval: start_time/start_time_tot, stop_time/stop_time_tot)
df_interval = df_merged[(df_merged['timestamp'] >= start_time_tot) & (df_merged['timestamp'] <= stop_time_tot)]

#Plot the interval with Port, Starboard, and Total Propulsion Power (Change Interval: start_time/start_time_tot, stop_time/stop_time_tot)
plt.figure(figsize=(12, 6))
plt.plot(df_interval['timestamp'], df_interval['Port_motor_power'], label='Port-side propulsion motor', color='blue')
plt.plot(df_interval['timestamp'], df_interval['Starboard_motor_power'], label='Starboard-side propulsion motor', color='red')
plt.plot(df_interval['timestamp'], df_interval['total_propulsion_power'], label='Total propulsion power', color='green')
plt.xlabel('Time')
plt.ylabel('Propulsion Power [kW]')
plt.title(f'Propulsion Power from {start_time_tot.time()} to {stop_time_tot.time()}')
plt.legend(loc='upper right')
plt.grid(True)
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.tight_layout()
plt.show()
