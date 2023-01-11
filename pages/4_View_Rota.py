# IMPORTS
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from Esteban import Esteban_
from database import get_rota_data, delete_rota_data

max_hours = int(st.sidebar.number_input('Max hours', min_value=0, max_value=12, value=9))
min_hours = int(st.sidebar.number_input('Min hours', min_value=3, max_value=8, value=4))

@st.experimental_memo
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def rota_():
    def interface():
        # Create "Save" and "Delete" buttons
        c1,c2 = st.columns(2)
        save_button = c1.button('Save')
        delete_button = c2.button('Delete')

        if delete_button:
            st.success('Rota data deleted')
            # delete rota data
            delete_rota_data()

        if save_button:
            # merge all the days ina single dataframe
            empty_dataframe = pd.DataFrame(columns=['Site Code', 'Department', 'Month', 'Day', 'Start Time', 'End Time'])
            for i in rota_data:
                # add to dataframe
                empty_dataframe = pd.concat([empty_dataframe, pd.DataFrame({'Site Code': [i[0]], 'Department': [i[1]], 'Month': [i[2]], 'Day': [i[3]], 'Start Time': [i[4]], 'End Time': [i[5]]})], ignore_index=True)
            # add a zero to all the start times and end times
            # download the dataframe
            csv = convert_df(empty_dataframe)
            st.download_button(
            "download",
            csv,
            f"rota.csv",
            "text/csv",
            key='download-csv'
            )
            st.success('Press the download button to download the rota data')

        # create a empty dataframe with columns -> Site Code, Department, Day, Monday Start Time, Monday End Time, Tuesday Start Time, Tuesday End Time, Wednesday Start Time, Wednesday End Time, Thursday Start Time, Thursday End Time, Friday Start Time, Friday End Time, Saturday Start Time, Saturday End Time, Sunday Start Time, Sunday End Time
        empty_dataframe = pd.DataFrame(columns=['Site Code', 'Department', 'Day', 'Monday Start Time', 'Monday End Time', 'Tuesday Start Time', 'Tuesday End Time', 'Wednesday Start Time', 'Wednesday End Time', 'Thursday Start Time', 'Thursday End Time', 'Friday Start Time', 'Friday End Time', 'Saturday Start Time', 'Saturday End Time', 'Sunday Start Time', 'Sunday End Time'])
        for i in rota_data:
            day_for_col = i[3]
            empty_dataframe = pd.concat([empty_dataframe, pd.DataFrame({'Site Code': [i[0]], 'Department': [i[1]], 'Day': [i[3]], f'{day_for_col} Start Time': [i[4]], f'{day_for_col} End Time': [i[5]]})], ignore_index=True)
        
        # create a list of unique site codes, departments and days
        site_codes  = empty_dataframe['Site Code'].unique().tolist()  + ['All']
        departments = empty_dataframe['Department'].unique().tolist() + ['All']
        days        = empty_dataframe['Day'].unique().tolist()        + ['All']

        # create 3 columns with the UI filters
        c1,c2,c3   = st.columns(3)
        site_code  = c1.selectbox('Site Code', site_codes, index=0)
        department = c2.selectbox('Department', departments, index=0)
        day        = c3.selectbox('Day', days, index=0)

        # Handle the filters
        if site_code != 'All':
            empty_dataframe = empty_dataframe[empty_dataframe['Site Code'] == site_code]
        if department != 'All':
            empty_dataframe = empty_dataframe[empty_dataframe['Department'] == department]
        if day != 'All':
            empty_dataframe = empty_dataframe[empty_dataframe['Day'] == day]
        empty_dataframe = empty_dataframe.fillna(0) # instead of nan show 0
        st.write(empty_dataframe)

    try:
        rota_data = get_rota_data()
        empty_dataframe = pd.DataFrame(columns=['Site Code', 'Department', 'Day', 'Start Time', 'End Time'])
        for i in rota_data:
            # add to dataframe with pd.concat
            empty_dataframe = pd.concat([empty_dataframe, pd.DataFrame({'Site Code': [i[0]], 'Department': [i[1]], 'Day': [i[3]], 'Start Time': [i[4]], 'End Time': [i[5]]})], ignore_index=True)
        # modify format of start time and end time
        empty_dataframe['Start Time'] = empty_dataframe['Start Time'].apply(lambda x: str(x) + '0')
        empty_dataframe['End Time']   = empty_dataframe['End Time'].apply(lambda x: str(x) + '0')
        
        interface()
    except:
        st.warning('Please add rota data from **Edit Structure**')

if __name__ == '__main__':
    rota_()