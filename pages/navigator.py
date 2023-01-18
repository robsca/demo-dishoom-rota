import streamlit as st
import pandas as pd

# open csv file
path = "Labour_Model_Hours_D6.csv"

# first dataframe
df_d6 = pd.read_csv(path)
# keep only budget hours
features = ['Site Code','Date (DDMMYYYY)','Department','Hour','Budget Rota Hours' ]
d6_only_budget = df_d6[features]
st.write('Correct Dataframe')
st.write(d6_only_budget)
st.write(len(d6_only_budget))

# Second Dataframe
path_all_res = "Labour_Model_Hours_w32_w43.csv"
df_all_res = pd.read_csv(path_all_res)
# keep only D6
d6_only = df_all_res[df_all_res['Site Code'] == 'D6']
st.write('Incorrect Dataframe need to add budget hours')
st.write(d6_only)
st.write(len(d6_only))
# take off budget rota hour column
d6_only = d6_only.drop(columns=['Budget Rota Hours'])
st.write('Incorrect Dataframe need to add budget hours')
# add the budget rota hours column
d6_only = d6_only.merge(d6_only_budget, on=['Site Code','Date (DDMMYYYY)','Department','Hour'])
st.write(d6_only)

# combine the two dataframes
# drop the d6 from res all 
df_all_res = df_all_res[df_all_res['Site Code'] != 'D6']
# now I can concat the two dataframes
df_all_res = pd.concat([df_all_res, d6_only])
st.write('Combined Dataframe')
# transform budget in float
df_all_res['Budget Rota Hours'] = df_all_res['Budget Rota Hours'].astype(float)

st.write(df_all_res)

# save as csv
#df_all_res.to_csv('Labour_Model_Hours_alls.csv', index=False)