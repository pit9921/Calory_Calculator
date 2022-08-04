#!/usr/bin/env python
# coding: utf-8
# %%
import streamlit as st  
import pandas as pd
import datetime
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

sheet_url = "https://docs.google.com/spreadsheets/d/1S_NB-vJcidtM2m_-2ZAavolLc-S8gFil0vj5s7vZZGo/edit#gid=0"

url_1 = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
df = pd.read_csv(url_1, error_bad_lines=False, decimal=',')
#df.head(n=3)


# %%
# Fill NaN values in dataframe with previous values in column
df['Datum'].fillna(method='ffill', inplace=True)

# %%
sheet_url = "https://docs.google.com/spreadsheets/d/1S_NB-vJcidtM2m_-2ZAavolLc-S8gFil0vj5s7vZZGo/edit#gid=1596053915"

url_2 = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
df1 = pd.read_csv(url_2, error_bad_lines=False, decimal=',')
#df1.head(n=3)


# %%
df['Kalorien'] = (df['Menge'] / (df['Produkt'].map(dict(zip(df1['Produkt'], df1['Referenz']))).fillna(0))) * df['Produkt'].map(dict(zip(df1['Produkt'], df1['Kalorien']))).fillna(0)
df['Fett'] = (df['Menge'] / (df['Produkt'].map(dict(zip(df1['Produkt'], df1['Referenz']))).fillna(0))) * df['Produkt'].map(dict(zip(df1['Produkt'], df1['Fett']))).fillna(0)
df['Kohlehydrate'] = (df['Menge'] / (df['Produkt'].map(dict(zip(df1['Produkt'], df1['Referenz']))).fillna(0))) * df['Produkt'].map(dict(zip(df1['Produkt'], df1['Kohlehydrate']))).fillna(0)
df['Zucker'] = (df['Menge'] / (df['Produkt'].map(dict(zip(df1['Produkt'], df1['Referenz']))).fillna(0))) * df['Produkt'].map(dict(zip(df1['Produkt'], df1['Zucker']))).fillna(0)
df['Protein'] = (df['Menge'] / (df['Produkt'].map(dict(zip(df1['Produkt'], df1['Referenz']))).fillna(0))) * df['Produkt'].map(dict(zip(df1['Produkt'], df1['Protein']))).fillna(0)


# %%
filtered_df = df[df['Kalorien'].isnull()]

# %%
filtered_df1 = df.loc[(df['Kalorien'] == 0)]

# %%
df['Datum_date'] = pd.to_datetime(df['Datum'], dayfirst=True)
df['Tag'] = df[['Datum_date']].apply(lambda x: dt.datetime.strftime(x['Datum_date'], '%A'), axis=1)


# %%
df.loc[df['Tag'] == "Sunday", 'Tag1'] = "Wochenende"
df.loc[df['Tag'] == "Saturday", 'Tag1'] = "Wochenende"
df.loc[df['Tag'] == "Monday", 'Tag1'] = "Arbeitstag"
df.loc[df['Tag'] == "Tuesday", 'Tag1'] = "Arbeitstag"
df.loc[df['Tag'] == "Wednesday", 'Tag1'] = "Arbeitstag"
df.loc[df['Tag'] == "Thursday", 'Tag1'] = "Arbeitstag"
df.loc[df['Tag'] == "Friday", 'Tag1'] = "Arbeitstag"


# %%
df_grouped = df.groupby(['Datum_date']).sum()
df_grouped = df_grouped.reset_index(level=0)
del df_grouped['Menge']
#df_grouped


# %%
#delta = df_grouped['Kalorien'].mean() - df_grouped["Kalorien"].iloc[-1]

calorien_limit = 2300
delta = calorien_limit - df_grouped["Kalorien"].iloc[-1]
#delta


# %%
# get a list of calories per day per mahlzeit
df_grouped1 = df.groupby(['Datum_date','Mahlzeit'],as_index=False).agg({'Kalorien':'sum'})

# find the closest meal to the delta
pos = df_grouped1['Kalorien'].sub(delta).abs().values.argmin()
df_grouped2 = df_grouped1.loc[[pos]]

day1 = df_grouped2["Datum_date"].iloc[-1]
Mahlzeit1 = df_grouped2["Mahlzeit"].iloc[-1]

first_meal = df[(df['Datum_date']==day1) & (df['Mahlzeit']==Mahlzeit1)]
first_meal = first_meal[['Produkt','Menge']]


# %%
if delta < 0:
    first_meal = df[(df['Datum_date']=='day1') & (df['Mahlzeit']==Mahlzeit1)]
    first_meal = first_meal[['Produkt','Menge']]

    fig_tabelle = go.Figure(data=[go.Table(
        header=dict(values=list(first_meal.columns),
                    fill_color='#a6a6a6',
                    font=dict(color='white', size=18),
                    align='left'),
        cells=dict(values=[first_meal.Produkt, first_meal.Menge],
                   fill_color='white',
                   font=dict(color='#a6a6a6', size=14),               
                   align='left'))
    ])

    #fig_tabelle.show()

else:

    fig_tabelle = go.Figure(data=[go.Table(
        header=dict(values=list(first_meal.columns),
                    fill_color='#a6a6a6',
                    font=dict(color='white', size=18),
                    align='left'),
        cells=dict(values=[first_meal.Produkt, first_meal.Menge],
                   fill_color='white',
                   font=dict(color='#a6a6a6', size=14),               
                   align='left'))
    ])

    #fig_tabelle.show()


# %%
today_date = df["Datum"].iloc[-1]
today_data = df[(df['Datum']==today_date)]

today_data = today_data.round(1)

# values with "gram"
today_data1 = pd.concat([today_data,pd.DataFrame(today_data.sum(axis=0),columns=['Grand Total']).T])
today_data1 = today_data1[['Fett','Kohlehydrate','Protein']]
today_data1 = today_data1.tail(1)
today_data1 = today_data1.astype(str).apply(lambda x: x.replace('.0',''))
today_data1["Fett"] = pd.to_numeric(today_data1["Fett"])
today_data1["Kohlehydrate"] = pd.to_numeric(today_data1["Kohlehydrate"])
today_data1["Protein"] = pd.to_numeric(today_data1["Protein"])
today_data1['Fett'] = today_data1['Fett'].round(decimals = 1)
today_data1['Kohlehydrate'] = today_data1['Kohlehydrate'].round(decimals = 1)
today_data1['Protein'] = today_data1['Protein'].round(decimals = 1)
today_data1['Fett'] = today_data1['Fett'].astype(str) + 'g'
today_data1['Kohlehydrate'] = today_data1['Kohlehydrate'].astype(str) + 'g'
today_data1['Protein'] = today_data1['Protein'].astype(str) + 'g'
Fett = today_data1['Fett'].iloc[0]
Kohlehydrate = today_data1['Kohlehydrate'].iloc[0]
Protein = today_data1['Protein'].iloc[0]
list = [Fett, Kohlehydrate, Protein]


Total_protein = today_data['Protein'].sum()


labels = ['Fett','Carb','Protein']
values = [today_data['Fett'].sum(), today_data['Kohlehydrate'].sum(), today_data['Protein'].sum()]
colors = ['#f8be6a', '#60bbce', '#5d64bf', '#fa8126', '#3b7eb5', '#a6a6a6']

# Use `hole` to create a donut-like pie chart
fig = go.Figure(data=[go.Pie(labels=labels, values=values, text=list, textinfo='label+percent+text', pull=[0.01, 0.01, 0.05],
                             rotation=125,
                             insidetextorientation='horizontal', hole=.55)])

fig.update_traces(hoverinfo='label+percent+text', textfont_size=12,
                  marker=dict(colors=colors))

#fig.update_layout(showlegend=False)

fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-0.25,
    xanchor="center",
    x=0.5
))

fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))


if Total_protein>130:
    fig.update_layout(
        # Add annotations in the center of the donut pies.
        annotations=[dict(text='Proteine OK', x=0.5, y=0.52, font_size=20, font_color="#5d64bf", showarrow=False),
                    dict(text='Referenz: 130g', x=0.5, y=0.46, font_size=14, font_color="#5d64bf", showarrow=False)])
else:
    fig.update_layout(
        # Add annotations in the center of the donut pies.
        annotations=[dict(text='Zu wenig Proteine', x=0.5, y=0.52, font_size=20, font_color="#5d64bf", showarrow=False),
                    dict(text='Referenz: 130g', x=0.5, y=0.46, font_size=14, font_color="#5d64bf", showarrow=False)])    

#fig.show()

# %%
# ---- MAINPAGE ----



st.set_page_config(
    page_title="Kalorienverbrauch App",
    page_icon="✅",
    layout="wide",
)


# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-bottom: 3.5rem;
                }
        </style>
        """, unsafe_allow_html=True)


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



st.title(":pizza: Kalorienverbrauch")
st.markdown("""---""") 
#st.markdown("##")



######### Hide row indices with st.table #######################
# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)
#################################################################

#st.subheader("Fehlende Eingaben:")

if filtered_df.empty:
#    st.write("Alle Mahlzeiten in der DB erhalten.  \n Angezeigte Ergebnisse sind relevant.")
    st.success('Alle Mahlzeiten in der DB erhalten.  \n Angezeigte **Ergebnisse** sind **relevant!**')
else:
    st.error("Folgende Gerichte **müssen** noch vor der Auswertung in der Datenbank **gepflegt werden!**")
    st.table(filtered_df)

st.markdown("#")


# Row B
b1, b2, b3 = st.columns(3)
b1.metric("Datum", df["Datum"].iloc[-1])
b2.metric("Kalorien am Tag (Soll: 2300kcal)", round(df_grouped["Kalorien"].iloc[-1]))

if delta < 0:
    b3.metric("Übrige Kalorien", abs(round(delta)))   # noch oder zu viel

else:
    b3.metric("Noch zunehmende Kalorien", round(delta))   # noch oder zu viel

# create blank space between objects
st.markdown('#')   

st.plotly_chart(fig, use_container_width=True)

st.markdown('#')  

st.subheader("Empfohlene Mahlzeit")

# Empfohlene Mahlzeit..
if first_meal.empty:
#    st.write("Kalorienverbrauch überschreitet.  \nAn diesem Tag **nicht mehr** konsumieren.")
    st.error("Kalorienverbrauch überschreitet.  \nAn diesem Tag **nicht mehr** konsumieren.")
else:
    st.success('Folgende Mahlzeit darf heute noch aufgenommen werden (basierend auf Kalorien).')
    st.table(first_meal)


# Remove “Made with Streamlit” from bottom of app
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


# %%
