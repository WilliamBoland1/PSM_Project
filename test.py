import pandas as pd

# Load the data
df = pd.read_csv('data.csv', sep=';')

# Display column names
print(df.columns)
