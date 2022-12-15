import pandas as pd
import streamlit as st
st.set_page_config(layout="wide")
from Esteban import Esteban_

open_time = 8
min_hours = 4
max_hours = 9


path_1 = 'Labour_Model_Hours_w32_w35.csv'
path_2 = 'Labour_Model_Hours_w36_w39.csv'
path_3 = 'Labour_Model_Hours_w40_w43.csv'

# Read the data
df_1 = pd.read_csv(path_1)
df_2 = pd.read_csv(path_2)
df_3 = pd.read_csv(path_3)

# merge the data
df = pd.concat([df_1, df_2, df_3], axis=0)

# how many nan
num_nan = df.isna().sum()
df = df.dropna()
# add month and day columns
df['Month'] = pd.to_datetime(df['Date (DDMMYYYY)']).dt.month
# add day name column
df['Day'] = pd.to_datetime(df['Date (DDMMYYYY)']).dt.day_name()

with st.expander('Show all data'):
    st.write(df)

# get unique restaurants
restaurants = df['Site Code'].unique()
# get unique months
months = df['Month'].unique()
# get unique days
days = df['Day'].unique()
# get unique departments
departments = df['Department'].unique()


data = df
# filter the data
hours_counter_generated = {} # for each hour it will count how many people start at that hour
hours_counter_generated_length = {} # for each hour it will store the length of the shift and sum it up
for i in range(len(restaurants)):
    #with st.expander(f'{restaurants[i]}'):
        site_code = restaurants[i]
        data_restaurant = data[data['Site Code'] == site_code]
        for department in departments:
            data_department = data_restaurant[data_restaurant['Department'] == department]
            for month in months:
                data_month = data_department[data_department['Month'] == month]
                # add day name column
                for day in days:
                    #st.write(f'{site_code} - {department} - {month} - {day}')
                    data_day = data_month[data_month['Day'] == day]
                    # take the averages hour by hour rounding the values
                    data_to_save = data_day.groupby('Hour').mean().round(0)
                    #st.write(data_to_save)
                    #st.write('---')
                    #data_to_save.to_csv(f'data_averages/{site_code}_{department}_{month}_{day}.csv')


                    #'''ADDING Calculate hours counter'''
                    # 1. create an appropriate rota
                    # 1.1 Get constraint, open_time, min_hours, max_hours to run the algorithm
                    contraints = data_to_save['Labour Model Hours'].values
                    print(contraints)

                    esteban = Esteban_(contraints)
                    rota, shifts = esteban.solving_(open_time, min_hours, max_hours)
                    #st.write(f'Generated Rota: {rota}')
                    #st.write(f'Generated Shifts: {shifts}')
                    # get all the starting hours
                    starting_hours = [shift[0] for shift in shifts]
                    ending_hours = [shift[1] for shift in shifts]
                    # count how many people start at each hour
                    for i, hour in enumerate(starting_hours):
                        length = ending_hours[i] - starting_hours[i]
                        if hour in hours_counter_generated:
                            hours_counter_generated[hour] += 1
                            hours_counter_generated_length[hour] += length
                        else:
                            hours_counter_generated[hour] = 1
                            hours_counter_generated_length[hour] = length

st.write(f'Generated Rota Hours Counter: {hours_counter_generated}')
st.write('---')
st.write(f'Generated Rota Hours Counter Length: {hours_counter_generated_length}')


path_1 = 'budget_rotas/d1.csv'
path_2 = 'budget_rotas/d2.csv'
path_3 = 'budget_rotas/d3.csv'
path_4 = 'budget_rotas/d4.csv'
path_5 = 'budget_rotas/d5.csv'
path_6 = 'budget_rotas/d6.csv'
path_7 = 'budget_rotas/d7.csv'
path_8 = 'budget_rotas/d8.csv'
path_9 = 'budget_rotas/d9.csv'


# Read the data
df_1 = pd.read_csv(path_1)
df_2 = pd.read_csv(path_2)
df_3 = pd.read_csv(path_3)
df_4 = pd.read_csv(path_4)
df_5 = pd.read_csv(path_5)
df_6 = pd.read_csv(path_6)
df_7 = pd.read_csv(path_7)
df_8 = pd.read_csv(path_8)
df_9 = pd.read_csv(path_9)

list_of_dfs = [df_1, df_2, df_3, df_4, df_5, df_6, df_7, df_8, df_9]

# BUDGET 
counting_starts_budget = {}
counting_starts_budget_length = {}
for df in list_of_dfs:
    # get all the starting hours
    starting_hours = df['Start Time (Hour)'].values
    # transform the starting hours to int
    starting_hours = [str(hour) for hour in starting_hours]
    
    # keep only hours
    starting_hours = [hour.split(':')[0] for hour in starting_hours if hour.split(':')[0] != '0']
    ending_hours = df['End Time (Hour)'].values
    # transform the starting hours to int
    ending_hours = [str(hour) for hour in ending_hours]
    # keep only hours
    ending_hours = [hour.split(':')[0] for hour in ending_hours if hour.split(':')[0] != '0']
    st.write(starting_hours)
    
    # count how many people start at each hour
    for i, hour in enumerate(starting_hours):
        length = int(ending_hours[i]) - int(starting_hours[i])
        if hour in counting_starts_budget:
            counting_starts_budget[hour] += 1
            counting_starts_budget_length[hour] += length
        else:
            counting_starts_budget[hour] = 1
            counting_starts_budget_length[hour] = length

st.write(f'Budget Rota Hours Counter: {counting_starts_budget}')
st.write('---')
st.write(f'Budget Rota Hours Counter Length: {counting_starts_budget_length}')

import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Bar(
    x=list(hours_counter_generated.keys()),
    y=list(hours_counter_generated.values()),
    name='Generated Rota',
    marker_color='indianred'
))
fig.add_trace(go.Bar(
    x=list(counting_starts_budget.keys()),
    y=list(counting_starts_budget.values()),
    name='Budget Rota',
    marker_color='lightsalmon'
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(barmode='group', xaxis_tickangle=-45)
st.plotly_chart(fig)
