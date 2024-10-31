import pandas as pd
import matplotlib.pyplot as plt

# Load data from the CSV file
data = pd.read_csv("data.csv", sep=';')

# Convert timestamp column to datetime format and sort by time for consistency
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

# Calculate total fuel consumed in kg and liters over the entire period
total_fuel_consumed_kg = merged_data['fuel_consumed_step_kg'].sum()
total_fuel_consumed_L = merged_data['fuel_consumed_step_L'].sum()

# Calculate total time in hours
total_time_hours = time_diff_hours.sum()

# Calculate average fuel consumption rate in kg per hour
average_fuel_consumption_kg_per_hour = total_fuel_consumed_kg / total_time_hours

# Calculate average fuel consumption rate in liters per hour
average_fuel_consumption_L_per_hour = total_fuel_consumed_L / total_time_hours

# Print the results
print(f"Total fuel consumed (kg): {total_fuel_consumed_kg:.2f} kg")
print(f"Total fuel consumed (L): {total_fuel_consumed_L:.2f} L")
print(f"Total time (hours): {total_time_hours:.2f} hours")
print(f"Average fuel consumption (kg/hour): {average_fuel_consumption_kg_per_hour:.2f} kg/hour")
print(f"Average fuel consumption (L/hour): {average_fuel_consumption_L_per_hour:.2f} L/hour")
