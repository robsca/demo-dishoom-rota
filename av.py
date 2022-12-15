import pandas as pd
import streamlit as st
st.set_page_config(layout="wide")
from Esteban import Esteban_
 
st.write('Tornado')
open_time = 8
min_hours = 4
max_hours = 9

# 1. LABOUR MODEL HOURS
path_1 = 'Labour_Model_Hours_w32_w35.csv'
path_2 = 'Labour_Model_Hours_w36_w39.csv'
path_3 = 'Labour_Model_Hours_w40_w43.csv'
# 1.1 Read the data
df_1 = pd.read_csv(path_1)
df_2 = pd.read_csv(path_2)
df_3 = pd.read_csv(path_3)
# 1.2 Merge the data and drop the rows with NaN values
df_Labour_Model_Hours = pd.concat([df_1, df_2, df_3], axis=0)
df_Labour_Model_Hours = df_Labour_Model_Hours.dropna()
# 1.3 Add month and day columns
df_Labour_Model_Hours['Month'] = pd.to_datetime(df_Labour_Model_Hours['Date (DDMMYYYY)']).dt.month
df_Labour_Model_Hours['Day'] = pd.to_datetime(df_Labour_Model_Hours['Date (DDMMYYYY)']).dt.day_name()

# 2. BUDGET 
path_1 = 'budget_rotas/d1.csv'
path_2 = 'budget_rotas/d2.csv'
path_3 = 'budget_rotas/d3.csv'
path_4 = 'budget_rotas/d4.csv'
path_5 = 'budget_rotas/d5.csv'
path_6 = 'budget_rotas/d6.csv'
path_7 = 'budget_rotas/d7.csv'
path_8 = 'budget_rotas/d8.csv'

# Read the data
df_1 = pd.read_csv(path_1) # d1
df_2 = pd.read_csv(path_2) # d2
df_3 = pd.read_csv(path_3) # d3
df_4 = pd.read_csv(path_4) # d4
df_5 = pd.read_csv(path_5) # d5
df_6 = pd.read_csv(path_6) # d6
df_7 = pd.read_csv(path_7) # d7
df_8 = pd.read_csv(path_8) # d8

# add a column with the name of the dataframe 
df_1['Site Code'] = 'D1'
df_2['Site Code'] = 'D2'
df_3['Site Code'] = 'D3'
df_4['Site Code'] = 'D4'
df_5['Site Code'] = 'D5'
df_6['Site Code'] = 'D6'
df_7['Site Code'] = 'D7'
df_8['Site Code'] = 'D8'

# Merge the data
df_Budget = pd.concat([df_1, df_2, df_3, df_4, df_5, df_6, df_7, df_8], axis=0)
# keep only - Site Code, Department, start time, end time, day
df_Budget = df_Budget[['Site Code', 'Department', 'Start Time (Hour)', 'End Time (Hour)', 'Hours', 'Day']]


with st.expander('Show all data'):
    # The data is in the right format
    st.write(df_Labour_Model_Hours) # will be used to calculate the rota
    st.write(df_Budget) # will be used to check the shifts
    # departments should be the same in both dataframes
    dep_labour = df_Labour_Model_Hours['Department'].unique()
    dep_budget = df_Budget['Department'].unique()
    st.write('The departments in LABOUR MODEL are: ', dep_labour)
    st.write('The departments in BUDGET are: ', dep_budget)
    # modify from expeditors to expo
    df_Budget['Department'] = df_Budget['Department'].replace('Expeditors', 'Expo')


# get unique restaurants, months, days, departments
site_codes = df_Labour_Model_Hours['Site Code'].unique()
months = df_Labour_Model_Hours['Month'].unique()
days = df_Labour_Model_Hours['Day'].unique()
departments = df_Labour_Model_Hours['Department'].unique()
# add all to all of them
restaurants = ['All'] + list(site_codes)
months = list(months)
days = ['All'] + list(days)
departments = ['All'] + list(departments)

# 1. Select the restaurant
with st.sidebar.expander('Parameters'):
    site_code = st.selectbox('Select the restaurant', restaurants)
    month = st.selectbox('Select the month', months)
    day = st.selectbox('Select the day', days)
    department = st.selectbox('Select the department', departments)

# 2. Filter the data
data = df_Labour_Model_Hours
data = data[data['Month'] == month]

if site_code != 'All':
    data = data[data['Site Code'] == site_code]
if day != 'All':
    data = data[data['Day'] == day]
if department != 'All':
    data = data[data['Department'] == department]

with st.expander('Labour Model Hours Data'):
    st.write('The data from LABOUR MODEL is filtered by the parameters selected')
    st.write(data)
    # get all departments
    departments = data['Department'].unique()
    st.write('The departments are: ', departments)
data_Labour_Model_Hours = data

# filter the other data as well
data_budget = df_Budget
if site_code != 'All':
    data_budget = data_budget[data_budget['Site Code'] == site_code]
if day != 'All':
    data_budget = data_budget[data_budget['Day'] == day]    
if department != 'All':
    data_budget = data_budget[data_budget['Department'] == department]

with st.expander('Budget Data'):
    st.write('The data from BUDGET is filtered by the parameters selected')
    st.write(data_budget)
    # get all departments
    departments = data_budget['Department'].unique()
    st.write('The departments are: ', departments)


# find all the restaurants in list
restaurants = data_Labour_Model_Hours['Site Code'].unique()
days = data_Labour_Model_Hours['Day'].unique()
departments = data_Labour_Model_Hours['Department'].unique()


data = data_Labour_Model_Hours
sum_generated_hours = 0
# filter the data
hours_counter_generated = {} # for each hour it will count how many people start at that hour
hours_counter_generated_length = {} # for each hour it will store the length of the shift and sum it up

for i in range(len(restaurants)):
        site_code = restaurants[i]
        data_restaurant = data[data['Site Code'] == site_code]
        for department in departments:
            data_department = data_restaurant[data_restaurant['Department'] == department]
            data_month = data_department[data_department['Month'] == month]
            # add day name column
            for day in days:
                data_day = data_month[data_month['Day'] == day]
                # get average in that day
                data_to_save = data_day.groupby('Hour').mean().round(0)

                #ADDING Calculate hours counter
                # 1. create an appropriate rota
                contraints = data_to_save['Labour Model Hours'].values
                esteban = Esteban_(contraints)
                rota, shifts = esteban.solving_(open_time, min_hours, max_hours)
                #Check if the shift exceed the max hours
                shift_to_split = []
                shifts_ = []
                for shift in shifts:
                    start = shift[0]
                    end = shift[1]
                    if end - start > max_hours:
                        shift_to_split.append(shift)
                        #st.write(f'Shift to split: {shift}')
                        # divide the shift in two
                        mid = (start + end) // 2
                        shifts_.append((start, mid))
                        shifts_.append((mid, end))
                    else:
                        shifts_.append(shift)
                shifts = shifts_
                #Split the shift

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

                    # add the length of the shift to the sum
                    sum_generated_hours += length

#st.write(f'Generated Rota Hours Counter: {hours_counter_generated}')
#st.write('---')
#st.write(f'Generated Rota Hours Counter Length: {hours_counter_generated_length}')


'''Budget'''
# same counting for budget
data = data_budget
sum_budget_hours = 0
# filter the data
hours_counter_budget = {} # for each hour it will count how many people start at that hour
hours_counter_budget_length = {} # for each hour it will store the length of the shift and sum it up

# delete all the rows that have 0 hours or '0' hours or nan
data = data[data['Hours'].notna()]
data = data[data['Hours'] != '0']
data = data[data['Hours'] != 0.0]

# count for each row how many people start at that hour
for i in range(len(data)):
    row = data.iloc[i]
    start = str(row['Start Time (Hour)'])
    end = str(row['End Time (Hour)'])
    length = int(row['Hours'])
    # keep only the hour
    start = start.split(':')[0]
    end = end.split(':')[0]

    # convert to int
    start = int(start)
    end = int(end)

    # st.write(f'Start: {start}')
    # st.write(f'End: {end}')

    if start in hours_counter_budget:
        hours_counter_budget[start] += 1
        hours_counter_budget_length[start] += length
    else:
        hours_counter_budget[start] = 1
        hours_counter_budget_length[start] = length

    # add the length of the shift to the sum
    sum_budget_hours += length
    
#st.write(f'Budget Hours Counter: {hours_counter_budget}')
#st.write(f'Budget Hours Counter Length: {hours_counter_budget_length}')


# plot data
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Bar(
    x=list(hours_counter_budget.keys()),
    y=list(hours_counter_budget.values()),
    name='Budget',
    marker_color='indianred'
))
fig.add_trace(go.Bar(
    x=list(hours_counter_generated.keys()),
    y=list(hours_counter_generated.values()),
    name='Generated Rota',
    marker_color='lightsalmon'
))

# add title
fig.update_layout(
    title_text="Budget vs Generated Rota - Starting Times",
    xaxis_title="Hour",
    yaxis_title="Number of People",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="#7f7f7f"
    )
)

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(barmode='group', xaxis_tickangle=-45)


fig_2 = go.Figure()
fig_2.add_trace(go.Bar(
    x=list(hours_counter_budget_length.keys()),
    y=list(hours_counter_budget_length.values()),
    name='Budget',
    marker_color='indianred'
))


fig_2.add_trace(go.Bar(
    x=list(hours_counter_generated_length.keys()),
    y=list(hours_counter_generated_length.values()),
    name='Generated Rota',
    marker_color='lightsalmon'
))

# add title
fig_2.update_layout(
    title_text="Budget vs Generated Rota - Length of Shifts",
    xaxis_title="Hour",
    yaxis_title="Length of Shifts",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="#7f7f7f"
    )
)

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig_2.update_layout(barmode='group', xaxis_tickangle=-45)

c1,c2 = st.columns(2)
c1.plotly_chart(fig)
c2.plotly_chart(fig_2)



# sum of budget hours
c2.subheader('Sum of Budget Hours')
c2.write(sum_budget_hours)

# sum of generated rota hours
c2.subheader('Sum of Generated Rota Hours')
c2.write(sum_generated_hours)
