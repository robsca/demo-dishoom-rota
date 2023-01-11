import streamlit as st
st.set_page_config(layout='wide',initial_sidebar_state='expanded')
import pandas as pd; import random; import plotly.graph_objects as go

path_1 = 'Labour_Model_Hours_w32_w43.csv'
# The script will now take the data and model it to get the averages.

def Modelling():
    from Esteban import Esteban_
    from database import delete_shift_data, delete_data, delete_shift_data 
    df = pd.read_csv(path_1)


    from datetime import date, datetime
    from datetime import timedelta
    import holidays

    c1,c2 = st.columns(2)
    # get today's date
    today = date.today()
    # if today is not monday, get the next monday
    if today.weekday() != 0:
        today += timedelta(days=7-today.weekday())
    # get the date in a week
    in_a_week = today + timedelta(days=7)
    # get the start and end dates
    start_date = c1.date_input('**Start date**', today)
    start_date_year = start_date.year
 
    # check if it's a monday
    is_monday = start_date.weekday() == 0
    # if it's not a monday, get the next monday
    if not is_monday:
        st.info('Please select a Monday')
        # block the rest of the code
        st.stop()
    else:
        pass
    # if the start date is not today, get the end date
    if start_date != today:
        end_date = c2.date_input('**End date**', start_date + timedelta(days=7))
    else:
        end_date = c2.date_input('**End date**', in_a_week)

    end_date_year  = end_date.year
    if start_date_year != end_date_year:
        years = start_date_year, end_date_year
    else:
        years = start_date_year
    
    # Select country
    uk_holidays = holidays.UnitedKingdom(years = years)

    list_of_holidays = []
    for ptr in uk_holidays:
        date_, name = ptr, uk_holidays[ptr]
        # transform the date into a string
        date_ = datetime.strftime(date_, '%Y-%m-%d')
        list_of_holidays.append([date_, name])

    # transform the list into a dataframe
    df_holidays = pd.DataFrame(list_of_holidays, columns = ['Date', 'Holiday'])


    # create a list of dates
    from datetime import timedelta
    dates = []
    for i in range((end_date - start_date).days + 1):
        dates.append(start_date + timedelta(days=i))

    seed_button = st.sidebar.button('Generate Structure')
    if seed_button:
        random_seed = random.randint(0, 1000)
    else:
        random_seed = 42

    # get unique restaurants, months, days, departments
    restaurants = df['Site Code'].unique();                  months = df['Month'].unique()
    days_list = ['Week Rota'] + df['Day'].unique().tolist(); departments = df['Department'].unique()


    # 4. Create the sidebar
    with st.sidebar.expander('⚙️ Selections ', expanded=False):
        site_code = st.selectbox('Select a restaurant', restaurants)
        department = st.selectbox('Select a department', departments, index=4)
        month = st.selectbox('Select a month', months)
        day_ = st.selectbox('Select a day', days_list)

    expander_percentiles = st.sidebar.expander('🪛 Percentiles ', expanded=False)
    # add selectbox to allow the user to select the percentile  for all the days
    
    select_perc = expander_percentiles.selectbox('Select the percentile for all the days', [None, 'Average', '95th Percentile', '90th Percentile', '75th Percentile', '50th Percentile', '25th Percentile'])
    if select_perc != None:
        percentile_message = select_perc
    else:
        percentile_message = None

    with st.sidebar.expander('🔧 Shift Parameters ', expanded=False):
        max_hours = int(st.number_input('Max hours', min_value=0, max_value=12, value=9))
        min_hours = int(st.number_input('Min hours', min_value=3, max_value=8, value=4))

    # 5. Filter the data from User selections
    data = df[df['Site Code'] == site_code] 
    data = data[data['Department'] == department]
    data = data[data['Month'] == month]

    def handle_single_d(data, day_, deletion = False, percentile_message = None, date_on_expander = None, percentile_for_all = None):
        from database import insert_shift_data, delete_shift_data, insert_data, delete_data, insert_shift_data, delete_shift_data 

        data = data[data['Day'] == day_]

        # Data is ready to be worked with.

        data_to_save = data.groupby('Hour').mean().round(0) # take the averages for each hours and rounding the values.
        # If we want to model the data we can do it here.

        # ADDING PERCENTILES MODELLING
        # 1. Create the function to transform the data
        def transform_in_95_percentile(x):
            return x.quantile(0.95)

        def transform_in_90_percentile(x):
            return x.quantile(0.9)

        def transform_in_75_percentile(x):
            return x.quantile(0.75)

        def transform_in_50_percentile(x):
            return x.quantile(0.5)

        def transform_in_25_percentile(x):
            return x.quantile(0.25)
        
        # Create the UI to allow user to 
        unique_key = f'{site_code}_{department}_{month}_{day_}'
        # add a selectbox to allow the user to select the percentile  for all the days
        if percentile_for_all != None:
            percentile_option = percentile_for_all

            # apply the transformation
            if percentile_option == 'Average':
                pass
            elif percentile_option == '95th Percentile':
                data_to_save = data.groupby('Hour').apply(transform_in_95_percentile).round(0)
            elif percentile_option == '90th Percentile':
                data_to_save = data.groupby('Hour').apply(transform_in_90_percentile).round(0)
            elif percentile_option == '75th Percentile':
                data_to_save = data.groupby('Hour').apply(transform_in_75_percentile).round(0)
            elif percentile_option == '50th Percentile':
                data_to_save = data.groupby('Hour').apply(transform_in_50_percentile).round(0)
            elif percentile_option == '25th Percentile':
                data_to_save = data.groupby('Hour').apply(transform_in_25_percentile).round(0)

        else:
            if percentile_message:
                percentile_option = expander_percentiles.selectbox(percentile_message, ['Average', '95%', '90%', '75%', '50%', '25%'], key = unique_key)
            else:
                percentile_option = expander_percentiles.selectbox('Select a percentile', ['Average', '95%', '90%', '75%', '50%', '25%'], key = unique_key)
            
            if percentile_option == 'Average':
                pass
            elif percentile_option == '95%':
                data_to_save = data.groupby('Hour').apply(transform_in_95_percentile).round(0)
            elif percentile_option == '90%':
                data_to_save = data.groupby('Hour').apply(transform_in_90_percentile).round(0)
            elif percentile_option == '75%':
                data_to_save = data.groupby('Hour').apply(transform_in_75_percentile).round(0)
            elif percentile_option == '50%':
                data_to_save = data.groupby('Hour').apply(transform_in_50_percentile).round(0)
            elif percentile_option == '25%':
                data_to_save = data.groupby('Hour').apply(transform_in_25_percentile).round(0)
            else:
                pass

        percentile_option = percentile_option + ' Percentile' if percentile_option != 'Average' else percentile_option
        constraints = data_to_save['Labour Model Hours'].values # we need them in a list format for the Esteban algorithm
        budget = data_to_save['Budget Rota Hours'] 

        

        # 6. Save the data to the DB
        if deletion:
            delete_shift_data()
            delete_data()

        open_time = 100 # set a high number to be able to compare with any initial value
        for index, row in data_to_save.iterrows():
            # get the values
            hour = index
            if hour < open_time:
                open_time = hour
            # if hour 
            labour_model_hours = row['Labour Model Hours']
            actual_hours = row["Actual Hours '22"]
            budget_rota_hours = row['Budget Rota Hours']
            insert_data(site_code, department, int(month), day_, actual_hours, budget_rota_hours, labour_model_hours)
        
        # 7.PLOT ACTUALS, BUDGET AND LABOUR MODEL HOURS
        fig = go.Figure()
        fig.add_trace(go.Bar(x=data_to_save.index, y=data_to_save['Labour Model Hours'], name='Labour Model Hours'))
        # add actuals and budget
        fig.add_trace(go.Bar(x=data_to_save.index, y=data_to_save["Actual Hours '22"], name='Actuals'))
        fig.add_trace(go.Scatter(x=data_to_save.index, y=data_to_save['Budget Rota Hours'],name='Budget'))           
        fig.update_layout(title=f'{percentile_option} - Labour Model Hours for {site_code} - {department} - {month} - {day_}',
                            xaxis_title='Hour',    
                                yaxis_title='Labour Model Hours')
        st.plotly_chart(fig, use_container_width=True)

        # 8. Generate the rota
        constraints = data_to_save['Labour Model Hours'].values

        # get parameters for Algorithm
        open_time_ = data_to_save.index.min()
        #st.write(f'Open time: {open_time}')
        constraints = data_to_save['Labour Model Hours'].values
        constraints_ = []   
        columns = st.columns(len(constraints))
        for i, c in enumerate(constraints):
            a = columns[i].number_input(f'Hour {i + open_time_}', value=c, min_value=0.0, max_value=100.0, step=1.0, key=f'hour_{i}_constraint_{day}')
            constraints_.append(a)
        constraints = constraints_

        
        esteban = Esteban_(constraints, random_seed)
        rota, shifts = esteban.solving_(open_time, min_hours, max_hours)
        #st.write(f'Shifts: {shifts}')

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
        fig = go.Figure()
        hours = [i+open_time for i in range(len(rota))]
        fig.add_trace(go.Bar(x=hours, y=data_to_save["Labour Model Hours"], name='Labour Model Hours'))
        fig.add_trace(go.Bar(x=hours, y=rota, name='Generated Rota'))
        # add actuals and budget
        fig.add_trace(go.Scatter(x=hours, y=data_to_save['Budget Rota Hours'],name='Budget'))

        fig.update_layout(title=f'Rota for {site_code} - {department} - {month} - {day_}',
                                xaxis_title='Hour', 
                                yaxis_title='Labour Model Hours')

        st.plotly_chart(fig, use_container_width=True)
        st.write('---')

        # 10. Generate the shifts
        from database import insert_shift_data, delete_shift_data
        data_frame = pd.DataFrame(columns=['Employees','Start', 'End'])
        for i, shift in enumerate(shifts):
            employee = f'{department} - {i}'
            start = int(shift[0])
            end = int(shift[1])
            data_frame = pd.concat([data_frame, pd.DataFrame({'Employees': employee, 'Start': start, 'End': end}, index=[0])])
            # append on database
            insert_shift_data(site_code, department, int(month), day_, start, end)


        # calculate some differences (hours over budget, hours over labour model)
        hours_over_budget = data_to_save['Labour Model Hours'].sum() - data_to_save['Budget Rota Hours'].sum()
        hours_over_labour_model = sum(rota) - data_to_save['Labour Model Hours'].sum()

        # 11. Chart with difference between budget and rota hour by hour
        fig = go.Figure()
        fig.add_trace(go.Bar(x=data_to_save.index, y=data_to_save['Budget Rota Hours'] - data_to_save['Labour Model Hours'], name='Budget - Labour Model Hours', orientation='v', opacity=0.5))
        fig.update_traces(marker_color=['green' if _y < 0 else 'red' if _y != 0 else 'blue' for _y in data_to_save['Budget Rota Hours'] - data_to_save['Labour Model Hours']])
        fig.update_traces(marker_line_width=[5 if _y == 0 else 1 for _y in data_to_save['Budget Rota Hours'] - data_to_save['Labour Model Hours']])
        fig.update_layout(title=f'Budget VS Generated Rota- {site_code} - {department} - {month} - {day_}',
                                xaxis_title='Hour', 
                                yaxis_title='Labour Model Hours')   

        # 12. Show the data
        c1,c2 = st.columns(2)
        c1.subheader('Shift Structure')
        c1.write(data_frame)
        c1.write(f'Hours over budget: {hours_over_budget}')
        c1.write(f'Hours over labour model: {hours_over_labour_model}')
        c2.plotly_chart(fig, use_container_width=True)
    
    if day_ != 'Week Rota':
        handle_single_d(data, day_, deletion=True)
    else:
        delete_shift_data()
        delete_data()
        # for all days
        days_ = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        expander_percentiles.write('---')
        for day, date in zip(days_, dates):
            # if the date is a holiday
            if date in df_holidays['Date'].values:
                # get the holiday name, and add it to the expander
                holiday_name = df_holidays[df_holidays['Date'] == date]['Holiday'].values[0]
                with st.expander(f'{date} - **{day}** - {holiday_name}'):
                    handle_single_d(data, day, deletion=False, percentile_message= percentile_message, percentile_for_all=select_perc)
            else:
                # if the date is not a holiday, just add the day to the expander
                with st.expander(f'{date} - **{day}**'):
                    handle_single_d(data, day, deletion=False, percentile_message= percentile_message, percentile_for_all=select_perc)
Modelling()         