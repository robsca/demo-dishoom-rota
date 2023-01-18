import streamlit as st
import pandas as pd

# open csv file
path = "Labour_Model_Hours_D6.csv"
path_all_res = "Labour_Model_Hours_w32_w43.csv"

# read csv file
df = pd.read_csv(path)
df_all_res = pd.read_csv(path_all_res)
# take off d6
df_all_res = df_all_res[df_all_res['Department'] != 'D6']

st.write(df)
st.write(df_all_res)

# concatenate the two dataframes
df = pd.concat([df, df_all_res], axis=0)
# all nan values to 0
#add dayname
df['Day'] = pd.to_datetime(df['Date (DDMMYYYY)']).dt.day_name()
df = df.fillna(0)

st.write(df)

# save as csv file

df.to_csv('Labour_Model_Hours_all.csv', index=False)