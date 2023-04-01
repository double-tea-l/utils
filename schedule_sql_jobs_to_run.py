"""
Project: Weekly E2E One Pager SQL Jobs Schedule 
Created on Fri Nov 22 17:53:45 2019
"""

## Schedule job to run
import pyodbc
import pandas as pd
import schedule
import os
import numpy as np
import datetime
from datetime import date


# set directory
root = r'T:\1_Weekly E2E One Pager\Data\Scripts\Python'
dest = r'T:\1_Weekly E2E One Pager\Data\Scripts\Python'


# sheetname dictionary
sheetname_dict= {'inbound_appts_and_arriving_6am.sql': 'inbound_appts_and_arriving_6am',
                 'outbound_today_carryover.sql': 'outbound_today_carryover',
                 'yard_current_loads_in_yard.sql': 'yard_current_loads_in_yard',
                 'outbound_forecast_accuracy.sql': 'outbound_forecast_accuracy',
                 'yard_past_week_utilization.sq': 'yard_past_week_utilization',
                 'outbound_ordered_and_shipped.sql': 'outbound_ordered_and_shipped'
                 }


# List of paths
paths = ['inbound_appts_and_arriving_6am.sql',
         'outbound_today_carryover.sql',
         'yard_current_loads_in_yard.sql',
         'outbound_forecast_accuracy.sql',
         'yard_past_week_utilization.sq'
         'outbound_ordered_and_shipped.sql',
        ]

# connectio dictionary
connection_dict = {'inbound_appts_and_arriving_6am.sql': 'SERVERNAME',
                   'outbound_today_carryover.sql': 'SERVERNAME',
                   'yard_current_loads_in_yard.sql': 'SERVERNAME',
                   'outbound_forecast_accuracy.sql': 'SERVERNAME',
                   'yard_past_week_utilization.sq': 'SERVERNAME',
                   'outbound_ordered_and_shipped.sql': 'SERVERNAME'
                   }

# define function to get connected to SQL server and run queries
def getdata(path, root=root):
    with open("%s/%s"%(root, path), 'r') as usact:
        query = usact.read()
        conn = pyodbc.connect('DSN=%s'%connection_dict[path])
        print("%s/%s"%(root, path), 'r')
        print("%s %s"%(path,'is running'))
        temp_data=  pd.read_sql(query,conn)    
    return temp_data

try:
    for path in paths:
        data = getdata(path)
        data.to_csv("%s/%s"%(dest, path.replace(' ', '_').replace('sql', 'csv')), index=False)
        #data.to_excel(writer,sheet_name=sheetname_dict[path],index=False) #todo:
        print("%s %s"%(path,'has been saved'))
except:
    print("%s %s"%(path,'not available'))
    


def job():
    print('xxx')

# schedule to run
schedule.every().monday().at(5:00).do(job)
