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

# Calculate time differences in hours between each reading
time_diff_hours = merged_data.index.to_series().diff().dt.total_seconds().fillna(0) / 3600

# Calculate cumulative fuel consumption for each engine
for col in merged_data.filter(like='fuel_consumption').columns:
    # Calculate the fuel consumed per step for each engine
    merged_data[f'{col}_fuel_consumed_step'] = merged_data[col] * time_diff_hours
    # Calculate cumulative fuel for each engine
    merged_data[f'{col}_cumulative_fuel'] = merged_data[f'{col}_fuel_consumed_step'].cumsum()

# Calculate total fuel consumption across all engines at each time step and cumulatively
merged_data['total_fuel_consumption'] = merged_data.filter(like='fuel_consumption').sum(axis=1)
merged_data['total_fuel_consumed_step'] = merged_data['total_fuel_consumption'] * time_diff_hours
merged_data['total_cumulative_fuel'] = merged_data['total_fuel_consumed_step'].cumsum()

# Plot cumulative fuel consumption for each engine and the total
plt.figure(figsize=(12, 8))

# Plot for each engine
for col in merged_data.filter(like='_cumulative_fuel').columns:
    if 'total' not in col:  # Exclude total from individual engine plots
        plt.plot(merged_data.index, merged_data[col], label=col.replace('_cumulative_fuel', ''))

# Plot total cumulative fuel consumption
plt.plot(merged_data.index, merged_data['total_cumulative_fuel'], label="Total Cumulative Fuel Consumption", linewidth=2, linestyle='--')

# Plot styling
plt.xlabel("Time")
plt.ylabel("Cumulative Fuel Consumption (L)")
plt.title("Cumulative Fuel Consumption for Each Engine and Total Over Time")
plt.legend()
plt.grid(True)
plt.show()
