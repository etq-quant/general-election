import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(
    page_title="General Election",
    layout="wide",
)
st.title("General Election")
DATA_PATH='notebooks/GE_sdata.csv'

@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df[~df['state'].isin(['Sarawak', 'Sabah'])]
    return df

df = load_data()

my_expander = st.expander(label='Turnout',expanded=True)
with my_expander:
    col1, col2 = st.columns(2)
    malay_turnout = col1.slider('Malay turnout', 0, 100, 80)
    non_malay_turnout = col2.slider('non-Malay turnout', 0, 100, 80)


my_expander = st.expander(label='BN',expanded=True)
with my_expander:
    #st.header("BN")
    BN_col1, BN_col2 = st.columns(2)
    BN_MS = BN_col1.slider('BN Malay Support', 0, 100, 40)
    BN_nMS = BN_col2.slider('BN non-Malay Support', 0, 100, 20)

my_expander = st.expander(label='PH',expanded=True)
with my_expander:
    #st.header("PH")
    PH_col1, PH_col2 = st.columns(2)
    PH_MS = PH_col1.slider('PH Malay Support', 0, 100, 25)
    PH_nMS = PH_col2.slider('PH non-Malay Support', 0, 100, 50)

my_expander = st.expander(label='PN',expanded=True)
with my_expander:
    #st.header("PN")
    PN_col1, PN_col2 = st.columns(2)
    PN_MS = PN_col1.slider('PN Malay Support', 0, 100, 30)
    PN_nMS = PN_col2.slider('PN non-Malay Support', 0, 100, 15)


df['BN'] = df['malay_voter_ratio']*BN_MS*malay_turnout + df['non_malay_voter_ratio']*BN_nMS*non_malay_turnout
df['PH'] = df['malay_voter_ratio']*PH_MS*malay_turnout + df['non_malay_voter_ratio']*PH_nMS*non_malay_turnout
df['PN'] = df['malay_voter_ratio']*PN_MS*malay_turnout + df['non_malay_voter_ratio']*PN_nMS*non_malay_turnout
df['estimated'] = df[['BN','PH','PN']].idxmax(axis=1)

def get_base(a,b):

    if a=='PR-PAS' and b=='GS-PAS':
        return 'PN'
    a = a.split('-')[0]
    b = b.split('-')[0]
    
    if a==b=='BN':
        return 'BN'
    elif a=='PR' and b=='PH':
        return 'PH'
    else:
        return None

df['base'] = df.apply(lambda x: get_base(x['2013'], x['2018']), axis=1)    
df['party'] = df['base'].fillna(df['estimated'])

data = {'BN': '#2B65EC', 'PH': '#E41B17', 'PN': '#659EC7'}
def highlight_party(val):
    return 'background-color: {}'.format(data.get(val))

#st.bar_chart(df.groupby(['party']).size())


sdf = df.groupby(['party']).size().reset_index().rename(columns={0: 'seats'})
sdf['color'] = df['party'].map(data)
chart = (
    alt.Chart(sdf, title='Expected Result')
    .mark_bar()
    .encode(
        alt.X("party"),
        alt.Y('seats'),
        alt.Color("party", scale=alt.Scale(domain=list(data.keys()), range=list(data.values()))),
        alt.Tooltip(["party", "seats"]),
    )
)

text = chart.mark_text(
    align='center',
    baseline='bottom',
    fontSize=24,
    # dy=50,
    # dx=50,
    color='black',
).encode(
    alt.Text('seats')
)

chart = (chart+text).properties(height=400).configure_title(fontSize=24).configure_axis(
    labelFontSize = 24,
    titleFontSize = 26)

st.altair_chart(chart, use_container_width=True)

cols = ['state', 'constituency_s', '2004', '2008', '2013', '2018', 'malay_voter_ratio', 'non_malay_voter_ratio', 'party']
st.dataframe(df.set_index('##')[cols].style.applymap(highlight_party, subset=['party']),
    use_container_width=True)

# ColorMinMax = st.markdown(''' <style> div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
#     background: rgb(1 1 1 / 0%); } </style>''', unsafe_allow_html = True)


# Slider_Cursor = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{
#     background-color: rgb(14, 38, 74); box-shadow: rgb(14 38 74 / 20%) 0px 0px 0px 0.2rem;} </style>''', unsafe_allow_html = True)

    
# Slider_Number = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div > div
#                                 { color: rgb(14, 38, 74); } </style>''', unsafe_allow_html = True)
    

# col = f''' <style> div.stSlider > div[data-baseweb = "slider"] > div > div {{
#     background: linear-gradient(to right, rgb(1, 183, 158) 0%, 
#                                 #2B65EC {BN_MS}% , 
#                                 #2B65EC {BN_MS}% , 
#                                }} </style>'''

# ColorSlider = st.markdown(col, unsafe_allow_html = True)  