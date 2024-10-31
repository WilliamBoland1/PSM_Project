import pandas as pd
import matplotlib.pyplot as plt

# Load the data from CSV
data = pd.read_csv("data.csv", sep=';')

# Convert timestamp column to datetime format
data['timestamp'] = pd.to_datetime(data['timestamp'])
data.sort_values(by='timestamp', inplace=True)

# Filter data for fuel consumption and speed
fuel_data = data[data['var'].str.contains("fuel_consumption")]
speed_data = data[data['var'] == 'gunnerus/RVG_mqtt/SeapathGPSVtg/SpeedKnots']

# Pivot fuel data to get each engine's fuel consumption in separate columns
fuel_data = fuel_data.pivot(index='timestamp', columns='var', values='value')

# Merge speed data with fuel data on timestamp
speed_data = speed_data.set_index('timestamp')
merged_data = fuel_data.join(speed_data[['value']].rename(columns={'value': 'speed_knots'}), how='outer').sort_index().fillna(method='ffill')

# Calculate total fuel consumption in L/h by summing across engine columns
merged_data['total_fuel_consumption'] = merged_data.filter(like='fuel_consumption').sum(axis=1)

# Calculate time difference in hours between each reading
time_diff_hours = merged_data.index.to_series().diff().dt.total_seconds().fillna(0) / 3600

# Calculate fuel consumed at each step in liters
merged_data['fuel_consumed_step_L'] = merged_data['total_fuel_consumption'] * time_diff_hours

# Calculate cumulative fuel consumption in liters over time
merged_data['cumulative_fuel_L'] = merged_data['fuel_consumed_step_L'].cumsum()

# Calculate fuel consumption per nautical mile (L/nm)
# We calculate L/nm by dividing total fuel consumption rate by vessel speed (when speed > 0)
merged_data['fuel_consumption_L_per_nm'] = merged_data['total_fuel_consumption'] / merged_data['speed_knots']
merged_data['fuel_consumption_L_per_nm'] = merged_data['fuel_consumption_L_per_nm'].fillna(0)

# Calculate average fuel consumption in L/nm over the entire period, considering only valid speed readings
average_fuel_consumption_L_per_nm = merged_data.loc[merged_data['speed_knots'] > 0, 'fuel_consumption_L_per_nm'].mean()

# Print the average fuel consumption in L/nm
print(f"Average fuel consumption (L/nm): {average_fuel_consumption_L_per_nm:.2f} L/nm")

# Plot cumulative fuel consumption over time for visualization
plt.figure(figsize=(12, 6))
plt.plot(merged_data.index, merged_data['cumulative_fuel_L'], label='Cumulative Fuel Consumption (L)', color='blue')
plt.title('Cumulative Fuel Consumption Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Cumulative Fuel Consumption (L)')
plt.legend()
plt.grid(True)
plt.show()
