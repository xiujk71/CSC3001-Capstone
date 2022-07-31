import threading
import csv

import pandas as pd
import numpy as np
import time
import sqlite3

from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import datasets

from time import sleep

svm_model = None
svm_model_in_use = False
svm_model_in_training = False

class svm_model_trainer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.history_table = None
        self.history_table_classified = None
        self.svm_linear = SVC(kernel= 'linear', random_state=1, C=0.1)

    def future_hits_calc(self):
        self.history_table = pd.read_csv('history_table_demo.csv')

        max_id = self.history_table["id"].max()
        tracker = []
        future_hits = []

        # initalize hit tracker
        for i in range(max_id+5):
            tracker.append([-1,-1])

        # initialize future_hits tracker
        for i in range(len(self.history_table)):
            future_hits.append(-1)

        for index, row in self.history_table.iterrows():
            # get current position
            current_sn = index
            id = row.values[0]
            key_search = row.values[1]
            
            # get old position
            old_hit_sn = tracker[id][key_search]
            
            # if its not first hit, update history_data on future hits
            if old_hit_sn != -1:
                future_hits[old_hit_sn] = current_sn - old_hit_sn

            # update tracker on last position to be hit
            tracker[id][key_search] = current_sn

            print ("id: ", row.values[0])
            print ("old_hit_sn: ", old_hit_sn)
            print ("current_sn: ", current_sn)
            print ("future_hits[old_hit_sn]: ", future_hits[old_hit_sn])
            

        #append future_hits
        self.history_table['future_hits'] = future_hits

        # replace all -1 values in future_hits to 0
        # self.history_table.loc[self.history_table['future_hits'] == -1, 'future_hits'] = 0
        print("History Table:")
        print(self.history_table.tail(20))

    def classify(self):
        self.history_table_classified = self.history_table

        # Get largest future hits
        max_hits = self.history_table_classified['future_hits'].max()

        self.history_table_classified.loc[self.history_table_classified['future_hits'] == -1, 'future_hits'] = max_hits + 1

        # Get Q1 & Q3
        Q3 = int(self.history_table_classified['future_hits'].quantile(0.75))

        self.history_table_classified = self.history_table

        self.history_table_classified.loc[self.history_table_classified['future_hits'] < Q3, 'future_hits'] = 0
        self.history_table_classified.loc[self.history_table_classified['future_hits'] >= Q3, 'future_hits'] = 1

        print("History Table Classified:")
        print(self.history_table_classified.tail(20))

    def train(self):
        global svm_model
        global svm_model_in_use

        target = self.history_table_classified.pop("future_hits")

        # Creating training and test split
        X_train, X_test, y_train, y_test = train_test_split(self.history_table_classified, target, test_size=0.3, random_state=1)
        
        # Feature Scaling
        sc = StandardScaler()
        sc.fit(X_train)
        X_train_std = sc.transform(X_train)
        X_test_std = sc.transform(X_test)

        print("Training Model")
        sleep(5)
        self.svm_linear.fit(X_train_std, y_train)

        while(svm_model_in_use == True):
            sleep(0.1)

        svm_model_in_use = True
        svm_model = self.svm_linear
        svm_model_in_use = False

        print("Training Complete")
    def run(self):
        global svm_model_in_training

        svm_model_in_training = True
        #self.train()
        self.future_hits_calc()
        self.classify()
        self.train()

        svm_model_in_training = False

def drop_table():
    conn = sqlite3.connect('test.db')
    print ("Opened database successfully")
    conn.execute('''DROP table IF EXISTS Follow;''')
    conn.execute('''DROP table IF EXISTS user_cache;''')
    print ("Table droppped successfully")
    conn.close()

def create_table():
    conn = sqlite3.connect('test.db')
    print ("Opened database successfully")

    conn.execute('''CREATE TABLE user_cache
    (
        id                                int PRIMARY KEY,
        iam_id                            text NOT NULL,
        utility_account_number            text NOT NULL,
        is_owner                          boolean NOT NULL DEFAULT FALSE,
        premise_id                        text NOT NULL,
        premise_address                   text NOT NULL,
        has_cooling_utility               boolean NOT NULL DEFAULT FALSE,
        encrypted_user_personal_data      text,
        is_active                         boolean NOT NULL DEFAULT FALSE,
        created_at                        timestamp NOT NULL DEFAULT current_timestamp,
        updated_at                        timestamp NOT NULL DEFAULT current_timestamp,
        updated_by                        text NOT NULL
    );'''
    )
    print ("Table created successfully")

    conn.close()

def add_to_cache(id_string, key_value):

    id = int(id_string)
    iam_id = -1
    utility_account_number = -1
    premise_id = id_string

    if key_value == "0":
        iam_id = id_string
        id += 10000
    elif key_value == "1":
        utility_account_number = id_string
        id += 20000
        
    conn = sqlite3.connect('test.db')
    cmd = '''INSERT INTO user_cache (
            id, 
            iam_id, 
            utility_account_number, 
            is_owner,
            premise_id, 
            premise_address, 
            has_cooling_utility,
            encrypted_user_personal_data,
            is_active,
            updated_by) VALUES (
            %d,
            "%d",
            "%d",
            true,
            "%d",
            "premise_address_test",
            true,
            "encrypted_test",
            true,
            "test_user"
            )''' % (id, int(iam_id), int(utility_account_number), int(premise_id))
        
    conn.execute(cmd);
    conn.commit()
    conn.close()

def reset_csv():
    with open('history_table_demo.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "key_value"])

def write_csv(id_string, key_value):
    data = [id_string, key_value]

    with open('history_table_demo.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(data)

    history_table = pd.read_csv('history_table_demo.csv')
    no_of_entries = len(history_table)

    if (no_of_entries % 10 == 0):
        svm_trainer = svm_model_trainer()
        svm_trainer.start()

def query(id, key_value):
    global svm_model
    global svm_model_in_use

    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    id_string = str(id)
    key_value_string = None
    if key_value == "0": key_value_string = "iam_id"
    if key_value == "1": key_value_string = "utility_account_number"

    print ("key_value_string = ", key_value_string)

    query = "SELECT * FROM user_cache WHERE %s=%s" % (key_value_string, id_string)
    
    cursor.execute(query)
    rows = cursor.fetchall()

    if len(rows) == 0:
        predict = 1

        while svm_model_in_use == True:
            sleep(0.1)
        
        svm_model_in_use = True

        if svm_model != None:
            predict = svm_model.predict(np.array([[int(id_string), int(key_value)]]))
            print("predict: ", predict)

        svm_model_in_use = False


        if predict < 0.5:
            add_to_cache(id_string, key_value)
            
        print ("cache miss: ", id, key_value)
    else:
        print ("cache hit: ", id, key_value)

    write_csv(id_string, key_value)

drop_table()
create_table()
reset_csv()

sleep(1)
while(1):
    id = input("ID Input: ")
    key_value = input("Key Value input: ")
    query (id, key_value)