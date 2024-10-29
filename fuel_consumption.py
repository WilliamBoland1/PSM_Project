import pandas as pd
import matplotlib.pyplot as plt

# Density assumed
density = 0.85

# Load the data
df = pd.read_csv('data.csv', sep=';')

# Convert timestamp column to datetime format with UTC timezone
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# Filter data for specific engines
df_engine_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/fuel_consumption']
df_engine_3 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/fuel_consumption']

#ROUTES CODE
#_____________________________________________
# Define the adjustable start and stop interval for plotting
#route 1
start_time = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
stop_time = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')

#Route 2
# start_time = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')
# stop_time = pd.to_datetime('2024-09-10 07:7:00').tz_localize('UTC')

#Max time
# start_time = df_engine_1['timestamp'].min()
# stop_time = df_engine_1['timestamp'].max()

#Filter data for the chosen interval (adjust here: start_time/start_time_tot, stop_time/stop_time_tot)
df_engine_1_interval = df_engine_1[(df_engine_1['timestamp'] >= start_time) & (df_engine_1['timestamp'] <= stop_time)]
df_engine_3_interval = df_engine_3[(df_engine_3['timestamp'] >= start_time) & (df_engine_3['timestamp'] <= stop_time)]
#_____________________________________________

# Convert fuel consumption from liters per hour to kg per hour
df_engine_1_interval['fuel_kg_per_hour'] = df_engine_1_interval['value'] * density
df_engine_3_interval['fuel_kg_per_hour'] = df_engine_3_interval['value'] * density

# Align timestamps for Engine 1 and Engine 3 intervals by merging on 'timestamp'
combined_fuel_flow_df = pd.merge(
    df_engine_1_interval[['timestamp', 'fuel_kg_per_hour']].rename(columns={'fuel_kg_per_hour': 'fuel_kg_1'}),
    df_engine_3_interval[['timestamp', 'fuel_kg_per_hour']].rename(columns={'fuel_kg_per_hour': 'fuel_kg_3'}),
    on='timestamp',
    how='outer'
).fillna(0)  # Fill missing values with 0 if one engine is not running at certain times

# Calculate the combined fuel flow rate by summing the two engines' rates
combined_fuel_flow_df['combined_fuel_flow_rate'] = combined_fuel_flow_df['fuel_kg_1'] + combined_fuel_flow_df['fuel_kg_3']

# Calculate the fuel consumed each second by dividing the flow rate by 3600 (since it's in kg per hour)
combined_fuel_flow_df['fuel_consumed_per_second'] = combined_fuel_flow_df['combined_fuel_flow_rate'] / 3600

# Calculate the cumulative sum of the fuel consumed per second
combined_fuel_flow_df['cumulative_fuel_consumed'] = combined_fuel_flow_df['fuel_consumed_per_second'].cumsum()

# Total fuel consumed
total_fuel_consumed = combined_fuel_flow_df['cumulative_fuel_consumed'].iloc[-1]
print(f'Total fuel consumed in kg: {total_fuel_consumed}')

# Plot the cumulative fuel consumed over time
plt.figure(figsize=(12, 6))
plt.plot(combined_fuel_flow_df['timestamp'], combined_fuel_flow_df['cumulative_fuel_consumed'], label='Cumulative Fuel Consumed', color='red')

# Add labels and legend for the cumulative fuel consumption plot
plt.title('Cumulative Fuel Consumed Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Cumulative Fuel Consumed (kg)')
plt.legend()
plt.grid(True)

# Display the plot
plt.show()
