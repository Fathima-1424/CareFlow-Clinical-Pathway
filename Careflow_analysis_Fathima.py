#Careflow_analysis_Fathima.py

import pandas as pd
import pm4py

#Read a file
df=pd.read_csv('data.csv')

#1.Change datatime format
df['DateTime']=pd.to_datetime(df['DateTime'],dayfirst=True)

#2.To sort patient wise
df=df.sort_values(by=['patient','DateTime'])

#3.To fill empty value
df=df.ffill()

#4.To remove duplicate rows
df=df.drop_duplicates()

#5.To remove the space in column name
df.columns=df.columns.str.strip()

#6.caseconcept name for pm4py
df=df.rename(columns={'patient':'case:concept:name','activity':'concept:name','DateTime':'time:timestamp'})

#7.fix bracket close
print("7 fixes done")

#event log creation 
event_log=pm4py.format_dataframe(df,case_id='case:concept:name',activity_key='concept:name',timestamp_key='time:timestamp')
print(event_log.head())




