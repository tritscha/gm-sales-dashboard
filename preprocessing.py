import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

events_df = pd.read_csv('data/events1.csv')
items_df = pd.read_csv('data/items.csv')

# Merge the two dataframes
df = pd.merge(events_df, items_df, left_on='item_id', right_on='id')

df.drop(columns=['variant'], inplace=True)
df.drop(columns=['id'], inplace=True)
df.fillna({'country': 'UNK'}, inplace=True)

df['date'] = pd.to_datetime(df['date'])
df['date_day'] = df['date'].dt.date
events_over_time = df['date_day'].value_counts().sort_index()
events_over_time_by_type = df.groupby(['date_day', 'type']).size().unstack().fillna(0)

# Filter the dataframe for rows where add_to_cart is 0
zero_add_to_cart_days = events_over_time_by_type[events_over_time_by_type['add_to_cart'] == 0]

# Find the last day with 0 add_to_cart events
last_zero_add_to_cart_day = zero_add_to_cart_days.index.max()
last_zero_add_to_cart_day

# trim df to only include data from last_zero_add_to_cart_day + 1
df = df[df['date_day'] >= last_zero_add_to_cart_day + pd.Timedelta(days=1)]

# save the dataframe to a new csv file
df.to_csv('data/preprocessed_data.csv', index=False)