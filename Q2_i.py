import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#Load the data
df = pd.read_csv('data.csv', sep=';')

#Convert timestamp column to datetime format with UTC timezone
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

#Filter data for specific engines
df_engine_1 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine1/engine_load']
df_engine_2 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine2/engine_load']
df_engine_3 = df[df['var'] == 'gunnerus/RVG_mqtt/Engine3/engine_load']

#Define the adjustable start and stop interval for plotting
start_time = pd.to_datetime('2024-09-10 06:30:26').tz_localize('UTC')
stop_time = pd.to_datetime('2024-09-10 06:45:30').tz_localize('UTC')

#Get the start and stop timestamps for the full trip
start_time_tot = df['timestamp'].min()
stop_time_tot = df['timestamp'].max()

#Filter data for the chosen interval (adjust here: start_time/start_time_tot, stop_time/stop_time_tot)
df_engine_1_interval = df_engine_1[(df_engine_1['timestamp'] >= start_time_tot) & (df_engine_1['timestamp'] <= stop_time_tot)]
#df_engine_2_interval = df_engine_2[(df_engine_2['timestamp'] >= start_time) & (df_engine_2['timestamp'] <= stop_time)]
df_engine_3_interval = df_engine_3[(df_engine_3['timestamp'] >= start_time_tot) & (df_engine_3['timestamp'] <= stop_time_tot)]

#Plot the interval with engine loads for Engines 1, 2, and 3
plt.figure(figsize=(12, 6))
plt.plot(df_engine_1_interval['timestamp'], df_engine_1_interval['value'], label='Engine 1 Load', color='blue')
#plt.plot(df_engine_2_interval['timestamp'], df_engine_2_interval['value'], label='Engine 2 Load', color='orange')
plt.plot(df_engine_3_interval['timestamp'], df_engine_3_interval['value'], label='Engine 3 Load', color='green')

#Add labels and title
plt.xlabel('Time')
plt.ylabel('Engine Load [kW]')
plt.title(f'Engine Load from {start_time_tot.time()} to {stop_time_tot.time()}')
plt.legend(loc='upper right')
plt.grid(True)

#Format the x-axis for readability
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

#Adjust layout and display the plot
plt.tight_layout()
plt.show()
