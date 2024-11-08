import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import zscore

# Load the data
df = pd.read_csv('data.csv', sep=';')

# Convert timestamp column to datetime format with UTC timezone
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Filter data for fuel consumption specific engines and motor load feedback
df_fuel_consumption_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/fuel_consumption'][['timestamp', 'value']].rename(columns={'value': 'fuel_consumption_1'})
df_fuel_consumption_3 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/fuel_consumption'][['timestamp', 'value']].rename(columns={'value': 'fuel_consumption_3'})
df_engine_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/engine_load'][['timestamp', 'value']].rename(columns={'value': 'engine_1'})
df_engine_2 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/engine_load'][['timestamp', 'value']].rename(columns={'value': 'engine_2'})
df_rpm_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/engine_speed'][['timestamp', 'value']].rename(columns={'value': 'rpm_1'})

# Merge fuel consumption and motor data by timestamp
df_merged = pd.merge(df_fuel_consumption_1, df_fuel_consumption_3, on='timestamp', how='inner')
df_merged = pd.merge(df_merged, df_rpm_1, on='timestamp', how='inner')
df_merged = pd.merge(df_merged, df_engine_1, on='timestamp', how='inner')
df_merged = pd.merge(df_merged, df_engine_2, on='timestamp', how='inner')
print(df_merged)

# Convert fuel consumption from [l/h] to [kg/h] using density
density_kg_per_L = 0.820  # kg/L
df_merged['fuel_consumption_1_kg_per_h'] = df_merged['fuel_consumption_1'] * density_kg_per_L
df_merged['fuel_consumption_3_kg_per_h'] = df_merged['fuel_consumption_3'] * density_kg_per_L

print(df_merged)

# Define threshold for near-zero values
threshold = 10  # Adjust as necessary for precision, This is prpolsuion power in [kW]

# Calculate Specific Fuel Consumption (SFC) and handle near-zero propulsion power cases sfc[kg/MJ] = Qf[kg/h]/(Pdg[kW]*3.6)
#Where the total propulsion power is under "treshold" [kW] total, the values are set to zero as the values goes towards infinity in these points where the engines aren't delivering power
specific_energy = 45.4 #[Mj/kg]

df_merged['eta_1'] = np.where(
    (df_merged['engine_1'] < threshold),
    None,
    (100*((3.6*df_merged['engine_1']) / (df_merged['fuel_consumption_1_kg_per_h']*specific_energy)))
)

# Smooth the thermal efficiency using a rolling mean with a window of 10
df_merged['eta_1_smoothed'] = df_merged['eta_1'].rolling(window=5, min_periods=1).mean()

# Remove outliers based on z-score filtering
df_merged['eta_1_zscore'] = zscore(df_merged['eta_1_smoothed'].fillna(0))
df_merged['eta_1_filtered'] = np.where(df_merged['eta_1_zscore'].abs() > 3, None, df_merged['eta_1_smoothed'])


#Eta values after filtering for outliers
print(f'Minimum filtered value for thermal efficiency of engine 1 is {df_merged["eta_1_filtered"].min()}')
print(f'Maximum filtered value for thermal efficiency of engine 1 is {df_merged["eta_1_filtered"].max()}')

eta_max = df_merged["eta_1_filtered"].max()
eta_min = df_merged["eta_1_filtered"].min()

df_merged['eta_2'] = np.where(
    (df_merged['engine_2'] < 0),
    None,
    (100*((3.6*df_merged['engine_2']) / (df_merged['fuel_consumption_3_kg_per_h']*specific_energy)))
)

# Plotting SFC over real timestamps
plt.figure(figsize=(12, 6))
plt.plot(df_merged['timestamp'], df_merged['eta_1'], label='Eta[th] engine 1',color ='red')
plt.plot(df_merged['timestamp'], df_merged['eta_2'], label='Eta[th] engine 2', color = 'green')
plt.plot(df_merged['timestamp'], df_merged['eta_1_filtered'], label='Smoothed & Filtered Eta[th] engine 1', color='blue')
plt.xlabel('Time')
plt.ylabel('Eta efficiency')
plt.title('Thermal Efficiency Over Time')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)  # Rotate timestamps for better readability
plt.tight_layout()
plt.show()

##############################################################################################################
##############################################################################################################
##############################################################################################################

#Calculating Torque
# Find the index positions for max and min values of eta_1_filtered
max_index = df_merged["eta_1_filtered"].idxmax()
min_index = df_merged["eta_1_filtered"].idxmin()

#Trying out for eta
max_index = df_merged["eta_1"].idxmax()
min_index = df_merged["eta_1"].idxmin()

# Retrieve the timestamps using these indices
timestamp_max = df_merged.loc[max_index, "timestamp"]
timestamp_min = df_merged.loc[min_index, "timestamp"]

#Find the corresponding RPM and engine load values
rpm_1_at_max = df_merged.loc[df_merged['timestamp'] == timestamp_max, 'rpm_1'].values[0]
engine_load_at_max = df_merged.loc[df_merged['timestamp']== timestamp_max, 'engine_1'].values[0]

rpm_1_at_min = df_merged.loc[df_merged['timestamp'] == timestamp_min, 'rpm_1'].values[0]
engine_load_at_min = df_merged.loc[df_merged['timestamp']== timestamp_min, 'engine_1'].values[0]

#Torquing time

#T = P/omega = P[W]/[rad/s] 
torque_at_max_eff = (engine_load_at_max*60)/(2*np.pi*rpm_1_at_max) * 1000 #Multiplied by 10^3 to make up for [kW] to [W] conversion
torque_at_min_eff = (engine_load_at_min*60)/(2*np.pi*rpm_1_at_min) * 1000

#In the formula power is given as watts, so it has to be multiplied by 1000
print("TORQUE AT MAX", torque_at_max_eff)
print("TORQUE AT MIN", torque_at_min_eff)

# Calculate torque for all timestamps using the formula: torque = (engine_load * 60) / (2 * π * rpm)
df_merged['torque'] = (df_merged['engine_1'] * 60) / (2 * np.pi * df_merged['rpm_1'])

# Convert torque to Nm (multiplied by 1000 to get torque in Nm if engine_load is in kW and rpm in RPM)
df_merged['torque'] = df_merged['torque'] * 1000

plt.figure(figsize=(12, 6))
plt.plot(df_merged['timestamp'], df_merged['torque'], label='Torque (Nm)', color='purple')
plt.xlabel('Time')
plt.ylabel('Torque (Nm)')
plt.title('Torque Over Time for Engine 1')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)  # Rotate timestamps for better readability
plt.tight_layout()
plt.show()

#BMEP
#####################################################################################################
displaced_volume = 0.0156 #[m^3] From data engine

#Other constants
k = 2 #For 4 stroke engines
i = 8 #number of engines
pascal_to_bar_conversion = 1e-5

#eq from presentation 0.2 machine lecture, k = n_r in equation from lecture
BMEP_max = ((2*np.pi*k*torque_at_max_eff)/displaced_volume) *pascal_to_bar_conversion
BMEP_min = ((2*np.pi*k*torque_at_min_eff)/displaced_volume) *pascal_to_bar_conversion

print(f'BMEP for max eff; {BMEP_max}')
print(f'BMEP for min eff; {BMEP_min}')
#####################################################################################################