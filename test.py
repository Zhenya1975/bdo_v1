import pandas as pd
from datetime import datetime

sap_eo_data = pd.read_csv('temp_data/sap_eo_data.csv', dtype = str)
sap_eo_data['operation_start_date'] = pd.to_datetime(sap_eo_data['operation_start_date'])
sap_eo_data['expected_operation_finish_date'] = pd.to_datetime(sap_eo_data['expected_operation_finish_date'])
# sap_eo_data['gar_no'] =  sap_eo_data['gar_no'].fillna(0)
sap_eo_data['gar_no'].fillna(0, inplace = True) 

date_time_plug = '31/12/2199 23:59:59'
date_time_plug = datetime.strptime(date_time_plug, '%d/%m/%Y %H:%M:%S')
sap_eo_data['operation_start_date'].fillna(date_time_plug, inplace = True) 

print(sap_eo_data.info())