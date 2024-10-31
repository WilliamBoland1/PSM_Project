import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the data
df = pd.read_csv('data.csv', sep=';')

# Convert timestamp column to datetime format with UTC timezone
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Filter data for specific engines
df_engine_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/engine_load']
df_engine_2 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine2/engine_load']
df_engine_3 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/engine_load']

# Define the adjustable start and stop interval for the entire trip
start_time_tot = df['timestamp'].min()
stop_time_tot = df['timestamp'].max()

# Filter data for the full trip interval
df_engine_1_interval = df_engine_1[(df_engine_1['timestamp'] >= start_time_tot) & (df_engine_1['timestamp'] <= stop_time_tot)]
df_engine_2_interval = df_engine_2[(df_engine_2['timestamp'] >= start_time_tot) & (df_engine_2['timestamp'] <= stop_time_tot)]
df_engine_3_interval = df_engine_3[(df_engine_3['timestamp'] >= start_time_tot) & (df_engine_3['timestamp'] <= stop_time_tot)]

# Calculate the maximum engine load for each engine during the interval
max_engine_1_load = df_engine_1_interval['value'].max()
max_engine_2_load = df_engine_2_interval['value'].max()
max_engine_3_load = df_engine_3_interval['value'].max()

# Print the maximum engine loads
print(f"Maximum Engine 1 Load: {max_engine_1_load:.2f} kW")
print(f"Maximum Engine 2 Load: {max_engine_2_load:.2f} kW")
print(f"Maximum Engine 3 Load: {max_engine_3_load:.2f} kW")

# Plot the interval with engine loads for Engines 1, 2, and 3
plt.figure(figsize=(12, 6))
plt.plot(df_engine_1_interval['timestamp'], df_engine_1_interval['value'], label='Engine 1 Load', color='blue')
plt.plot(df_engine_2_interval['timestamp'], df_engine_2_interval['value'], label='Engine 2 Load', color='orange')
plt.plot(df_engine_3_interval['timestamp'], df_engine_3_interval['value'], label='Engine 3 Load', color='green')

# Mark maximum load points on the plot
plt.axhline(max_engine_1_load, color='blue', linestyle='--', linewidth=1, label=f'Max Engine 1 Load: {max_engine_1_load:.2f} kW')
plt.axhline(max_engine_2_load, color='orange', linestyle='--', linewidth=1, label=f'Max Engine 2 Load: {max_engine_2_load:.2f} kW')
plt.axhline(max_engine_3_load, color='green', linestyle='--', linewidth=1, label=f'Max Engine 3 Load: {max_engine_3_load:.2f} kW')

# Add labels and title
plt.xlabel('Time')
plt.ylabel('Engine Load [kW]')
plt.title(f'Engine Load from {start_time_tot.time()} to {stop_time_tot.time()}')
plt.legend(loc='upper right')
plt.grid(True)

# Format the x-axis for readability
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

# Adjust layout and display the plot
plt.tight_layout()
plt.show()
