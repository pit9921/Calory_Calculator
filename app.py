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
df['gesätt Fett'] = (df['Menge'] / (df['Produkt'].map(dict(zip(df1['Produkt'], df1['Referenz']))).fillna(0))) * df['Produkt'].map(dict(zip(df1['Produkt'], df1['gesätt Fett']))).fillna(0)
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

calorien_limit = 2879
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

Total_Kalorien= today_data['Kalorien'].sum()
total_kal_per = ((Total_Kalorien / 2879 ) * 100).round(1)


labels = ['Kalorien', 'noch aufnehmen']
values = [Total_Kalorien, (2879 -Total_Kalorien) ]
colors = ['#a6a6a6', '#f6f6f6']

# Use `hole` to create a donut-like pie chart
fig = go.Figure(data=[go.Pie(labels=labels, values=values, direction='clockwise', sort=False,
                             rotation=180, hole=.7)])

fig.update_traces(hoverinfo='label', textfont_size=12,
                  marker=dict(colors=colors))


fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
fig.update_traces(textinfo='none')

fig.update_layout(
        # Add annotations in the center of the donut pies.
        annotations=[dict(text=str(total_kal_per) + "%", x=0.5, y=0.52, font_size=40, font_color="#5d64bf", showarrow=False),
                    dict(text=str(Total_Kalorien) + " kcal", x=0.5, y=0.46, font_size=14, font_color="#5d64bf", showarrow=False)])

fig.update_layout(showlegend=False)

#fig.show()

# %%
# Weight
sheet_url = "https://docs.google.com/spreadsheets/d/1S_NB-vJcidtM2m_-2ZAavolLc-S8gFil0vj5s7vZZGo/edit#gid=1161092296"

url_3 = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
df5 = pd.read_csv(url_3, error_bad_lines=False, decimal=',')
df6 = df5.loc[df5['Tätigkeit'] == "Gewicht"]

fig1 = px.line(df6, x="Datum", y="Wert", markers=True, template="xgridoff", line_shape='spline')

fig1.update_traces( line=dict(color="#f8be6a"))
fig1.update_layout(title_text='Gewicht - Regelkarte', title_x=0.05)


fig1.update_layout(yaxis_title="Gewicht [kg]")

fig1.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})

fig1.update_layout(
    font_color="#a6a6a6",
    title_font_color="#a6a6a6",
    legend_title_font_color="#a6a6a6"
)

# %%
Total_Protein = today_data['Protein'].sum()
Total_Kohlehydrate = today_data['Kohlehydrate'].sum()
Total_Fett = today_data['Fett'].sum()
Soll_Protein = 211 
Soll_Kohlehydrate = 281 
Soll_Fett = 93

# %%
# create df of aggregation
data = [['Protein', Total_Protein, Soll_Protein], ['Carb', Total_Kohlehydrate, Soll_Kohlehydrate], ['Fett', Total_Fett, Soll_Fett]]
df6 = pd.DataFrame(data, columns=['Macro', 'Ist', 'Soll'])
df6['utilization'] = ((df6['Ist'] / df6['Soll'] )*100).round(1)
df6['utilization'] = df6['utilization'].astype(str) + '%'

# %%
from plotly.subplots import make_subplots
fig3 = make_subplots(shared_yaxes=True, shared_xaxes=True)
fig3.add_bar(y=df6['Macro'],x=df6['Soll'],opacity=0.3,width=0.7,name='Ziel',hovertemplate='%{y}', orientation='h',
            marker_color=['#5d64bf','#60bbce','#f8be6a'])

#fig3.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
#                  marker_line_width=1.5, opacity=0.6)

fig3.add_bar(y=df6['Macro'],x=df6['Ist'],width=0.5,name='aufgenommen',text=df6['utilization'],
             textposition='outside', orientation='h', marker_color=['#5d64bf','#60bbce','#f8be6a'])



fig3.update_layout(xaxis_ticksuffix = 'g')
fig3.update_layout(barmode='overlay', xaxis_title='Menge')

fig3.update_layout(showlegend=False)

fig3.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})

fig3.update_layout(
    font_color="#a6a6a6",
    title_font_color="#a6a6a6",
    legend_title_font_color="#a6a6a6"
)

# %%
# get overview table of the last day
names = [df["Datum"].iloc[-1]]
df8 = df[df.Datum.isin(names)]
df8 = df8[['Produkt','Menge','Kalorien']]
df8 = df8.round(1)

# %%
import plotly.graph_objects as go

headerColor = 'grey'
rowEvenColor = 'lightgrey'
rowOddColor = 'white'

fig7 = go.Figure(data=[go.Table(
    columnwidth = [80,50,60],
    header=dict(values=list(df8.columns),
                line_color='darkslategray',
                fill_color=headerColor,
                align=['left','center'],
                font=dict(color='white', size=18)
                ),
    cells=dict(values=df8.transpose().values.tolist(),
                line_color='darkslategray',
                # 2-D list of colors for alternating rows
                fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
                align = ['left', 'center'],
                font = dict(color = 'darkslategray', size = 14)
               ))
])


#fig7.show()

# %%
# ---- MAINPAGE ----



st.set_page_config(
    page_title="Kalorienverbrauch App",
    page_icon="🍏",
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



color1 = "#FFFFFF"
color2 = "#FFFFFF"
color3 = "#a6a6a6"

text="Calory_Calculator"

def example(color1, color2, color3, content):
     st.markdown(f'<p style="text-align:center;background-image: linear-gradient(to right,{color1}, {color2});color:{color3};font-size:40px;font-weight: bold;border-radius:2%;">{content}</p>', unsafe_allow_html=True)
example(color1,color2,color3,text)

#st.markdown("""---""") 
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

# create blank space between objects

st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)

st.markdown('#')  

st.plotly_chart(fig1, use_container_width=True)

st.markdown('#')  


#text="Aufgenommene Produkte am " + str(df["Datum"].iloc[-1])

#def example(color1, color2, color3, content):
#     st.markdown(f'<p style="text-align:center;background-image: linear-gradient(to right,{color1}, {color2});color:{color3};font-size:40px;font-weight: bold;border-radius:2%;">{content}</p>', unsafe_allow_html=True)
#example(color1,color2,color3,text)

#st.subheader("Aufgenommene Produkte am " + str(df["Datum"].iloc[-1]))

st.markdown(f'<h1 style="color:#a6a6a6;font-size:24px;">{"Aufgenommene Produkte am " + str(df["Datum"].iloc[-1])}</h1>', unsafe_allow_html=True)
st.plotly_chart(fig7, use_container_width=True)
        

# Remove “Made with Streamlit” from bottom of app
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


# %%
