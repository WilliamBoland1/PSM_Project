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

# Plot cumulative fuel consumption over time in both liters and kg
plt.figure(figsize=(12, 6))
plt.plot(merged_data.index, merged_data['cumulative_fuel_L'], label="Cumulative Fuel Consumption (L)", color="orange")
plt.plot(merged_data.index, merged_data['cumulative_fuel_kg'], label="Cumulative Fuel Consumption (Kg)", color="blue")
plt.xlabel("Time")
plt.ylabel("Cumulative Fuel Consumption")
plt.title("Total Cumulative Fuel Consumption over Time (L and Kg)")
plt.legend()
plt.grid(True)
plt.show()

