import pandas as pd
import numpy as np
from IPython.display import display
import easysqlite3
from sqlalchemy import create_engine
import string
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats
import chart_studio as py
from plotly.tools import FigureFactory as FF
from plotly.graph_objs import Bar, Scatter, Marker, Layout, Choropleth, Histogram
display(pd.read_csv('complaints2019.csv', nrows=9).head())
db_conn = create_engine('sqlite:///databases/complaints.db')
chunks = 25000

for data in pd.read_csv('complaints2019.csv', chunksize=chunks,
                        iterator=True, encoding='utf-8'):
    data = data.rename(columns={col: col.replace('-', ' ') for col in data.columns})
    data = data.rename(columns={col: col.strip() for col in data.columns})
    data = data.rename(columns={col: string.capwords(col) for col in data.columns})
    data = data.rename(columns={col: col.replace(' ', '') for col in data.columns})
    data.to_sql('data', db_conn, if_exists='append')
pd.read_sql_query('SELECT * FROM data LIMIT 10', db_conn)
query = pd.read_sql_query('SELECT Product, Company, COUNT(*) as `Complaints`'
                         'FROM data '
                         'GROUP BY Product '
                         'ORDER BY `Complaints` DESC', db_conn)
py.iplot([Bar(x=query.Product, y=query.Complaints)], filename = 'ConsumerComplaints_Products with most complaints')
query_responses = pd.read_sql_query('SELECT Company, COUNT(*) as `Complaints` '
                           'FROM data '
                           'GROUP BY Company '
                           'ORDER BY `Complaints` DESC '
                           'LIMIT 10 ', db_conn)
py.iplot([Bar(x=query_responses.Company, y=query_responses.Complaints)], filename='ConsumerComplaints_Companies with most Complaints')
query_comp = pd.read_sql_query('SELECT Company, '
                           'COUNT(CASE WHEN `TimelyResponse?` = "Yes" THEN 1 ELSE NULL END) As YesCount, '
                           'COUNT(CASE WHEN `TimelyResponse?` = "No" THEN 1 ELSE NULL END) As NoCount, '
                           'COUNT(*) as Total '
                           'FROM data '
                           'GROUP BY Company '
                           'HAVING COUNT(*) > 500 '
                           'ORDER BY YesCount DESC', db_conn)
query_comp['Timely_Response_Ratio'] = query_comp.YesCount / query_comp.Total * 100
bot_10_response = query_comp.sort_values('Timely_Response_Ratio', ascending=True)[0:10]
responses = 'Timely Responses: ' + bot_10_response.YesCount.astype(str) + '<br>' + 'Untimely Responses: ' + bot_10_response.NoCount.astype(str)
py.iplot([Bar(x=bot_10_response.Company, y=bot_10_response.Timely_Response_Ratio,
              text=responses)], filename='ConsumerComplaints_LowestTimelyResponse')
query3 = pd.read_sql_query('SELECT Product, Issue, COUNT(*) `Number of Complaints` '
                          'FROM data '
                          'WHERE Product = "Mortgage" '
                          'GROUP BY Issue '
                          'ORDER BY `Number of Complaints` DESC', db_conn)
py.iplot([Bar(x=query3.Issue, y=query3['Number of Complaints'])], filename='ConsumerComplaints_MostComplainedProductIssue')
state_query = pd.read_sql_query('SELECT ZIPCode, Product, COUNT(*) as `Complaints` '
                                'FROM data '
                                'WHERE ZipCode <> "None" '
                                'GROUP BY ZIPCode', db_conn
                               )
dat = [dict(
    type = 'choropleth',
    locations = state_query['ZIP'],
    z = state_query['Complaints'],
    locationmode = 'USA-ZIP'
    )]

layout = dict(geo = dict(
    scope='usa', showlakes=True, lakecolor = 'rgb(255, 255, 255)'))

fig = dict(data=dat, layout=layout)

py.iplot(fig, filename='complaints_ZIPWithMostComplaints')
