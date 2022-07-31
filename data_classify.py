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
print ("Q1:", Q1)
print ("Q3:", Q3)

# Get value for splitting classes
split_value = 7

class_split_value = int((Q3-Q1)/split_value)
class_split = []

for i in range(split_value):
    class_split.append(Q1 + (class_split_value * i))

class_split.append(Q3)

# Split the class
for i in range(len(class_split)):
    if i == 0:
        csv.loc[(csv['future_hits'] >= 0) & (csv['future_hits'] <= class_split[i]), 'future_hits'] = i
    else:
        csv.loc[(csv['future_hits'] >= class_split[i-1]) & (csv['future_hits'] <= class_split[i]), 'future_hits'] = i

csv.loc[(csv['future_hits'] >= Q3) & (csv['future_hits'] <= max_hits), 'future_hits'] = split_value + 1
csv.loc[csv['future_hits'] == max_hits + 1, 'future_hits'] = split_value + 2


print(csv)
csv.to_csv('data_formatted_classified.csv')