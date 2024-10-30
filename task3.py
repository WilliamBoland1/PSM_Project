import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = pd.read_csv('data.csv', sep=';')

# Convert timestamp column to datetime format with UTC timezone
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Filter data for fuel consumption specific engines and motor load feedback
#############################################################################
df_fuel_consumption_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/fuel_consumption'][['timestamp', 'value']].rename(columns={'value': 'fuel_consumption_1'})
df_fuel_consumption_3 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/fuel_consumption'][['timestamp', 'value']].rename(columns={'value': 'fuel_consumption_3'})

df_Port = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_port_mp/LoadFeedback'][['timestamp', 'value']].rename(columns={'value': 'load_port'})
df_Stbd = df[df['var'] == 'gunnerus/RVG_mqtt/hcx_stbd_mp/LoadFeedback'][['timestamp', 'value']].rename(columns={'value': 'load_stbd'})

############################################################################

# Merge fuel consumption and motor data by timestamp
############################################################################
df_merged = pd.merge(df_fuel_consumption_1, df_fuel_consumption_3, on='timestamp', how='inner')
df_merged = pd.merge(df_merged, df_Port, on='timestamp', how='inner')
df_merged = pd.merge(df_merged, df_Stbd, on='timestamp', how='inner')
############################################################################

# Find the propulsion power in kW instead of %
############################################################################
BASE_POWER = 500 # kW

df_merged['Port_motor_power'] = df_merged['load_port'] / 100 * BASE_POWER
df_merged['Starboard_motor_power'] = df_merged['load_stbd'] / 100 * BASE_POWER
df_merged['total_propulsion_power'] = df_merged['Port_motor_power'] + df_merged['Starboard_motor_power']
############################################################################

# Convert fuel consumption from [l/h] to [g/s]
############################################################################
density_g_per_L = 820  # g/L

df_merged['fuel_consumption_1_g_per_s'] = df_merged['fuel_consumption_1'] * density_g_per_L / 3600
df_merged['fuel_consumption_3_g_per_s'] = df_merged['fuel_consumption_3'] * density_g_per_L / 3600
df_merged['total_fuel_consumption'] = df_merged['fuel_consumption_1_g_per_s'] + df_merged['fuel_consumption_3_g_per_s']
############################################################################

# Calculate Specific Fuel Consumption (SFC) and handle near-zero propulsion power cases
############################################################################
df_merged['sfc'] = df_merged['total_fuel_consumption'] / df_merged['total_propulsion_power']
df_merged['sfc'] = df_merged['sfc'].where(df_merged['total_propulsion_power'] > 1e-6, 0)
df_merged['sfc'] = df_merged['sfc'].where(df_merged['total_fuel_consumption'] > 1e-6, 0)  # Set SFC to 0 where propulsion power is close to zero
############################################################################

# Plotting the results
array_time = np.arange(len(df_merged['sfc']))  # Time array based on length of `sfc`

plt.figure(figsize=(10, 6))
plt.plot(array_time, df_merged['sfc'], label='Specific Fuel Consumption')
# plt.plot(array_time, df_merged['total_fuel_consumption'], label='Total Fuel Consumption')
plt.xlabel('Time (arbitrary units)')
plt.ylabel('Specific Fuel Consumption (mg/J)')
plt.title('Specific Fuel Consumption over Time')
plt.legend()
plt.grid(True)
plt.show()
