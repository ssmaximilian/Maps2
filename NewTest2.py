import pandas as pd
import numpy as np
from IPython.display import display
import sqlite3
from sqlalchemy import create_engine
import string
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats
import chart_studio as py
from plotly.tools import FigureFactory as FF
from plotly.graph_objs import Bar, Scatter, Marker, Layout, Choropleth, Histogram
display(pd.read_csv('complaints2020.csv', nrows=9).head())
db_conn = create_engine('sqlite:///databases/complaints.db')
chunks = 5
query = pd.read_sql_query('SELECT Product, Company, COUNT(*) as `Complaints`'
                         'FROM data '
                         'GROUP BY Product '
                         'ORDER BY `Complaints` DESC', db_conn)