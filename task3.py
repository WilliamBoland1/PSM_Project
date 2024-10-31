import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = pd.read_csv('data.csv', sep=';')

# Convert timestamp column to datetime format with UTC timezone
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Filter data for fuel consumption specific engines and motor load feedback
df_fuel_consumption_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/fuel_consumption'][['timestamp', 'value']].rename(columns={'value': 'fuel_consumption_1'})
df_fuel_consumption_3 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/fuel_consumption'][['timestamp', 'value']].rename(columns={'value': 'fuel_consumption_3'})
df_Port = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_port_mp/LoadFeedback'][['timestamp', 'value']].rename(columns={'value': 'load_port'})
df_Stbd = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_stbd_mp/LoadFeedback'][['timestamp', 'value']].rename(columns={'value': 'load_stbd'})

#ROUTES CODE
#_____________________________________________
# Define the adjustable start and stop interval for plotting
#route 1
start_time = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
stop_time = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')

#Route 2
# start_time = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
# stop_time = pd.to_datetime('2024-09-10 07:7:00').tz_localize('UTC')

#Both routes
start_time = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
stop_time = pd.to_datetime('2024-09-10 07:6:00').tz_localize('UTC')

#Max time
# start_time = df_fuel_consumption_1['timestamp'].min()
# stop_time = df_fuel_consumption_1['timestamp'].max()

#Filter data for the chosen interval (adjust here: start_time/start_time_tot, stop_time/stop_time_tot)
df_fuel_consumption_1 = df_fuel_consumption_1[(df_fuel_consumption_1['timestamp'] >= start_time) & (df_fuel_consumption_1['timestamp'] <= stop_time)]
df_fuel_consumption_3 = df_fuel_consumption_3[(df_fuel_consumption_3['timestamp'] >= start_time) & (df_fuel_consumption_3['timestamp'] <= stop_time)]
df_Port = df_Port[(df_Port['timestamp'] >= start_time) & (df_Port['timestamp'] <= stop_time)]
df_Stbd = df_Stbd[(df_Stbd['timestamp'] >= start_time) & (df_Stbd['timestamp'] <= stop_time)]

#_____________________________________________

# Merge fuel consumption and motor data by timestamp
df_merged = pd.merge(df_fuel_consumption_1, df_fuel_consumption_3, on='timestamp', how='inner')
df_merged = pd.merge(df_merged, df_Port, on='timestamp', how='inner')
df_merged = pd.merge(df_merged, df_Stbd, on='timestamp', how='inner')

# Calculate propulsion power in kW based on load percentages
BASE_POWER = 500  # kW
df_merged['Port_motor_power'] = df_merged['load_port'] / 100 * BASE_POWER
df_merged['Starboard_motor_power'] = df_merged['load_stbd'] / 100 * BASE_POWER
df_merged['total_propulsion_power'] = df_merged['Port_motor_power'] + df_merged['Starboard_motor_power'] #now in [kw]

# Convert fuel consumption from [l/h] to [kg/h] using density
density_kg_per_L = 0.820  # kg/L
df_merged['fuel_consumption_1_g_per_h'] = df_merged['fuel_consumption_1'] * density_kg_per_L
df_merged['fuel_consumption_3_g_per_h'] = df_merged['fuel_consumption_3'] * density_kg_per_L
df_merged['total_fuel_consumption'] = df_merged['fuel_consumption_1_g_per_h'] + df_merged['fuel_consumption_3_g_per_h'] #now in [kg/hour]

# Define threshold for near-zero values
threshold = 15  # Adjust as necessary for precision, This is prpolsuion power in [kW]

# Calculate Specific Fuel Consumption (SFC) and handle near-zero propulsion power cases sfc[kg/MJ] = Qf[kg/h]/(Pdg[kW]*3.6)
#Where the total propulsion power is under "treshold" [kW] total, the values are set to zero as the values goes towards infinity in these points where the engines aren't delivering power
df_merged['sfc'] = np.where(
    (df_merged['total_propulsion_power'] < threshold),
    None,
    (df_merged['total_fuel_consumption']) / (df_merged['total_propulsion_power']*3.6)
)

# Plotting SFC over real timestamps
plt.figure(figsize=(12, 6))
plt.plot(df_merged['timestamp'], df_merged['sfc'], label='Specific Fuel Consumption (SFC)')
plt.xlabel('Time')
plt.ylabel('Specific Fuel Consumption (kg/MJ)')
plt.title('Specific Fuel Consumption Over Time')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)  # Rotate timestamps for better readability
plt.tight_layout()
plt.show()
