import pandas as pd

# prep and clean twitter cluster
column_names=["timestamp","anonymized_key","key_size","value_size","client_id","operation","TTL"]
twit_data = pd.read_csv('twitter-traces/cluster001', names=column_names)

twit_data = twit_data.drop(["timestamp","anonymized_key","key_size","value_size","TTL"], axis=1)
twit_data.loc[twit_data["operation"] == "get", "operation"] = 0
twit_data.loc[twit_data["operation"] == "add", "operation"] = 1
twit_data.loc[twit_data["operation"] == "cas", "operation"] = 1
twit_data.loc[twit_data["operation"] == "gets", "operation"] = 1

twit_data.rename(columns = {'client_id':'id'}, inplace = True)
twit_data.rename(columns = {'operation':'key_search'}, inplace = True)

max_id = twit_data["id"].max()

print(twit_data.head())
print("max id: ", max_id)

# initalize hit tracker
tracker = []

for i in range(max_id+5):
    tracker.append([0,0])

# initialize variable to store future_hits
future_hits = []

for i in range(1000000):
    future_hits.append(0)

for index, row in twit_data.iterrows():
    print("index:", index)

    # get current position
    current_sn = index
    id = row.values[0]
    key_search = row.values[1]

    #print("id:", id)
    #print("key_search:", key_search)

    # get old position
    old_hit_sn = tracker[id][key_search]
    #print("old_hit_sn", old_hit_sn)
    
    # if its not first hit, update history_data on future hits
    if old_hit_sn != 0:
        future_hits[old_hit_sn] = current_sn - old_hit_sn

    # update tracker on last position to be hit
    tracker[id][key_search] = current_sn

twit_data['future_hits'] = future_hits
twit_data.to_csv('data_formatted.csv')
print(twit_data.head())

print("complete")