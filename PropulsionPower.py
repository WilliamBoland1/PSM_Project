import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


#Constants (Base power)
BASE_POWER_PORT = 500  # kW for Port motor
BASE_POWER_STARBOARD = 500  # kW for Starboard motor

#Read and prepare data
df = pd.read_csv('data.csv', sep=';')

#Extract the colums from data.csv: Index(['timestamp', 'var', 'value', 'unit']
df['timestamp'] = pd.to_datetime(df['timestamp'])

#Filter data for Port and Starboard motors. It only containts rows in which this is true:
df_Port = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_port_mp/LoadFeedback']
df_Stbd = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_stbd_mp/LoadFeedback']

#Merge Port and Starboard data on 'timestamp'. Align the timevalues (filtering our missmatch)
df_merged = pd.merge(df_Port[['timestamp', 'value']], 
                     df_Stbd[['timestamp', 'value']], 
                     on='timestamp', suffixes=('_port', '_stbd'))

#Calculate propulsion power for each motor (LoadFeedBack [%] times base power)
df_merged['Port_motor_power'] = df_merged['value_port'] / 100 * BASE_POWER_PORT 
df_merged['Starboard_motor_power'] = df_merged['value_stbd'] / 100 * BASE_POWER_STARBOARD
df_merged['total_propulsion_power'] = df_merged['Port_motor_power'] + df_merged['Starboard_motor_power']

#Step 1: Determine midpoint timestamp (determin Route 1 and Route 2)
start_time = df_merged['timestamp'].min()
end_time = df_merged['timestamp'].max()
midpoint_time = start_time + (end_time - start_time) / 2

#Step 2: Split data into Route 1 and Route 2
df_route_1 = df_merged[df_merged['timestamp'] < midpoint_time]
df_route_2 = df_merged[df_merged['timestamp'] >= midpoint_time]

#Step 3: Plot for Route 1 - Separate Propulsion Power
plt.figure(figsize=(12, 6))
plt.plot(df_route_1['timestamp'], df_route_1['Port_motor_power'], label='Port-side propulsion motor', color='blue')
plt.plot(df_route_1['timestamp'], df_route_1['Starboard_motor_power'], label='Starboard-side propulsion motor', color='red')
plt.xlabel('Time')
plt.ylabel('Propulsion Power [kW]')
plt.title('Route 1: Propulsion Power in Separate Engines')
plt.legend(loc='upper right')
plt.grid(True)  # Add grid lines
plt.xticks(rotation=45)  # Rotate x-axis labels for readability
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.tight_layout()  # Adjust layout to avoid clipping
plt.show()

#Plot for Route 1 - Total Propulsion Power
plt.figure(figsize=(12, 6))
plt.plot(df_route_1['timestamp'], df_route_1['total_propulsion_power'], label='Total propulsion power', color='green')
plt.xlabel('Time')
plt.ylabel('Propulsion Power [kW]')
plt.title('Route 1: Total Propulsion Power')
plt.legend(loc='upper right')
plt.grid(True)
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.tight_layout()
plt.show()

#Step 4: Plot for Route 2 - Separate Propulsion Power
plt.figure(figsize=(12, 6))
plt.plot(df_route_2['timestamp'], df_route_2['Port_motor_power'], label='Port-side propulsion motor', color='blue')
plt.plot(df_route_2['timestamp'], df_route_2['Starboard_motor_power'], label='Starboard-side propulsion motor', color='red')
plt.xlabel('Time')
plt.ylabel('Propulsion Power [kW]')
plt.title('Route 2: Propulsion Power in Separate Engines')
plt.legend(loc='upper right')
plt.grid(True)
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.tight_layout()
plt.show()

#Plot for Route 2 - Total Propulsion Power
plt.figure(figsize=(12, 6))
plt.plot(df_route_2['timestamp'], df_route_2['total_propulsion_power'], label='Total propulsion power', color='green')
plt.xlabel('Time')
plt.ylabel('Propulsion Power [kW]')
plt.title('Route 2: Total Propulsion Power')
plt.legend(loc='upper right')
plt.grid(True)
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.tight_layout()
plt.show()
