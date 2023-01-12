import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import plotly.graph_objects as go
from Esteban import Esteban_
from database import get_data, get_shift_data, delete_rota_data_same_day, insert_rota_data

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Week Rota']
day_ = st.sidebar.selectbox('Day', days, index=len(days)-1)
max_hours = int(st.sidebar.number_input('Max hours', min_value=0, max_value=12, value=9))
min_hours = int(st.sidebar.number_input('Min hours', min_value=3, max_value=8, value=4))

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

def handle_one_day(d, constraints_table, shifts_table):
    constraints_table_, shifts_table_  = [i for i in constraints_table if i[3] == d] , [i for i in shifts_table if i[3] == d]
    #--------------------------------------------
    try:
        with st.expander(f'{d}'): # create an expander for each day
            day = d
            month = constraints_table_[0][4]
            site_code = constraints_table_[0][0]
            constraints, budget, actuals, hours = [], [], [], []
            for i, constraint in enumerate(constraints_table_):
                constraints.append(int(constraint[-1]))
                budget.append(int(constraint[-2]))
                actuals.append(int(constraint[-3]))
                hours.append(int(constraint[2]))
                department = constraint[1]
            open_time = min(hours)
            open_time_for_slider = 5
            st.subheader(f'**Department**: {department}')
            st.write(f'**Site Code**: {site_code}')
            st.write(f'**Day**: {day}')
            st.write('---')

            # Create a dataframe with the shifts
            shifts = pd.DataFrame(columns=['Employees','Start', 'End'])
            for i, shift in enumerate(shifts_table_):
                employee = i
                start = int(float(shift[-2]))
                end = int(float(shift[-1]))
                shifts = pd.concat([shifts, pd.DataFrame([[employee, start, end]], columns=['Employees','Start', 'End'])], ignore_index=True)

            # create a slider view of the shifts
            #-----------------  C1 ------------------------------#-----------------------   C2   --------------------------#
            #----------------------------------------------------#---------------------------------------------------------#
            # EMP1 0====================0----------------0            | Graphical representation of the shifts             |
            # EMP2 0---0=================0---------------0            | -------------------------7-------------------------|
            # EMP3 0------0================0-------------0            | --------------------6--------6---------------------|
            # EMP4 0---------0================0----------0            | -----------------5---------------5-----------------|
            # EMP5 0------------0================0-------0            | --------------4--------------------4---------------|
            # EMP6 0---------------0================0----0            | -----------3--------------------------3------------|
            # EMP7 0------------------0================0-0            | --------2--------------------------------2---------|
            # EMP8 0---------------------0===============0            | -----1--------------------------------------1------|
            #--------------------------------------------------------------------------------------------------------------#

            c1, c2 = st.columns(2)
            with c1:
                # Creating the slider, so I need: min: , max, value, step, key
                sliders = []
                # get hour max
                max_value, min_value = int(shifts['End'].max()), int(open_time)
                for index, row in shifts.iterrows():
                    st.write(f'**{department} - {index+1}** : {row["Start"]} - {row["End"]}')
                    key = f'{department} - {index+1} - {row["Start"]} - {row["End"]} - {d}' # key for the slider
                    value = (int(row['Start']), int(row['End']))                                   # value for the slider
                    sl = st.slider(f'{index}', min_value=open_time_for_slider, max_value=max_value, value=value, key=key) # create the slider
                    
                    #'''MERGE BUTTON'''
                    # merge button
                    # find the mergable shifts
                    # iterate through the shifts and find the ones that start at the end of the current shift
                    mergable_shifts = []
                    for i, row_ in shifts.iterrows():
                        if row_['Start'] == row['End']:
                            shist_as_tuple = (row_['Start'], row_['End'])
                            mergable_shifts.append(shist_as_tuple)
                    # add no merge option
                    mergable_shifts.append('No merge')
                    # select the shift to merge
                    shift_to_merge = st.selectbox('Select shift to merge', mergable_shifts, index=len(mergable_shifts)-1, key=f'{key} - merge')
                    # if the user selects a shift to merge
                    if shift_to_merge != 'No merge':
                        # update the shifts table
                        shifts.loc[index, 'End'] = shift_to_merge[1]
                        # eliminate the shift that was merged
                        shifts = shifts[shifts['Start'] != shift_to_merge[0]]
                        # update the slider
                        sl = (sl[0], shift_to_merge[1])
                        print('This is the slider: ',sl)
                        # update the shift table
                        shifts.loc[index, 'End'] = sl[1]
                    #'''Still Experimenting with Merge Button: IN PROGRESS'''
                    if validity_shift_checker(sl, min_hours=min_hours, max_hours=max_hours):
                        sliders.append(sl)
            
            # Create the final shifts dataframe
            new_shifts = pd.DataFrame(sliders, columns=['Start', 'End']); 
            # Modify the index column to create a column of employee-n
            new_shifts['index'] = new_shifts.index; new_shifts['index'] = new_shifts['index'].apply(lambda x: f'{department} :  {x}' + ' ' *25)
            new_shifts.set_index('index', inplace=True)
            # add a column to the shifts dataframe
            new_shifts['length'] = new_shifts['End'] - new_shifts['Start']; new_shifts['cost'] = new_shifts['length'] * 9.50
            hours = [i for index, row in new_shifts.iterrows() for i in range(int(row['Start']), int(row['End']))]


            # import counter
            from collections import Counter
            occurences = Counter(hours)

            # Create the plot
            fig = go.Figure()
            # add labour model
            fig.add_trace(go.Bar(x=list(occurences.keys()), y=constraints, name='Labour Model Hours'))
            # add generated rota
            fig.add_trace(go.Bar(x=list(occurences.keys()), y=list(occurences.values()), name='Generated Rota Hours'))
            # add budget
            fig.add_trace(go.Scatter(x=sorted(list(occurences.keys())), y=budget, name='Budget'))

            c2.plotly_chart(fig, use_container_width=True)
            c2.write(new_shifts)

            with c2: # SAVE BUTTON 
                # SAVE All button
                if st.button('Save', key=f'{department} : {d}'):
                    st.write('Saving')
                    # delete rota data of the same day
                    delete_rota_data_same_day(day, department, site_code)
                    # save rota to database
                    for index, row in new_shifts.iterrows():
                        insert_rota_data(site_code, department, month, day, row['Start'], row['End'])

    except:
        pass

def shift_adjustments():
    global validity_shift_checker
    # 1. Get the data from the database
    constraints_table = get_data() # get the constraints
    shifts_table = get_shift_data() # get the shifts

    if day_ == 'Week Rota':
        for d in days: # iterate through the days
            handle_one_day(d, constraints_table, shifts_table)
    else:
        handle_one_day(day_, constraints_table, shifts_table)
    
shift_adjustments()