#Calculate fuel consumption as a function of time: plot 𝑀_𝑓[Kg] vs. time.
import pandas as pd
import matplotlib.pyplot as plt

#Load data from the CSV file
data = pd.read_csv("data.csv", sep=';')

#Convert timestamp to a datetime format and sort by time for consistency
data['timestamp'] = pd.to_datetime(data['timestamp'])
data.sort_values(by='timestamp', inplace=True)

#Filter relevant rows: engine load and fuel consumption for each engine
#We assume engine_load and fuel_consumption values are labeled consistently in the 'var' column
engine_load_data = data[data['var'].str.contains("engine_load")]
fuel_data = data[data['var'].str.contains("fuel_consumption")]

#Pivot data so each engine's load and fuel consumption are in separate columns
engine_load_data = engine_load_data.pivot(index='timestamp', columns='var', values='value')
fuel_data = fuel_data.pivot(index='timestamp', columns='var', values='value')

#Merge engine load and fuel data into a single DataFrame
merged_data = engine_load_data.join(fuel_data, how='outer').sort_index().fillna(method='ffill')

#Ensure column names match for accessing specific engines (modify if necessary)
#Example column names after pivot might be 'gunnerus/RVG_mqtt/Engine1/fuel_consumption' for fuel data

#Calculate total fuel consumption at each time step by summing fuel consumption across engines
#For instance, for two engines, sum columns like 'Engine1/fuel_consumption' and 'Engine3/fuel_consumption'
merged_data['total_fuel_consumption'] = merged_data.filter(like='fuel_consumption').sum(axis=1)

#Calculate cumulative fuel consumption

#Delta t
time_diff_hours = merged_data.index.to_series().diff().dt.total_seconds().fillna(0) / 3600

#Q_f*delta_t gives the fuel condumed at given time intervall
merged_data['fuel_consumed_step'] = merged_data['total_fuel_consumption'] * time_diff_hours

#Calculates the cumulative fuel consumption over time 
merged_data['cumulative_fuel'] = merged_data['fuel_consumed_step'].cumsum()

#Plot cumulative fuel consumption over time
plt.figure(figsize=(10, 6))
plt.plot(merged_data.index, merged_data['cumulative_fuel'], label="Cumulative Fuel Consumption (L)")
plt.xlabel("Time")
plt.ylabel("Cumulative Fuel Consumption (L)")
plt.title("Total cumulative fuel consumption over time")
plt.legend()
plt.grid(True)
plt.show()
