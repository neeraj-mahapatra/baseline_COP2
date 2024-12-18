import pandas as pd 

def purchase_frequency(df, groupby_columns, time_period = None): 
    if isinstance(groupby_columns, str): 
        groupby_columns = [groupby_columns]

    
    if time_period: 
        df['Period'] = pd.to_datetime(df['PurchaseDate']).dt.to_period(time_period)
        groupby_columns.append('Period')

    freq_df = df.groupby(groupby_columns).size().reset_index(name = 'Frequency')

    return freq_df

data = {
    'TransID' : [1, 2, 3, 4, 5], 
    'ProductID' : ['P1', 'P2', 'P1', 'P2', 'P1'], 
    'PurchaseDate' : ['2024-12-01', '2024-12-02', '2024-12-01', '2024-12-03', '2024-12-03']
}

df = pd.DataFrame(data)

# overall freq 
print("Overall Frequency: ")
print(purchase_frequency(df, 'ProductID'))

#Weekly freq
print("Weekly Frequency: ")
print(purchase_frequency(df, 'ProductID', time_period = 'W'))

    