import pandas as pd
from datetime import datetime

# sap_eo_data = pd.read_csv('temp_data/sap_eo_data.csv', dtype = str)
# sap_eo_data['operation_start_date'] = pd.to_datetime(sap_eo_data['operation_start_date'])
# sap_eo_data['expected_operation_finish_date'] = pd.to_datetime(sap_eo_data['expected_operation_finish_date'])
# # sap_eo_data['gar_no'] =  sap_eo_data['gar_no'].fillna(0)
# sap_eo_data['gar_no'].fillna(0, inplace = True) 

# date_time_plug = '31/12/2199 23:59:59'
# date_time_plug = datetime.strptime(date_time_plug, '%d/%m/%Y %H:%M:%S')
# sap_eo_data['operation_start_date'].fillna(date_time_plug, inplace = True) 

# print(sap_eo_data.info())
sap_eo_raw_data = pd.read_excel('uploads/sap_eo_data.xlsx', index_col = False, dtype=str)
print(sap_eo_raw_data)  
sap_eo_data = sap_eo_raw_data.rename(columns={'Планирующий завод':'be_code', 'Единица оборудования': 'eo_code', 'Название технического объекта':'eo_description', 'Техническое место': 'teh_mesto','Поле сортировки':'gar_no', "ДатВвода в эксплуат.":'operation_start_date'})
# поля с датами - в формат даты
# sap_eo_data["operation_start_date"] = pd.to_datetime(sap_eo_data["operation_start_date"], format='%d.%m.%Y')
sap_eo_data["operation_start_date"] = pd.to_datetime(sap_eo_data["operation_start_date"])
print(sap_eo_data.info())