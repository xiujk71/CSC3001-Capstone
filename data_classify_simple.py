import pandas as pd

# Load data for classify
print("reading csv file")
csv = pd.read_csv('data_formatted.csv', index_col=0)

# Get largest future hits
max_hits = csv['future_hits'].max()

# Set 0 Future-Hits 1 higher then max hit
csv.loc[csv['future_hits'] == 0, 'future_hits'] = max_hits + 1

# Get Q1 & Q3
Q1 = int(csv['future_hits'].quantile(0.25))
Q3 = int(csv['future_hits'].quantile(0.75))
IQR = Q3-Q1
center = Q1+(IQR/2)
print ("Q1:", Q1)
print ("Q3:", Q3)
print ("center:", center)

csv.loc[csv['future_hits'] < Q1, 'future_hits'] = 0
csv.loc[csv['future_hits'] >= Q1, 'future_hits'] = 1


print(csv)
csv.to_csv('data_formatted_classified_simple.csv')