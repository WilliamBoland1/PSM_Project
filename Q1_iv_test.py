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

# Calculate cumulative fuel consumption in liters and kg over time
merged_data['cumulative_fuel_L'] = merged_data['fuel_consumed_step_L'].cumsum()
merged_data['cumulative_fuel_kg'] = merged_data['fuel_consumed_step_kg'].cumsum()

# Define the time intervals for Route 1 and Route 2
route1_start = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
route1_stop = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
route2_start = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
route2_stop = pd.to_datetime('2024-09-10 07:07:00').tz_localize('UTC')

# Filter data for each route
df_route1 = merged_data[(merged_data.index >= route1_start) & (merged_data.index <= route1_stop)]
df_route2 = merged_data[(merged_data.index >= route2_start) & (merged_data.index <= route2_stop)]

# Original plot for the entire interval
plt.figure(figsize=(12, 6))
plt.plot(merged_data.index, merged_data['cumulative_fuel_L'], label="Cumulative Fuel Consumption (L)", color="orange")
plt.plot(merged_data.index, merged_data['cumulative_fuel_kg'], label="Cumulative Fuel Consumption (Kg)", color="blue")
plt.xlabel("Time")
plt.ylabel("Cumulative Fuel Consumption")
plt.title("Total Cumulative Fuel Consumption Over Time (L and Kg)")
plt.legend()
plt.grid(True)
plt.show()

# Plot for Route 1
plt.figure(figsize=(12, 6))
plt.plot(df_route1.index, df_route1['cumulative_fuel_L'], label="Cumulative Fuel Consumption (L) - Route 1", color="orange")
plt.plot(df_route1.index, df_route1['cumulative_fuel_kg'], label="Cumulative Fuel Consumption (Kg) - Route 1", color="blue")
plt.xlabel("Time")
plt.ylabel("Cumulative Fuel Consumption")
plt.title("Cumulative Fuel Consumption Over Time - Route 1 (L and Kg)")
plt.legend()
plt.grid(True)
plt.show()

# Plot for Route 2
plt.figure(figsize=(12, 6))
plt.plot(df_route2.index, df_route2['cumulative_fuel_L'], label="Cumulative Fuel Consumption (L) - Route 2", color="orange")
plt.plot(df_route2.index, df_route2['cumulative_fuel_kg'], label="Cumulative Fuel Consumption (Kg) - Route 2", color="blue")
plt.xlabel("Time")
plt.ylabel("Cumulative Fuel Consumption")
plt.title("Cumulative Fuel Consumption Over Time - Route 2 (L and Kg)")
plt.legend()
plt.grid(True)
plt.show()
