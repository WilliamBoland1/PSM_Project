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
df_Port = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/engine_load'][['timestamp', 'value']].rename(columns={'value': 'engine_1'})
df_Stbd = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/engine_load'][['timestamp', 'value']].rename(columns={'value': 'engine_2'})

# Merge fuel consumption and motor data by timestamp
df_merged = pd.merge(df_fuel_consumption_1, df_fuel_consumption_3, on='timestamp', how='inner')
df_merged = pd.merge(df_merged, df_Port, on='timestamp', how='inner')
df_merged = pd.merge(df_merged, df_Stbd, on='timestamp', how='inner')

# Calculate propulsion power in kW based on load percentages
df_merged['Engine_1_power'] = df_merged['engine_1']
df_merged['Engine_2_power'] = df_merged['engine_2']

# Convert fuel consumption from [l/h] to [kg/h] using density
density_kg_per_L = 0.820  # kg/L
df_merged['fuel_consumption_1_kg_per_h'] = df_merged['fuel_consumption_1'] * density_kg_per_L
df_merged['fuel_consumption_3_kg_per_h'] = df_merged['fuel_consumption_3'] * density_kg_per_L

# Define threshold for near-zero values
threshold = 10  # Adjust as necessary for precision, This is prpolsuion power in [kW]

# Calculate Specific Fuel Consumption (SFC) and handle near-zero propulsion power cases sfc[kg/MJ] = Qf[kg/h]/(Pdg[kW]*3.6)
#Where the total propulsion power is under "treshold" [kW] total, the values are set to zero as the values goes towards infinity in these points where the engines aren't delivering power
df_merged['sfc_1'] = np.where(
    (df_merged['Engine_1_power'] < threshold),
    None,
    (df_merged['fuel_consumption_1_kg_per_h']) / (df_merged['Engine_1_power']*3.6)
)

# df_merged['sfc_2'] = np.where(
#     (df_merged['Engine_2_power'] < threshold),
#     None,
#     (df_merged['fuel_consumption_3_kg_per_h']) / (df_merged['Engine_2_power']*3.6)
# )

# Plotting SFC over real timestamps
plt.figure(figsize=(12, 6))
plt.plot(df_merged['timestamp'], df_merged['sfc_1'], label='Specific Fuel Consumption (SFC)')
plt.xlabel('Time')
plt.ylabel('Specific Fuel Consumption (kg/MJ)')
plt.title('Specific Fuel Consumption Over Time')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)  # Rotate timestamps for better readability
plt.tight_layout()
plt.show()
