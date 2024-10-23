import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#Reads csv file seperated by ";" 
df = pd.read_csv('data.csv', sep = ';')

df['timestamp'] = pd.to_datetime(df['timestamp'])

# df = df[(df['timestamp'] >= '2024-09-10T07:08:15.256130129Z') & (df['timestamp'] <= '2024-09-10T07:10:15.356181072Z')]

#Creates new dataframe for all rows with variable "gunnerus/RVG_mqtt/Engine1/engine_load"
df_engine_1 = df[df['var']== 'gunnerus/RVG_mqtt/Engine1/engine_load']
df_engine_2 = df[df['var']== 'gunnerus/RVG_mqtt/Engine2/engine_load']
df_engine_3 = df[df['var']== 'gunnerus/RVG_mqtt/Engine3/engine_load']

#create time array of the size of engine load
# time = df_engine_3['timestamp'].to_d

# Plot the engine load against the time (index)
# plt.plot(time, engine_1_load_array)
plt.plot(df_engine_1['timestamp'], df_engine_1['value'])
plt.plot(df_engine_3['timestamp'], df_engine_3['value'])
plt.xlabel('Time (Index)')
plt.ylabel('Engine Load')
plt.title('Engine 1 Load Over Time')
plt.show()