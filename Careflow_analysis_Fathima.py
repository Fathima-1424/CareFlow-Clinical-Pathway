#Careflow_analysis_Fathima.py

import pandas as pd
import pm4py

#Read a file
df=pd.read_csv('data.csv')

#1.To remove the space in column name
df.columns=df.columns.str.strip()

#2.To remove space in DateTime values
df['DateTime']=df['DateTime'].astype(str).str.strip()

#3.Change datetime format - no dayfirst
df['DateTime']=pd.to_datetime(df['DateTime'])

#4.To sort patient wise by DateTime
df=df.sort_values(by=['patient','DateTime'])

#5.To fill empty value
df=df.ffill()

#6.To remove duplicate rows
df=df.drop_duplicates()

#7.caseconcept name for pm4py - rename for event log
df=df.rename(columns={'patient':'case:concept:name','action':'concept:name','DateTime':'time:timestamp'})

#8.fix bracket close - 7 fixes done
print("7 fixes done")

#event log creation 
event_log=pm4py.format_dataframe(df,case_id='case:concept:name',activity_key='concept:name',timestamp_key='time:timestamp')
print(event_log.head())
