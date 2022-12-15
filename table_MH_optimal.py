import pandas as pd
import streamlit as st
st.set_page_config(layout="wide")


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
# 

with st.expander('Show all data'):
    st.write(df)

# plot the data
import plotly.graph_objects as go
fig = go.Figure()
features = ['Labour Model Hours']
# plot them all
for feature in features:
    fig.add_trace(go.Bar(x=df['Date (DDMMYYYY)'], y=df[feature], name=feature))
fig.update_layout(title='Labour Model Hours', xaxis_title='day', yaxis_title='Hours')

# get unique day
# change format of date to date only
df['Date (DDMMYYYY)'] = df['Date (DDMMYYYY)'].apply(lambda x: x.split(' ')[0])
unique_day = df['Date (DDMMYYYY)'].unique()
day = st.sidebar.selectbox('Select a day', unique_day)
restaurant = st.sidebar.selectbox('Select a restaurant', df['Site Code'].unique())
department = st.sidebar.selectbox('Select a department', df['Department'].unique())

# get only the data for the selected day
df_day = df[df['Date (DDMMYYYY)'] == day]
# get only the data for the selected restaurant
df_restaurant = df_day[df_day['Site Code'] == restaurant]
# get only the data for the selected department
df_department = df_restaurant[df_restaurant['Department'] == department]
final = df_department

budget = final['Budget Rota Hours'].values.tolist()
constraint = final['Labour Model Hours'].values.tolist()
constraint = [int(i) for i in constraint]
# get all unique hours in that day
unique_hours = final['Hour'].unique()
# get the min 
open_time = min(unique_hours)

with st.expander('Show filtered data'):
    st.write('This is the data for the selected day, and department and restaurant')
    st.write(final)

# Rota Creator
@st.cache(allow_output_mutation=True)
class Esteban:
    def __init__(self, constraint):
        self.constraint = constraint

    def make_it_binary(self, constraint):
        '''
        make the constraint binary
        '''
        if not constraint:
            constraint = self.constraint
        else:
            constraint = constraint
        const_ = []
        for const in constraint:
            if const >=0:
                const = 1
            else:
                const = 0
            const_.append(const)
        return const_

    def populate_layer_1(self, layer):
        '''
        Take every layer and divide it into groups
        retur a list of groups
        '''
        layer_full = True if sum(layer) == len(layer) else False
        if layer_full:
            groups = []
            #st.write('This layer is full')
            # start == index of the first 1
            indexes_of_ones = [i for i, x in enumerate(layer) if x == 1]
            groups.append(indexes_of_ones)
            # choose random length
        else:
            # get the index of all zeros
            indexes_of_zeros = [i for i, x in enumerate(layer) if x == 0]
            # get the index of all ones
            indexes_of_ones = [i for i, x in enumerate(layer) if x == 1]
            start = indexes_of_ones[0]
            groups = []
            group = []
            for i, element in enumerate(indexes_of_ones):
                if i < len(indexes_of_ones)-1:
                    if indexes_of_ones[i+1] == element+1:
                        group.append(element)
                    else:
                        group.append(element)
                        groups.append(group)
                        group = []
                else:
                    group.append(element)
                    groups.append(group)  
        return groups

    def random_splitter(self, group, len_shifts):
        '''
        This is the core of the problem
        '''
        import random
        shifts = []
        hours_to_cover = len(group) 
        while hours_to_cover > 0:
            len_shift = random.choice(len_shifts)
            if hours_to_cover >= len_shift:
                shift = [group[0], group[0]+len_shift]
                shifts.append(shift)
                group = group[len_shift:]
                hours_to_cover -= len_shift
            else:
                shift = [group[0], group[0] + hours_to_cover]
                shifts.append(shift)
                hours_to_cover = 0


        copy_of_shifts = shifts.copy()
        shifts_ok = []
        shift_to_review = []

        for shift in copy_of_shifts:
            if shift[1] - shift[0] not in len_shifts: # if the shift is not in the allowed lengths
                shift_to_review.append(shift)
            else:
                shifts_ok.append(shift)

        # now merge the ok shifts with the shift to review
        if len(shift_to_review) > 0:
            for shift in shifts_ok:
                start = shift[0]
                end = shift[1]
                # get all the starting times of the shift to review
                starts_to_review = [i[0] for i in shift_to_review]

                if end in starts_to_review:
                    # get the shifts that needs to be merges
                    index_end = starts_to_review.index(end)
                    shift_to_merge = shift_to_review[index_end]
                    # create a new shift
                    new_shift = [start, shift_to_merge[1]]
                    # remove shift from the list of shifts
                    shifts_ok.remove(shift)
                    shifts_ok.append(new_shift)
                
        return shifts_ok
        
    def populate_layer_2(self, groups, min_hours, max_hours):
        '''
        Take the group and transform it into shifts
        '''
        lenghts_allowed = [i for i in range(int(min_hours), int(max_hours)+1)]
        shifts = []
        
        for group in groups:
            #st.write('Transform this group into a series of shifts: ')
            #st.write(group)
            shifts_ = self.random_splitter(group, lenghts_allowed)
            for shift in shifts_:
                shifts.append(shift)

        return shifts

    def process_rota(self, shifts):
        '''
        take all the shifts and create a hour by hour totals array for plotting
        '''
        rota = []
        for shift in shifts:
            hours = [i for i in range(shift[0], shift[1])]
            rota.extend(hours)
        unique_hours = list(set(rota))
        unique_hours.sort()
        # count the number of hours per day
        rota = [rota.count(i) for i in unique_hours]
        return rota

    def solving_(self, open_time, min_hours, max_hours):
        '''
        create a layer structure for the problem
        '''
        stop = [-1 for i in range(len(self.constraint))]
        new_constraint = constraint.copy()
        layers = []
        while max(new_constraint) != 0:
            new_constraint = [element-1 for element in new_constraint]
            constraint_layer = self.make_it_binary(new_constraint)
            layers.append(constraint_layer)

        # obtain all the groups to transform in shifts
        groups = []
        shift_to_add_later = []
        for i, layer in enumerate(layers):
            print('layer: ', i)
            print(layer)
            print('----------------')
            if len(layer) > 0:
                group_in_layer = self.populate_layer_1(layer)
                print('group in layer: ', group_in_layer)
                for group in group_in_layer:
                    print('group: ', group)
                    if len(group) < 4:
                        print('This group is too short')
                        print(f'group: {group}')
                        print('----------------')
                        shift_to_add_later.append(group)

                print('----------------')
                groups.extend(group_in_layer)
            else:
                print('This layer is too short to be processed')
                shift_to_add_later.append(layer)

        shifts = self.populate_layer_2(groups, min_hours, max_hours)
        # process the shifts to align with open and close time
        shifts = [[shift[0]+open_time, shift[1]+open_time] for shift in shifts]
        ''''''
        # for all the shift to add later add a shift of min hours at the center
        with st.expander('This are the shift that need adjustments'):
            st.write("Currently it's been add a shift of min length at the first available moment.")
            for shift in shift_to_add_later:
                st.write(shift)
                if len(shift) > 0:
                    shift = [shift[0]+open_time, shift[0]+open_time+min_hours]
                    shifts.append(shift)
                


        rota = self.process_rota(shifts)   
        return rota, shifts

    import pandas as pd
    import plotly.graph_objects as go


def main(constraint, open_time, budget):
    # get the data from the user
    if st.checkbox('Solve the problem'):
        with st.sidebar:
            st.title('Rota Generator')
            #open_time = int(st.number_input('Enter the open time', min_value=0, max_value=23, value=8))
            # set open time to min(Hours)
            open_time = open_time
            min_hours = int(st.number_input('Enter the min hours', min_value=1, max_value=23, value=4))
            max_hours = int(st.number_input('Enter the max hours', min_value=1, max_value=23, value=8))

        # solve the problem
        esteban = Esteban(constraint)
        rota, shifts = esteban.solving_(open_time, min_hours, max_hours)
        shifts = pd.DataFrame(shifts, columns=['start', 'end'])

        # create graph
        fig = go.Figure()
        # add generated rota
        fig.add_trace(go.Bar(x=[i+open_time for i in range(len(rota))], y=rota, name='Generated Rota : Algorithm'))
        # add contrsaint
        fig.add_trace(go.Bar(x=[i+open_time for i in range(len(constraint))], y=constraint, name='Labour Model Hours'))        
        # add budget
        fig.add_trace(go.Scatter(x=[i+open_time for i in range(len(constraint))], y=budget, name='Budget Hours'))
        
        # show the graph
        st.plotly_chart(fig, use_container_width=True)
        
        # start analysis of shifts
        st.title('Shifts Analysis')
        st.write('This section is still under development')
        # add a columns with the index
        shifts['index'] = shifts.index
        # modify column 
        shifts['index'] = shifts['index'].apply(lambda x: f'Server :  {x}')
        # set as index 
        shifts.set_index('index', inplace=True)
        # add a column to the shifts dataframe
        shifts['length'] = shifts['end'] - shifts['start']
        # add a column for the cost of labour
        shifts['cost'] = shifts['length'] * 9.50

        with st.expander('Shifts Analysis'):
            c1,c2 = st.columns(2)
            c1.dataframe(shifts)
            with c2:
                # calculate the total cost
                total_cost = shifts['cost'].sum()
                st.write(f'Total cost: £{total_cost}')
                total_hours = shifts['length'].sum()
                st.write(f'Total hours Generated: {total_hours} hours')
                # get total hours in constraint
                total_hours_constraint = sum(constraint)
                st.write(f'Total hours needed: {total_hours_constraint} hours')
                # get difference
                difference = total_hours_constraint - total_hours
                st.write(f'Difference: {difference} hours')
                # get difference in cost
                difference_cost = difference * 9.50
                st.write(f'Difference in cost: £{difference_cost}')
                # difference in percentage num
                difference_percentage = (difference / total_hours_constraint) * 100
                st.write(f'Difference in percentage: {round(difference_percentage, 2)}%')
                if st.button('Save shifts as csv'):
                    shifts.to_csv('shifts.csv')
                    st.write('Done!')
                return shifts

def shift_adjustments():
    # open csv file
    import os
    if os.path.exists('shifts.csv'):
        shifts = pd.read_csv('shifts.csv')

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
        with st.expander('Shifts Adjustments'):
            c1, c2 = st.columns(2)
            with c1:
                sliders = []
                # get hour max
                hour_max = shifts['end'].max()
                for index, row in shifts.iterrows():
                    # create a slider for each row
                    st.write(f'{index} : {row["start"]} - {row["end"]}')
                    sl = st.slider('',min_value=int(open_time), max_value=int(hour_max), value=(int(row['start']), int(row['end'])), key=index)
                    if validity_shift_checker(sl):
                        sliders.append(sl)

            # create a new dataframe with the sliders
            new_shifts = pd.DataFrame(sliders, columns=['start', 'end'])
            # add the index
            new_shifts['index'] = new_shifts.index
            # modify column
            new_shifts['index'] = new_shifts['index'].apply(lambda x: f'Server :  {x}')
            # set as index
            new_shifts.set_index('index', inplace=True)
            # add a column to the shifts dataframe
            new_shifts['length'] = new_shifts['end'] - new_shifts['start']
            # add a column for the cost of labour
            new_shifts['cost'] = new_shifts['length'] * 9.50
            # show the new shifts
            c2.write(new_shifts)
            hours = []
            # iterate through the new shifts
            for index, row in new_shifts.iterrows():
                shift = [i for i in range(int(row['start']), int(row['end']))]
                hours.extend(shift)
            # count occurences
            # import counter
            from collections import Counter
            occurences = Counter(hours)
            #st.write(occurences)
            # plot the occurences
            fig = go.Figure()
            fig.add_trace(go.Bar(x=list(occurences.keys()), y=list(occurences.values())))
            # add labour model
            fig.add_trace(go.Bar(x=[
                i+open_time for i in range(len(constraint))], y=constraint, name='Labour Model Hours'))
            # add budget
            fig.add_trace(go.Scatter
                            (x=[i+open_time for i in range(len(constraint))], y=budget, name='Budget Hours'))
            # show the graph

            c2.plotly_chart(fig, use_container_width=True)

            return new_shifts


if __name__ == '__main__':
    shifts = main(constraint, open_time, budget)
    new_shifts = shift_adjustments()

