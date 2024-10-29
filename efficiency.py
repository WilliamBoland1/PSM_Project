import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Constants for base power of motors
BASE_POWER_PORT = 500  # kW for Port motor
BASE_POWER_STARBOARD = 500  # kW for Starboard motor

# Load the data
df = pd.read_csv('data.csv', sep=';')
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Filter data for genset (engine load) and propulsion motor LoadFeedback data
df_engine_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/engine_load']
df_engine_3 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/engine_load']
df_Port = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_port_mp/LoadFeedback']
df_Stbd = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_stbd_mp/LoadFeedback']

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
# start_time = df_engine_1['timestamp'].min()
# stop_time = df_engine_1['timestamp'].max()

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

#______________________________________________________________________________________________________________________________

#Finding mean efficiency using the IQR method, according to page 152 in the compendium this answers to the energy efficiency
mean = df_final['efficiency'].mean()
print(f'unfiltered mean {mean}')

# Calculate Q1 (25th percentile) and Q3 (75th percentile)
Q1 = df_final['efficiency'].quantile(0.25)
Q3 = df_final['efficiency'].quantile(0.75)
IQR = Q3 - Q1

# Define bounds for outliers
lower_bound = Q1 - 3 * IQR
upper_bound = Q3 + 3 * IQR

# Filter out outliers
filtered_efficiency = df_final[(df_final['efficiency'] >= lower_bound) & (df_final['efficiency'] <= upper_bound)]

# Calculate mean efficiency without outliers
mean_efficiency = filtered_efficiency['efficiency'].mean()

print("Mean Efficiency without Outliers:", mean_efficiency)

#____________________________________________________________________________________________________________________________