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

# Merge engine 1 and engine 3 data on 'timestamp' and calculate total engine load
df_engine_loads = pd.merge(df_engine_1[['timestamp', 'value']], df_engine_3[['timestamp', 'value']], on='timestamp', how='outer', suffixes=('_engine1', '_engine3'))
df_engine_loads = df_engine_loads.fillna({'value_engine3': 0})
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

# Filter out anomalous efficiency values for analysis (e.g., greater than 100% or less than 0%)
anomalies = df_final[(df_final['efficiency'] > 100) | (df_final['efficiency'] < 0)]

# Print out the anomalous values
print("Anomalous Efficiency Values:")
print(anomalies[['timestamp', 'total_engine_load', 'total_propulsion_power', 'efficiency']])

# Optional: Save the anomalies to a CSV for detailed analysis
anomalies.to_csv('anomalous_efficiency_values.csv', index=False)

# Plot the efficiency over time (after filtering out anomalies if needed)
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
