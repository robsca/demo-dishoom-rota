import streamlit as st
import pandas as pd


path1 = 'data/Labour_Model_Hours_w32_w35.csv'
path2 = 'data/Labour_Model_Hours_w36_w39.csv'
path3 = 'data/Labour_Model_Hours_w40_w43.csv'
data1 = pd.read_csv(path1)
data2 = pd.read_csv(path2)
data3 = pd.read_csv(path3)

# concatenate data
data = pd.concat([data1, data2, data3], axis=0)
# add column for day name
# find the day name from date
data['Day'] = pd.to_datetime(data['Date (DDMMYYYY)']).dt.day_name()


path4 = 'Labour_Model_Hours_w32_w43.csv'
data_all = pd.read_csv(path4)


# get unique restaurants
restaurants = data['Site Code'].unique()
days = data['Day'].unique()
departments = data['Department'].unique()

# filter data
select_restaurant = st.sidebar.selectbox('Select Restaurant', restaurants) 
select_day = st.sidebar.selectbox('Select Day', days)
select_department = st.sidebar.selectbox('Select Department', departments)

# filter data
filtered_data = data[(data['Site Code'] == select_restaurant) & (data['Day'] == select_day) & (data['Department'] == select_department)]

st.write(filtered_data)
# filter data
filtered_data_all = data_all[(data_all['Site Code'] == select_restaurant) & (data_all['Day'] == select_day) & (data_all['Department'] == select_department)]
st.write(filtered_data_all)

# group it by hour
grouped_data_all = filtered_data_all.groupby('Hour').mean()
st.write(grouped_data_all)