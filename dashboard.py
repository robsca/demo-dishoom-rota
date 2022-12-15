import pandas as pd
import hydralit_components as hc
import streamlit as st
import plotly.graph_objects as go
st.set_page_config(layout='wide',initial_sidebar_state='collapsed')
from Esteban import Esteban_

max_hours = st.sidebar.number_input('Max hours', min_value=0, max_value=12, value=9)
min_hours = st.sidebar.number_input('Min hours', min_value=3, max_value=8, value=4)
# transform into int
max_hours = int(max_hours)
min_hours = int(min_hours)

def navbar():
    # Images
    markd = '''
    <img src="https://www.dishoom.com/assets/img/roundel-seva.png" width = "120" heigth = "120" >
    '''
    st.markdown(markd, unsafe_allow_html=True)

    # Menu
    menu_data = [
                {'id':'Guide','label':"Guide"},
                {'id':'Generate Rota','label':"Modeling"},
                {'id':'Adjust','label':"Shift Adjustment"},
                {'id':'Rota','label':"Rota"},
                {'id':'Tornado','label':"Comparison"},
                ]

    # Specify the theme
    over_theme = {'menu_background': '#ebd2b9',
                    'txc_inactive': '#6e7074' ,
                    'txc_active':'#6e7074'}

    menu_id = hc.nav_bar(
        menu_definition=menu_data,
        override_theme=over_theme,
        hide_streamlit_markers=True, # Will show the st hamburger as well as the navbar now!
        sticky_nav=False,           # At the top or not
        sticky_mode='sticky',      # jumpy or not-jumpy, but sticky or pinned
    )
    return menu_id

def main():
    if st.button('Generate'):
        import random
        random_seed = random.randint(0, 1000)
    else:
        random_seed = 42

    # 1. Get data
    path_1 = 'Labour_Model_Hours_w32_w43.csv'
   
    # read the data
    df = pd.read_csv(path_1)

    #with st.expander('Show all data'):
    #    st.write(df)

    #4. UI FOR FILTERING
    # get unique restaurants, months, days, departments
    restaurants = df['Site Code'].unique()
    months = df['Month'].unique()
    days = df['Day'].unique()
    departments = df['Department'].unique()

    with st.sidebar.expander('Selections', expanded=True):
        site_code = st.selectbox('Select a restaurant', restaurants)
        department = st.selectbox('Select a department', departments, index=4)
        month = st.selectbox('Select a month', months)
        day = st.selectbox('Select a day', days)

    # 5. Filter the data from User selections
    data = df[df['Site Code'] == site_code]
    data = data[data['Department'] == department]
    data = data[data['Month'] == month]
    data = data[data['Day'] == day]

    # Data is ready to be worked with.
    # take the averages hour by hour rounding the values
    data_to_save = data.groupby('Hour').mean().round(0)
    constraints = data_to_save['Labour Model Hours'].values
    budget = data_to_save['Budget Rota Hours']

    months_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    #with st.expander(f'Average {day} in {site_code} - {department} - {months_names[month]}'):
    #    st.write(data_to_save)

    # 6. Save the data to the DB
    #'''Insert DB connection here and save the data to the DB'''
    from database import insert_data, delete_data
    delete_data()
    # iterate over the data and save it
    open_time = 100
    for index, row in data_to_save.iterrows():
        # get the values
        hour = index
        if hour < open_time:
            open_time = hour
        # if hour 
        labour_model_hours = row['Labour Model Hours']
        actual_hours = row["Actual Hours '22"]
        budget_rota_hours = row['Budget Rota Hours']
        insert_data(site_code, department, int(month), day, actual_hours, budget_rota_hours, labour_model_hours)
    
    # 7. Plot the data
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data_to_save.index, y=data_to_save['Labour Model Hours'], name='Labour Model Hours'))
    # add actuals and budget
    fig.add_trace(go.Bar(x=data_to_save.index, y=data_to_save["Actual Hours '22"], name='Actuals'))
    fig.add_trace(go.Scatter(x=data_to_save.index, y=data_to_save['Budget Rota Hours'],name='Budget'))           
    fig.update_layout(title=f'Averages - Labour Model Hours for {site_code} - {department} - {month} - {day}',
                        xaxis_title='Hour',    
                            yaxis_title='Labour Model Hours')
    st.plotly_chart(fig, use_container_width=True)

    # 8. Generate the rota
    from Esteban import Esteban_
    # get parameters for Algorithm
    #open_time = data_to_save.index.min()
    #st.write(f'Open time: {open_time}')
    constraints = data_to_save['Labour Model Hours'].values
    
    esteban = Esteban_(constraints, random_seed)
    rota, shifts = esteban.solving_(open_time, min_hours, max_hours)
    #st.write(f'Shifts: {shifts}')

    #'''Check if the shift exceed the max hours'''
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
    #'''Split the shift'''


    #''''''
    # 9. Plot the rota
    import plotly.graph_objects as go
    fig = go.Figure()
    hours = [i+open_time for i in range(len(rota))]
    fig.add_trace(go.Bar(x=hours, y=data_to_save["Labour Model Hours"], name='Labour Model Hours'))
    fig.add_trace(go.Bar(x=hours, y=rota, name='Generated Rota'))
    # add actuals and budget
    fig.add_trace(go.Scatter(x=hours, y=data_to_save['Budget Rota Hours'],name='Budget'))

    fig.update_layout(title=f'Rota for {site_code} - {department} - {month} - {day}',
                            xaxis_title='Hour', 
                            yaxis_title='Labour Model Hours')

    st.plotly_chart(fig, use_container_width=True)
    st.write('---')

    # 10. Generate the shifts
    from database import insert_shift_data, delete_shift_data
    delete_shift_data()
    data_frame = pd.DataFrame(columns=['Employees','Start', 'End'])
    for i, shift in enumerate(shifts):
        employee = f'{department} - {i}'
        start = int(shift[0])
        end = int(shift[1])
        data_frame = data_frame.append({'Employees': employee, 'Start': start, 'End': end}, ignore_index=True)
        # append on database
        insert_shift_data(site_code, department, int(month), day, start, end)


    # calculate some differences (hours over budget, hours over labour model)
    hours_over_budget = data_to_save['Labour Model Hours'].sum() - data_to_save['Budget Rota Hours'].sum()
    hours_over_labour_model = sum(rota) - data_to_save['Labour Model Hours'].sum()

    # 11. Chart with difference between budget and rota hour by hour
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data_to_save.index, y=data_to_save['Budget Rota Hours'] - data_to_save['Labour Model Hours'], name='Budget - Labour Model Hours', orientation='v', opacity=0.5))
    fig.update_traces(marker_color=['green' if _y < 0 else 'red' if _y != 0 else 'blue' for _y in data_to_save['Budget Rota Hours'] - data_to_save['Labour Model Hours']])
    fig.update_traces(marker_line_width=[5 if _y == 0 else 1 for _y in data_to_save['Budget Rota Hours'] - data_to_save['Labour Model Hours']])
    fig.update_layout(title=f'Budget VS Generated Rota- {site_code} - {department} - {month} - {day}',
                            xaxis_title='Hour', 
                            yaxis_title='Labour Model Hours')   

    # 12. Show the data
    c1,c2 = st.columns(2)
    c1.subheader('Shift Structure')
    c1.write(data_frame)
    c1.write(f'Hours over budget: {hours_over_budget}')
    c1.write(f'Hours over labour model: {hours_over_labour_model}')
    c2.plotly_chart(fig, use_container_width=True)
    return data_frame, open_time, max_hours, min_hours, department, constraints, budget

def shift_adjustments():
    # need constraints and shifts
    from database import get_data, get_shift_data
    constraints_table = get_data()
    day = constraints_table[0][3]
    site_code = constraints_table[0][0]
    month = constraints_table[0][2]
    constraints = []   
    budget = []     
    actuals = []
    hours = []
    for i, constraint in enumerate(constraints_table):
        constraints.append(int(constraint[-1]))
        budget.append(int(constraint[-2]))
        actuals.append(int(constraint[-3]))
        hours.append(int(constraint[2]))
        department = constraint[1]
    st.subheader(f'**Department**: {department}')
    st.write(f'**Site Code**: {site_code}')
    st.write(f'**Month**: {month}')
    st.write(f'**Day**: {day}')
    st.write('---')

    open_time = min(hours)

    
    shifts_table = get_shift_data()
    shifts = pd.DataFrame(columns=['Employees','Start', 'End'])
    for i, shift in enumerate(shifts_table):
        employee = i
        start = int(float(shift[-2]))
        end = int(float(shift[-1]))
        shifts = shifts.append({'Employees': employee, 'Start': start, 'End': end}, ignore_index=True)

    def validity_shift_checker(sl, min_hours=4, max_hours=8):
        # shift have to be at least four hours and at most max hours
        if sl[1] - sl[0] >= min_hours and sl[1] - sl[0] <= max_hours:
            return True
        else:
            if sl[1] - sl[0] < min_hours:
                st.warning('Shift too short')
            else:
                st.warning('Shift too long')
            return False
        
    # create a slider view of the shifts
    c1, c2 = st.columns(2)
    with c1:
        sliders = []
        # get hour max
        hour_max = shifts['End'].max()
        for index, row in shifts.iterrows():
            # create a slider for each row
            st.write(f'**{department} - {index+1}** : {row["Start"]} - {row["End"]}')
            sl = st.slider('',min_value=int(open_time), max_value=int(hour_max), value=(int(row['Start']), int(row['End'])), key=index)
            if validity_shift_checker(sl, min_hours=min_hours, max_hours=max_hours):
                sliders.append(sl)
    

    # create a new dataframe with the sliders
    new_shifts = pd.DataFrame(sliders, columns=['Start', 'End'])
    # add the index
    new_shifts['index'] = new_shifts.index
    # modify column
    new_shifts['index'] = new_shifts['index'].apply(lambda x: f'{department} :  {x}')
    # set as index
    new_shifts.set_index('index', inplace=True)
    # add a column to the shifts dataframe
    new_shifts['length'] = new_shifts['End'] - new_shifts['Start']
    # add a column for the cost of labour
    new_shifts['cost'] = new_shifts['length'] * 9.50
    # show the new shifts
    hours = []
    # iterate through the new shifts
    for index, row in new_shifts.iterrows():
        shift = [i for i in range(int(row['Start']), int(row['End']))]
        hours.extend(shift)
    # count occurences
    # import counter
    from collections import Counter
    occurences = Counter(hours)
    #st.write(occurences)
    # plot the occurences
    fig = go.Figure()
    # add labour model
    fig.add_trace(go.Bar(x=[
        i+open_time-1 for i in range(len(constraints))], y=constraints, name='Labour Model Hours'))
    fig.add_trace(go.Bar(x=list(occurences.keys()), y=list(occurences.values()), name='Generated Rota Hours'))

    # add budget
    fig.add_trace(go.Scatter
                    (x=[i+open_time-1 for i in range(len(constraints))], y=budget, name='Budget Hours'))
    # show the graph

    c2.plotly_chart(fig)
    c2.write(new_shifts, use_container_width=True)

    with c2:
        if st.button('Save'):
            st.write('Saving')
            # delete rota data of the same day
            from database import delete_rota_data_same_day
            delete_rota_data_same_day(day)

            # save rota to database
            from database import insert_rota_data
            # iterate through the new shifts
            for index, row in new_shifts.iterrows():
                #st.write(row['Start'], row['End'])
                #site_code text, departments text, month text, day text, start_time text, end_time text
                insert_rota_data(site_code, department, month, day, row['Start'], row['End'])
    return new_shifts

def rota_():
    
    # connect to database
    from database import get_rota_data
    # get rota data
    try:
        rota_data = get_rota_data()
        department = rota_data[0][1]
        site_code = rota_data[0][0]
        month = rota_data[0][2]
        day = rota_data[0][3]
        st.subheader(f'**Department**: {department}')
        st.write(f'**Site Code**: {site_code}')
        st.write('---')
    except:
        st.error('No Rota Data yet')
        return
    # check unique days
    days = []
    for i in rota_data:
        days.append(i[3])
    days = list(set(days))
    # sort days
    days.sort()
    days_df = []
    for day in days:
        # iterate through the rota data
        empty_dataframe = pd.DataFrame(columns=['Site Code', 'Department', 'Month', 'Day', 'Start Time', 'End Time'])
        for i in rota_data:
            if i[3] == day:
                # add to dataframe
                empty_dataframe = empty_dataframe.append({'Site Code': i[0], 'Department': i[1], 'Month': i[2], 'Day': i[3], 'Start Time': i[4], 'End Time': i[5]}, ignore_index=True)

        # split at . and take the first element of end times
        empty_dataframe['End Time'] = empty_dataframe['End Time'].apply(lambda x: x.split('.')[0])
        # transform the end time in integer
        empty_dataframe['End Time'] = empty_dataframe['End Time'].apply(lambda x: int(x))
        # if > 24 then - 24
        empty_dataframe['End Time'] = empty_dataframe['End Time'].apply(lambda x: x-24 if x > 24 else x)
        # add : 00 to the end time
        empty_dataframe['End Time'] = empty_dataframe['End Time'].apply(lambda x: f'{x}:00')
        # same for start time
        empty_dataframe['Start Time'] = empty_dataframe['Start Time'].apply(lambda x: x.split('.')[0])
        empty_dataframe['Start Time'] = empty_dataframe['Start Time'].apply(lambda x: int(x))
        empty_dataframe['Start Time'] = empty_dataframe['Start Time'].apply(lambda x: x-24 if x > 24 else x)
        # add : 00 to the start time
        empty_dataframe['Start Time'] = empty_dataframe['Start Time'].apply(lambda x: f'{x}:00')
        days_df.append(empty_dataframe)
    # sort by name of the day of the week respecting the sequence
    sequence = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # sort the days
    days_df.sort(key=lambda x: sequence.index(x['Day'][0]))

   

    # if button delete
    c1,c2 = st.columns(2)
    with c2: # delete
        if st.button('Delete'):
            st.write('Deleting')
            # delete rota data
            from database import delete_rota_data
            delete_rota_data()

    with c1:  # download
        if st.button('Download'):
            # merge all the days ina single dataframe
            empty_dataframe = pd.DataFrame(columns=['Site Code', 'Department', 'Month', 'Day', 'Start Time', 'End Time'])
            for i in rota_data:
                # add to dataframe
                empty_dataframe = empty_dataframe.append({'Site Code': i[0], 'Department': i[1], 'Month': i[2], 'Day': i[3], 'Start Time': i[4], 'End Time': i[5]}, ignore_index=True)
            # download the dataframe

            @st.experimental_memo
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')


            csv = convert_df(empty_dataframe)

            st.download_button(
            "Press to Download",
            csv,
            f"rota.csv",
            "text/csv",
            key='download-csv'
            )
    # show rota day by day
    for i in days_df:
        with st.expander(f'{i["Day"][0]}'):
            st.write(i)

def tornado():
    from Esteban import Esteban_
    
    #open_time = 8

    # 1. LABOUR MODEL HOURS
    path_1 = 'Labour_Model_Hours_w32_w43.csv'
    # 1.1 Read the data
    df_1 = pd.read_csv(path_1)
    # 1.2 Merge the data and drop the rows with NaN values
    df_Labour_Model_Hours = df_1.dropna()
    # 1.3 Add month and day columns
    #df_Labour_Model_Hours['Month'] = pd.to_datetime(df_Labour_Model_Hours['Date (DDMMYYYY)']).dt.month
    #df_Labour_Model_Hours['Day'] = pd.to_datetime(df_Labour_Model_Hours['Date (DDMMYYYY)']).dt.day_name()

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


    #with st.expander('Show all data'):
        # The data is in the right format
        #st.write(df_Labour_Model_Hours) # will be used to calculate the rota
        #st.write(df_Budget) # will be used to check the shifts
        # departments should be the same in both dataframes
    dep_labour = df_Labour_Model_Hours['Department'].unique()
    dep_budget = df_Budget['Department'].unique()
    #st.write('The departments in LABOUR MODEL are: ', dep_labour)
    #st.write('The departments in BUDGET are: ', dep_budget)
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
    with st.sidebar.expander('Parameters', expanded=True):
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

    # with st.expander('Labour Model Hours Data'):
    #     st.write('The data from LABOUR MODEL is filtered by the parameters selected')
    #     st.write(data)
    #     # get all departments
    #     departments = data['Department'].unique()
    #     st.write('The departments are: ', departments)
    data_Labour_Model_Hours = data

    # filter the other data as well
    data_budget = df_Budget
    if site_code != 'All':
        data_budget = data_budget[data_budget['Site Code'] == site_code]
    if day != 'All':
        data_budget = data_budget[data_budget['Day'] == day]    
    if department != 'All':
        data_budget = data_budget[data_budget['Department'] == department]

    # with st.expander('Budget Data'):
    #     st.write('The data from BUDGET is filtered by the parameters selected')
    #     st.write(data_budget)
    #     # get all departments
    #     departments = data_budget['Department'].unique()
    #     st.write('The departments are: ', departments)


    # find all the restaurants in list
    restaurants = data_Labour_Model_Hours['Site Code'].unique()
    days = data_Labour_Model_Hours['Day'].unique()
    departments = data_Labour_Model_Hours['Department'].unique()


    data = data_Labour_Model_Hours
    sum_generated_hours = 0
    # filter the data
    hours_counter_generated = {} # for each hour it will count how many people start at that hour
    hours_counter_generated_length = {} # for each hour it will store the length of the shift and sum it up

    shifts_count = 0
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
                    # find open time
                    open_time = data_to_save.index[0]

                    #ADDING Calculate hours counter
                    # 1. create an appropriate rota
                    contraints = data_to_save['Labour Model Hours'].values
                    esteban = Esteban_(contraints)
                    # open time
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
                    # add the shifts to the counter
                    shifts_count += len(shifts)

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

                        # add the length of the shift to the counter

    #st.write(f'Generated Rota Hours Counter: {hours_counter_generated}')
    #st.write('---')
    #st.write(f'Generated Rota Hours Counter Length: {hours_counter_generated_length}')

    ########################################
    # BUDGET
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
    # fig 1
    # keep only 5 to 21
    hours_counter_budget = {k: v for k, v in hours_counter_budget.items() if k >= 5 and k <= 21}
    hours_counter_generated = {k: v for k, v in hours_counter_generated.items() if k >= 5 and k <= 21}
    
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
            family="Courier New",
            size=12,
            color="#7f7f7f"
        )
    )
    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(barmode='group', xaxis_tickangle=-45)


    # fig 2
    # keep only 5 to 21
    hours_counter_budget_length = {k: v for k, v in hours_counter_budget_length.items() if k >= 5 and k <= 21}
    hours_counter_generated_length = {k: v for k, v in hours_counter_generated_length.items() if k >= 5 and k <= 21}

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
            family="Courier New",
            size=12,
            color="#7f7f7f"
        )
    )
    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig_2.update_layout(barmode='group', xaxis_tickangle=-45)

    # gett number of shift in budget
    number_of_shifts_budget = len(data)
    # get number of shifts in generated rota
    number_of_shift_algo = shifts_count
    c1,c2 = st.columns(2)
    c1.plotly_chart(fig)
    c2.plotly_chart(fig_2)

    c1.subheader('Number of Shifts in Budget')
    c1.write(f'{number_of_shifts_budget}')
    c1.write('---')
    c1.subheader('Number of Shifts in Generated Rota')
    c1.write(f'{number_of_shift_algo}')
    c1.write('---')


    # sum of budget hours
    c2.subheader('Sum of Budget Hours')
    c2.write(f'{round(sum_budget_hours, 2)}')
    c2.write('---')
    c2.subheader('Sum of Generated Rota Hours')
    c2.write(f'{round(sum_generated_hours, 2)}')
    c2.write('---')


    # average length of shift in budget
    average_length_budget = sum_budget_hours / number_of_shifts_budget
    c1.subheader('Average Length of Shift in Budget')
    c1.write(f'{round(average_length_budget, 2)} hrs')
    c1.write('---')
    # average length of shift in generated rota
    average_length_generated = sum_generated_hours / number_of_shift_algo
    c1.subheader('Average Length of Shift in Generated Rota')
    c1.write(f'{round(average_length_generated, 2)} hrs')
    c1.write('---')

def guide():
    st.subheader('What is this?')
    '''
    This is a tool that will help you to create a rota for your restaurant. \n
    The tool will take into account the budget that you have provided and will try to create a rota that will be as close as possible to the budget. \n
    \n

    
    '''
    st.subheader('How does it works?')
    '''
    We asked the GMs to provide us with the following information: \n
    At 20-cover increments, how many members of staff would be needed in a given cafe. \n
    \n
    We then took the average table occupancy covers for the same period to understand the actual \n 
    cover volume, and used to GMs templates to match the optimal number of staff needed for each hour of the day. \n 

    This program uses this matched optimal number of labour hours for each hour of the day, and generates a rota schedule of best fit
    '''
    st.subheader('How to use it?')

    st.write('''
        We have asked the GMs to provide us with the perfect number of staff depending on how many customers we have in the restaurant. \n
        This a fundamental information that we need to have in order to be able to create a rota that is efficient and that will not cost us too much money. \n
        \n
        We use this data to evaluate how this rules translates into a rota and compared the rota with the budget and the actual rota that currently exists. \n
        ''')

        


if __name__ == '__main__':
    choosen = navbar()
    if choosen == 'Generate Rota':
        main()
    elif choosen == 'Adjust':
        shift_adjustments()
    elif choosen == 'Rota':
        rota_()
    elif choosen == 'Tornado':
        tornado()

    elif choosen == 'Guide':
        guide()
