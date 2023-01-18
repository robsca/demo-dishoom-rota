import streamlit as st
st.set_page_config(layout='wide',initial_sidebar_state='expanded')
import pandas as pd; import random; import plotly.graph_objects as go

path_1 = 'Labour_Model_Hours_alls.csv'
# The script will now take the data and model it to get the averages.


# HELPER FUNCTIONS
def get_dates():
    '''
    This function returns today's date and the date in a week
    If today is not monday, it returns the next monday and the date in a week
    '''
    from datetime import date, datetime, timedelta
    # get today's date
    today = date.today()
    # if today is not monday, get the next monday
    if today.weekday() != 0:
        today += timedelta(days=7-today.weekday())
    # get the date in a week
    in_a_week = today + timedelta(days=7)
    return today, in_a_week

def get_holidays(start_date, end_date, years):
    import holidays
    from datetime import datetime
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
    return df_holidays

def hadle_start_end_date(start_date, today, in_a_week, c2):
    '''
    This function checks if the start date is a monday
    '''
    from datetime import date, datetime, timedelta
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
    # get the year of the start date and end date
    start_date_year = start_date.year
    end_date_year  = end_date.year
    if start_date_year != end_date_year:
        years = start_date_year, end_date_year
    else:
        years = start_date_year
    return start_date, end_date, years

def get_dates_between_start_end(start_date, end_date):
    # create a list of dates
    from datetime import timedelta
    dates = []
    for i in range((end_date - start_date).days + 1):
        dates.append(start_date + timedelta(days=i))
    return dates

def random_seed_generator():
    # Set random Seed for generation
    seed_button = st.sidebar.button('Generate Structure')
    if seed_button:
        random_seed = random.randint(0, 1000)
    else:
        random_seed = 42
    return random_seed

# LAMBDA FUNCTIONS

def transform_in_percentile(x, percentile):
    '''
    25 percentile = 0.25
    '''
    percentile = percentile/100
    return x.quantile(percentile)


# MAIN FUNCTION
def Modelling():
    c1,c2 = st.columns(2)
    from datetime import date, timedelta
    from Esteban import Esteban_
    from database import delete_shift_data, delete_data, delete_shift_data 
    df = pd.read_csv(path_1)

    # get unique restaurants, months, days, departments
    restaurants = df['Site Code'].unique()
    # sort the restaurant by the name
    restaurants = sorted(restaurants)
    months = ['All'] + df['Month'].unique().tolist()
    days_list = ['Week Rota'] + df['Day'].unique().tolist()
    departments = df['Department'].unique()
    # sort the departments by the name
    departments = sorted(departments)

    random_seed = random_seed_generator()
    today, in_a_week = get_dates()

    # Create the sidebar expanders 
    sidebar_expander =  st.sidebar.expander('⚙️ Selections ', expanded=False)
    expander_percentiles = st.sidebar.expander('🪛 Percentiles ', expanded=False)
    expander_shift_parameters = st.sidebar.expander('🔧 Shift Parameters ', expanded=False)

    # Get the start date and end date
    start_date = c1.date_input('**Start date**', today)
    start_date, end_date, years = hadle_start_end_date(start_date, today, in_a_week, c2)

    # Once the user has selected the start and end date, we can get the holidays
    df_holidays = get_holidays(start_date, end_date, years)
    dates = get_dates_between_start_end(start_date, end_date)

    # 1. Filling Expander Selections
    site_code = sidebar_expander.selectbox('Select a restaurant', restaurants)
    department = sidebar_expander.selectbox('Select a department', departments, index=len(departments)-1)
    month = sidebar_expander.selectbox('Select a month', months)
    day_ = sidebar_expander.selectbox('Select a day', days_list)

    # 2. Filling Expander Percentiles
    select_perc = expander_percentiles.selectbox('Select the percentile for all the days', [None, 'Average', '95th Percentile', '90th Percentile', '75th Percentile', '50th Percentile', '25th Percentile'])
    percentile_message = None if select_perc == None else select_perc

    # 3. Filling Expander Shift Parameters
    max_hours = int(expander_shift_parameters.number_input('Max hours', min_value=0, max_value=12, value=9))
    min_hours = int(expander_shift_parameters.number_input('Min hours', min_value=3, max_value=8, value=4))

    # 4. Filter the data from User selections
    data = df[df['Site Code'] == site_code] 
    data['Month'] = data['Month'].astype(int)

 
    def handle_single_d(data, day_, deletion = False, percentile_message = None, date_on_expander = None, percentile_for_all = None, month = 'All', site_code = site_code, department = department):
        from database import insert_shift_data, delete_shift_data, insert_data, delete_data, insert_shift_data, delete_shift_data 
        # filter by site_code and department and day
        data = data[data['Department'] == department]
        data = data[data['Day'] == day_]
        data = data[data['Site Code'] == site_code]
        # if day == 'Wednesday':
        #     st.write(data)

        # Data is ready to be worked with.
        if month  == 'All':
            month = 1
        else:
            data= data[data['Month'] == int(month)]
            st.write(month)



        # ADDING PERCENTILES MODELLING
        data_to_save = data.groupby('Hour').mean().round(0) # DEFAULT - take the averages for each hours and rounding the values.
        # Create the UI to allow user to 
        unique_key = f'{site_code}_{department}_{month}_{day_}'
        # add a selectbox to allow the user to select the percentile  for all the days
        if percentile_for_all != None:
            percentile_option = percentile_for_all

            # apply the transformation
            if percentile_option != 'Average':
                # take only the first 2 characters
                percentile_option = percentile_option[:2]
                # convert to float
                percentile_option = float(percentile_option)
                # apply the transformation
                data_to_save = data.groupby('Hour').apply(transform_in_percentile, percentile = percentile_option).round(0)
                percentile_option = str(percentile_option) 
        else:
            if percentile_message:
                percentile_option = expander_percentiles.selectbox(percentile_message, ['Average', '95%', '90%', '75%', '50%', '25%'], key = unique_key)
            else:
                percentile_option = expander_percentiles.selectbox('Select a percentile', ['Average', '95%', '90%', '75%', '50%', '25%'], key = unique_key)
            
            if percentile_option != 'Average':
                # take only the first 2 characters
                percentile_option = percentile_option[:2]
                # convert to float
                percentile_option = float(percentile_option)
                # apply the transformation
                data_to_save = data.groupby('Hour').apply(transform_in_percentile, percentile = percentile_option).round(0)
                percentile_option = str(percentile_option)

        percentile_option = percentile_option + ' Percentile' if percentile_option != 'Average' else percentile_option
        constraints = data_to_save['Labour Model Hours'].values # we need them in a list format for the Esteban algorithm

        # 6. Save the data to the DB
        if deletion:
            delete_shift_data()
            delete_data()   

        def record_to_database():
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

            return open_time
        
        open_time = record_to_database()

        def plot_actuals_budget_labour_model_hours():
            # 7.PLOT ACTUALS, BUDGET AND LABOUR MODEL HOURS
            fig = go.Figure()
            fig.add_trace(go.Bar(x=data_to_save.index, y=data_to_save['Labour Model Hours'], name='Labour Model Hours'))
            # add actuals and budget
            fig.add_trace(go.Bar(x=data_to_save.index, y=data_to_save["Actual Hours '22"], name='Actuals'))
            fig.add_trace(go.Scatter(x=data_to_save.index, y=data_to_save['Budget Rota Hours'],name='Budget'))           
            fig.update_layout(title=f'{percentile_option} - Labour Model Hours for {site_code} - {department} - {month} - {day_}',
                                xaxis_title='Hour',    
                                    yaxis_title='Labour Model Hours')
            return fig
        
        st.plotly_chart(plot_actuals_budget_labour_model_hours(), use_container_width=True)

        # 8. Generate the rota
        open_time_ = data_to_save.index.min()
        constraints = data_to_save['Labour Model Hours'].values
        constraints_ = []   

        columns = st.columns(len(constraints))
        for i, c in enumerate(constraints):
            a = columns[i].number_input(f'Hour {i + open_time_}', value=c, min_value=0.0, max_value=100.0, step=1.0, key=f'hour_{i}_constraint_{day_}')
            constraints_.append(a)
        constraints = constraints_
        esteban = Esteban_(constraints, random_seed)
        rota, shifts = esteban.solving_(open_time, min_hours, max_hours)
        #st.write(f'Shifts: {shifts}')

        def optimize_shifts(shifts):
            '''
            If a shift is longer than max_hours, split it in two
            '''
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

            '''
            if a shift start after 20:00, move it to 20:00
            '''
            new_adjusted_shifts = []
            for shift in shifts:
                start = shift[0]
                if start > 20: 
                    start = 20
                end = shift[1]
                new_adjusted_shifts.append((start, end))
            shifts = new_adjusted_shifts
            return shifts 

        shifts = optimize_shifts(shifts)

        
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


        # Record the shifts on the database
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
        hours_over_budget = sum(rota) - data_to_save['Budget Rota Hours'].sum()
        hours_over_labour_model = sum(rota) - data_to_save['Labour Model Hours'].sum()
        hours_over_actuals = sum(rota) - data_to_save["Actual Hours '22"].sum()

        labour_model_over_actuals = data_to_save['Labour Model Hours'].sum() - data_to_save["Actual Hours '22"].sum()
        labour_model_over_budget = data_to_save['Labour Model Hours'].sum() - data_to_save['Budget Rota Hours'].sum()

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
        c2.plotly_chart(fig, use_container_width=True)
        st.write('---')
        c1,c2, c3 = st.columns(3)
        c1.write(f'**Generated Rota vs Budget**: {hours_over_budget}')
        c1.write(f'**Generated Rota vs Actuals**: {hours_over_actuals}')
        c2.write(f'**Generated Rota vs Labour Model**: {hours_over_labour_model}')

        c3.write(f'**Labour model over budget**: {labour_model_over_budget}')
        c3.write(f'**Labour model over actuals**: {labour_model_over_actuals}')

    
    
    if day_ != 'Week Rota':
        handle_single_d(data, day_, deletion=True)
    
    else:
        delete_shift_data()
        delete_data()
        days_ = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        expander_percentiles.write('---')
        for day, date in zip(days_, dates):
            date = str(date)
            data = df[df['Day'] == day]
            data = data[data['Department'] == department]
            if date in df_holidays['Date'].values:
                holiday_name = df_holidays[df_holidays['Date'] == date]['Holiday'].values[0]
                with st.expander(f'{date} - **{day}** - {holiday_name}'):
                    handle_single_d(data, day, deletion=False, percentile_message= percentile_message, percentile_for_all=select_perc, month=month)
            else:
                with st.expander(f'{date} - **{day}**'):
                    handle_single_d(data, day, deletion=False, percentile_message= percentile_message, percentile_for_all=select_perc, month=month)


Modelling()         