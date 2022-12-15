import pandas as pd
import streamlit as st


def from_restaurant_name_to_site_code(restaurant_name):
    dictionary_res = {
        'Dishoom Carnaby' : 'D4',
        'Dishoom Manchester' : 'D7',
        'Dishoom Kensington' : 'D6',
        'Dishoom Covent Garden' : 'D1',
        'Dishoom Shoreditch' : 'D2',
        'Dishoom Kings Cross' : 'D3',
        'Dishoom Birmingham' : 'D8',
        'Dishoom Edinburgh' : 'D5',

    }
    return dictionary_res[restaurant_name]

def from_site_code_to_restaurant_name(site_code):
    dictionary_res = {
        'D4' : 'Dishoom Carnaby',
        'D7' : 'Dishoom Manchester',
        'D6' : 'Dishoom Kensington',
        'D1' : 'Dishoom Covent Garden',
        'D2' : 'Dishoom Shoreditch',
        'D3' : 'Dishoom Kings Cross',
        'D8' : 'Dishoom Birmingham',
        'D5' : 'Dishoom Edinburgh',
    }
    return dictionary_res[site_code]

def create_data():
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
    st.write(df_Labour_Model_Hours['Day'])


    st.write(df_Labour_Model_Hours)
    # find the unique departments
    departments = df_Labour_Model_Hours['Department'].unique()
    st.write(departments)
    ''''''


    # i need now to find the actuals in the Fourth Data that I have from august.
    # 2. ACTUALS

    path_fourth = 'ActualHoursvRotaHours_2022_Jul.xlsx'
    df_Actuals = pd.read_excel(path_fourth)

    st.write(df_Actuals)


    # change bar support to barback
    df_Actuals['Division'] = df_Actuals['Division'].replace('Bar Support', 'Barback')
    # change bartenders to bartender
    df_Actuals['Division'] = df_Actuals['Division'].replace('Bartenders', 'Bartender')
    # change expeditors to expo
    df_Actuals['Division'] = df_Actuals['Division'].replace('Expeditor', 'Expo')
    # change food and drink runners to runners
    df_Actuals['Division'] = df_Actuals['Division'].replace('Food and drinks Runners', 'Runners')
    # keep only the departments that are in the labour model hours
    df_Actuals = df_Actuals[df_Actuals['Division'].isin(departments)]
    # change Paid/Actual StartTime1 to Start time
    df_Actuals = df_Actuals.rename(columns={'Paid/Actual StartTime1': 'Start time'})
    # change Paid/Actual StopTime1 to Stop time 
    df_Actuals = df_Actuals.rename(columns={'Paid/Actual StopTime1': 'End time'})


    # create a empty dataframe to store the data
    df_Actuals_new = pd.DataFrame(columns=['Home', 'Division', 'Shift date', 'Hour', 'Actual_Number', 'Day'])
    # get all restaurants 
    restaurants = df_Actuals['Home'].unique()
    for choosen_restaurant in restaurants:
        with st.expander(f'{choosen_restaurant}'):
            df_Actuals_restaurant = df_Actuals[df_Actuals['Home'] == choosen_restaurant]
            departments = df_Actuals['Division'].unique()
            for choosen_department in departments:
                st.subheader(choosen_department)
                # filter the data
                df_Actuals_dep = df_Actuals_restaurant[df_Actuals_restaurant['Division'] == choosen_department]
                # choose a day
                days = df_Actuals_dep['Shift date'].unique()
                for date in days:
                    st.write('---')
                    st.subheader(date)
                    # filter the data
                    df_Actuals_date = df_Actuals_dep[df_Actuals_dep['Shift date'] == date]

                    '''CORRECT THE HOURS'''
                    # take off last 2 digits if there's something left else keep it
                    df_Actuals_date['Start time'] = df_Actuals_date['Start time'].apply(lambda x: int(str(x)[:-2]) if len(str(x)) > 2 else int(x))
                    # if len(x) == 2 then add 0 to the beginning
                    df_Actuals_date['End time'] = df_Actuals_date['End time'].apply(lambda x: '0' + str(x) if len(str(x)) == 2 else x)
                    # if len == 1 add 00 to the beginning
                    df_Actuals_date['End time'] = df_Actuals_date['End time'].apply(lambda x: '00' + str(x) if len(str(x)) == 1 else x)
                    df_Actuals_date['End time'] = df_Actuals_date['End time'].apply(lambda x: str(x)[:-2] if len(str(x)) > 2 else x)

                    # take only start time and end time
                    df_Actuals_date = df_Actuals_date[['Start time', 'End time']]
                    # if start time is greater than end time then add 24 to end time
                    df_Actuals_date['End time'] = df_Actuals_date.apply(lambda x: int(x['End time']) + 24 if int(x['Start time']) > int(x['End time']) else int(x['End time']), axis=1)
                    
                    '''CORRECTION DONE'''

                    # translate to list of list -> [[start time, end time], [start time, end time]]
                    df_Actuals_date = df_Actuals_date.values.tolist()
                    # for all the shifts in the list create a list of hours -> [start time, start time + 1, start time + 2, ..., end time]
                    df_Actuals_date = [list(range(x[0], x[1])) for x in df_Actuals_date]

                    #st.write(df_Actuals_date)
                    # flatten the list
                    df_Actuals_date = [item for sublist in df_Actuals_date for item in sublist]
                    # count every hour
                    # get unique hours
                    unique_hours = list(set(df_Actuals_date))
                    # create a dictionary with the hours as keys and the number of times they appear as values
                    actual_hours = {x: df_Actuals_date.count(x) for x in unique_hours}
                    st.write(actual_hours)
                    for hour in actual_hours:
                        #st.write(hour)
                        # tranform date to datetime
                        if hour > 27:
                            hour = 27
                        date = pd.to_datetime(date)
                        df_Actuals_new = df_Actuals_new.append({'Home': choosen_restaurant, 'Division': choosen_department, 'Shift date': date, 'Hour': hour, 'Actual_Number': actual_hours[hour], 'Day': date.day_name()}, ignore_index=True)
                    # create a table like hour | actual number | date | department | Home
    st.write(df_Actuals_new)
    # save as csv
    # 
    df_Actuals_new.to_csv('Actuals.csv', index=False)
    # open and return the dataframe
    df_Actuals_new = pd.read_csv('Actuals.csv')
    return df_Actuals_new

def get_data():
    try:
        df_Actuals_new = pd.read_csv('Actuals.csv')
    except:
        st.write('No file found')
        df_Actuals_new = create_data()
    return df_Actuals_new


# opem the file
df_Actuals_new = get_data()

'''Adjust for averages'''
# create a table with the average for each restaurant and department in each day and hour
df_Actuals_new_average = pd.DataFrame(columns=['Home', 'Division', 'Hour', 'Day', 'Average'])
# for all the restaurant and departments and day and hour calculate mean
for choosen_restaurant in df_Actuals_new['Home'].unique():
    st.write(choosen_restaurant)
    for choosen_department in df_Actuals_new['Division'].unique():
        for day in df_Actuals_new['Day'].unique():
            for hour in df_Actuals_new['Hour'].unique():
                # filter the data
                df_Actuals_new_filtered = df_Actuals_new[(df_Actuals_new['Home'] == choosen_restaurant) & (df_Actuals_new['Division'] == choosen_department) & (df_Actuals_new['Day'] == day) & (df_Actuals_new['Hour'] == hour)]
                # calculate mean
                average = df_Actuals_new_filtered['Actual_Number'].mean()
                # add to the dataframe
                df_Actuals_new_average = df_Actuals_new_average.append({'Home': choosen_restaurant, 'Division': choosen_department, 'Hour': hour, 'Day': day, 'Average': average}, ignore_index=True)

st.write(df_Actuals_new)


# delete the nan row
df_Actuals_new_average = df_Actuals_new_average.dropna()
st.write(df_Actuals_new_average)

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


st.write(df_Labour_Model_Hours)

empty_data_frame = pd.DataFrame(columns=df_Labour_Model_Hours.columns)
restaurants = df_Labour_Model_Hours['Site Code'].unique()
for restaurant in restaurants:
    res_name = from_site_code_to_restaurant_name(restaurant)
    # filter the data labour
    df_Labour_Model_Hours_filtered = df_Labour_Model_Hours[df_Labour_Model_Hours['Site Code'] == restaurant]
    # filter the data actuals
    df_Actuals_new_filtered = df_Actuals_new_average[df_Actuals_new_average['Home'] == res_name]
    departments = df_Labour_Model_Hours_filtered['Department'].unique()
    for department in departments:
        # filter the data labour
        df_Labour_Model_Hours_filtered_2 = df_Labour_Model_Hours_filtered[df_Labour_Model_Hours_filtered['Department'] == department]
        # filter the data actuals
        df_Actuals_new_filtered_2 = df_Actuals_new_filtered[df_Actuals_new_filtered['Division'] == department]
        # now we have the data for each restaurant and department
        # get unique dates in labour
        dates = df_Labour_Model_Hours_filtered_2['Date (DDMMYYYY)'].unique()
        for date in dates:
            # filter the data labour
            df_Labour_Model_Hours_filtered_3 = df_Labour_Model_Hours_filtered_2[df_Labour_Model_Hours_filtered_2['Date (DDMMYYYY)'] == date]
            # day name  
            day = df_Labour_Model_Hours_filtered_3['Day'].unique()[0]
            # now we have the data for each restaurant, department and date
            # check how many hours are in the labour model
            hours = df_Labour_Model_Hours_filtered_3['Hour'].unique()
            # modify actuals to only get the missing hours
            df_Actuals_new_for_adding = df_Actuals_new_filtered_2[(df_Actuals_new_filtered_2['Day'] == day) & (~df_Actuals_new_filtered_2['Hour'].isin(hours))]
            # add the missing hours to the labour model
            start_hour = df_Actuals_new_for_adding['Hour'].min() if len(df_Actuals_new_for_adding['Hour'].unique()) > 0 else min(hours)
            end_hour = df_Actuals_new_for_adding['Hour'].max() if len(df_Actuals_new_for_adding['Hour'].unique()) > 0 else max(hours)
            for hour in range(start_hour, end_hour + 1):
                # if the hour is not in the labour model add it
                if hour not in hours:
                    site_code = restaurant
                    department = department
                    date = date
                    hour = hour
                    # set actual and budget and labour to average
                    row = df_Actuals_new_for_adding[df_Actuals_new_for_adding['Hour'] == hour]
                    average_from_row = row['Average'].values[0]
                    actuals = average_from_row
                    budget = average_from_row
                    labour_model_hours = average_from_row
                    day = day
                    month = pd.to_datetime(date).month
                    row = pd.DataFrame([[site_code, date, department, hour, actuals, budget, labour_model_hours,month, day]], columns=df_Labour_Model_Hours.columns)
                else:                   
                    row = df_Labour_Model_Hours_filtered_3[df_Labour_Model_Hours_filtered_3['Hour'] == hour]
                    site_code = restaurant
                    department = department
                    date = date
                    hour = hour
                    actual = row["Actual Hours '22"].values[0]
                    budget = row['Budget Rota Hours'].values[0]
                    labour_model_hours = row['Labour Model Hours'].values[0]
                    day = row['Day'].values[0]
                    month = pd.to_datetime(date).month
                    row = pd.DataFrame([[site_code, date, department,  hour, actual, budget, labour_model_hours, month, day]], columns=df_Labour_Model_Hours.columns)
                if day == 'Wednesday' and department == 'Expo' and res_name == 'Dishoom Kings Cross':
                   
                    # transform the day to string object
                    row['Day'] = row['Day'].astype(str)
                    st.write(row)
                    # for every element in row print(type)
                    st.write(row.dtypes)

                # add the row from the labour model
                empty_data_frame = pd.concat([empty_data_frame, row], axis=0)


# replace column day with month_ and month with day_
st.write(empty_data_frame)
# save as csv
empty_data_frame.to_csv('Labour_Model_Hours_w32_w43.csv', index=False)

