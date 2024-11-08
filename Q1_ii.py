import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#Constants for base power of motors
BASE_POWER_PORT = 500  # kW for Port motor
BASE_POWER_STARBOARD = 500  # kW for Starboard motor

#Load the data
df = pd.read_csv('data.csv', sep=';')

#Convert timestamp column to datetime format with UTC timezone
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

#Define time intervals for Route 1 and Route 2, ensuring timezone-aware (UTC)
route1_start = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
route1_stop = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
route2_start = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
route2_stop = pd.to_datetime('2024-09-10 07:07:00').tz_localize('UTC')

#Get the start and stop timestamps for the entire trip
start_time_tot = df_merged['timestamp'].min()
stop_time_tot = df_merged['timestamp'].max()

#Filter data for the specified intervals
df_interval = df_merged[(df_merged['timestamp'] >= start_time_tot) & (df_merged['timestamp'] <= stop_time_tot)]
df_route1 = df_merged[(df_merged['timestamp'] >= route1_start) & (df_merged['timestamp'] <= route1_stop)]
df_route2 = df_merged[(df_merged['timestamp'] >= route2_start) & (df_merged['timestamp'] <= route2_stop)]

#Plot for the entire trip
plt.figure(figsize=(12, 8))
plt.plot(df_interval['timestamp'], df_interval['Port_motor_power'], label='Port-side propulsion motor', color='blue')
plt.plot(df_interval['timestamp'], df_interval['Starboard_motor_power'], label='Starboard-side propulsion motor', color='red')
plt.plot(df_interval['timestamp'], df_interval['total_propulsion_power'], label='Total propulsion power', color='green')
plt.xlabel('Time')
plt.ylabel('Propulsion Power [kW]')
plt.title(f'Total Propulsion Power from {start_time_tot.time()} to {stop_time_tot.time()}')
plt.legend(loc='upper right')
plt.grid(True)
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.tight_layout()
plt.show()


#Plot for Route 1
plt.figure(figsize=(12, 8))
plt.plot(df_route1['timestamp'], df_route1['Port_motor_power'], label='Port-side propulsion motor', color='blue')
plt.plot(df_route1['timestamp'], df_route1['Starboard_motor_power'], label='Starboard-side propulsion motor', color='red')
plt.plot(df_route1['timestamp'], df_route1['total_propulsion_power'], label='Total propulsion power', color='green')
plt.xlabel('Time')
plt.ylabel('Propulsion Power [kW]')
plt.title('Propulsion Power for Route 1')
plt.legend(loc='upper right')
plt.grid(True)
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.tight_layout()
plt.show()

#Plot for Route 2
plt.figure(figsize=(12, 8))
plt.plot(df_route2['timestamp'], df_route2['Port_motor_power'], label='Port-side propulsion motor', color='blue')
plt.plot(df_route2['timestamp'], df_route2['Starboard_motor_power'], label='Starboard-side propulsion motor', color='red')
plt.plot(df_route2['timestamp'], df_route2['total_propulsion_power'], label='Total propulsion power', color='green')
plt.xlabel('Time')
plt.ylabel('Propulsion Power [kW]')
plt.title('Propulsion Power for Route 2')
plt.legend(loc='upper right')
plt.grid(True)
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.tight_layout()
plt.show()
