#2. You have determined the total mass of fuel used for the entire voyage- (from task 02) - determine the total amount of carbon
#   dioxide emitted for the voyage, explaining which assumptions you have made.

#Link to emission factor: https://safety4sea.com/wp-content/uploads/2020/11/Marine-Benchmark-Maritime-CO2-Emissions-2020_11.pdf
#Also given in mandatory lecture, around 3,2 kg/l

import pandas as pd
import matplotlib.pyplot as plt

# Load data from the CSV file
data = pd.read_csv("data.csv", sep=';')

# Convert timestamp to a datetime format and sort by time for consistency
data['timestamp'] = pd.to_datetime(data['timestamp'])
data.sort_values(by='timestamp', inplace=True)

# Filter relevant rows: engine load and fuel consumption for each engine
engine_load_data = data[data['var'].str.contains("engine_load")]
fuel_data = data[data['var'].str.contains("fuel_consumption")]

# Pivot data so each engine's load and fuel consumption are in separate columns
engine_load_data = engine_load_data.pivot(index='timestamp', columns='var', values='value')
fuel_data = fuel_data.pivot(index='timestamp', columns='var', values='value')

# Merge engine load and fuel data into a single DataFrame
merged_data = engine_load_data.join(fuel_data, how='outer').sort_index().fillna(method='ffill')

# Calculate total fuel consumption at each time step by summing fuel consumption across engines
merged_data['total_fuel_consumption'] = merged_data.filter(like='fuel_consumption').sum(axis=1)

# Calculate time difference in hours between each reading
time_diff_hours = merged_data.index.to_series().diff().dt.total_seconds().fillna(0) / 3600

# Calculate fuel consumed at each step in liters and kilograms
merged_data['fuel_consumed_step_L'] = merged_data['total_fuel_consumption'] * time_diff_hours
merged_data['fuel_consumed_step_kg'] = merged_data['fuel_consumed_step_L'] * 0.82  # Convert to kg

# Calculate cumulative fuel consumption in kg over time
merged_data['cumulative_fuel_kg'] = merged_data['fuel_consumed_step_kg'].cumsum()

# Define emission factor for CO2 (kg CO2 per kg of fuel)
emission_factor = 3.15  # kg CO2/kg fuel

# Calculate CO2 emitted at each step and cumulative CO2 emissions
merged_data['CO2_emitted_step'] = merged_data['fuel_consumed_step_kg'] * emission_factor
merged_data['cumulative_CO2'] = merged_data['CO2_emitted_step'].cumsum()

# Define the time intervals for Route 1 and Route 2
route1_start = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
route1_stop = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
route2_start = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
route2_stop = pd.to_datetime('2024-09-10 07:07:00').tz_localize('UTC')

# Filter data for each route
df_route1 = merged_data[(merged_data.index >= route1_start) & (merged_data.index <= route1_stop)].copy()
df_route2 = merged_data[(merged_data.index >= route2_start) & (merged_data.index <= route2_stop)].copy()

# Reset cumulative CO2 emissions for Route 1 and Route 2 to start from 0
df_route1['cumulative_CO2'] -= df_route1['cumulative_CO2'].iloc[0]
df_route2['cumulative_CO2'] -= df_route2['cumulative_CO2'].iloc[0]

# Plot total CO2 emissions over the entire interval
plt.figure(figsize=(12, 6))
plt.plot(merged_data.index, merged_data['cumulative_CO2'], label="Cumulative CO2 Emissions (kg)", color="green")
plt.xlabel("Time")
plt.ylabel("Cumulative CO2 Emissions (kg)")
plt.title("Total Cumulative CO2 Emissions Over Time")
plt.legend()
plt.grid(True)
plt.show()

# Plot CO2 emissions for Route 1
plt.figure(figsize=(12, 6))
plt.plot(df_route1.index, df_route1['cumulative_CO2'], label="Cumulative CO2 Emissions (kg) - Route 1", color="green")
plt.xlabel("Time")
plt.ylabel("Cumulative CO2 Emissions (kg)")
plt.title("Cumulative CO2 Emissions Over Time - Route 1")
plt.legend()
plt.grid(True)
plt.show()

# Plot CO2 emissions for Route 2
plt.figure(figsize=(12, 6))
plt.plot(df_route2.index, df_route2['cumulative_CO2'], label="Cumulative CO2 Emissions (kg) - Route 2", color="green")
plt.xlabel("Time")
plt.ylabel("Cumulative CO2 Emissions (kg)")
plt.title("Cumulative CO2 Emissions Over Time - Route 2")
plt.legend()
plt.grid(True)
plt.show()

# Print total CO2 emissions for each interval
print(f"Total CO2 emissions for the entire interval: {merged_data['cumulative_CO2'].iloc[-1]:.2f} kg")
print(f"Total CO2 emissions for Route 1: {df_route1['cumulative_CO2'].iloc[-1]:.2f} kg")
print(f"Total CO2 emissions for Route 2: {df_route2['cumulative_CO2'].iloc[-1]:.2f} kg")
