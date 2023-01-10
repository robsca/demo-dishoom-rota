import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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

guide()