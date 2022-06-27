Таблица Eo_DB - это мастер-файл.

Импорт "Загрузка данных БДО САП."" Имя файла: "sap_eo_data.xlsx" обновляет значения без проверок.

Импорт "Загрузка данных из файлов "Парк оборудования". Имя файла: "be_eo_data.xlsx" Построчно проверяет данные. 
- Если не найден номер ео, то создается кандидат на добавление.
- Если номер найден, но значение в поле не совпадает с мастер-данными то создается конфликт с записью о расхождении.

Конфликт разрешается или повторной загрузкой с исправленным значением или загрузкой файла "Изменение мастер-данных"

Функции

generate_eo_diagram_data.generate_eo_diagram_data():
Основаная цель - сборка result_diagram_data_df.
Итерируемся по словарю year_dict.
Для каждого года из списка:
  - создается выборка из датафрема данных, полученных из мастер-файла. В выборку попадают записи, которые сейчас находятся в эксплуатации.
  Из выборки готовится временный датафрейм с записями с текущим годом и единичкой в поле qty_by_end_of_year и age
  - создается выборка с записями, которые вошли в эксплуатацию в текущем году. Эта выборка мерджится справа от предыдущей.
  - создается выборка с записями, которые вышли их эксплуатации в текущем году. Эта выборка мерджится справа от предыдущей.
  результирующий датафрейм конкатинируется снизу к предыдущему году.

generate_excel_calendar_status_eo

generate_excel_conflicts

generate_excel_master_eo

generate_excel_model_eo

import_be_data

import_eo_class_data

import_model_data

import_operation_status

import_sap_eo_data

read_be_eo_xlsx_file_v3

read_delete_eo_xlsx_file

read_eo_models_xlsx_file

read_sap_eo_xlsx_file


read_update_eo_data_xlsx_file.read_update_eo_data_xlsx(): 
Итерируемся по загруженному файлу uploads/update_eo_data.xlsx
Проверем есть ли искомая колонка в загруженном файле.
Если есть, то обновляем значение в соответствующей колонке в мастер данных

read_eo_models_xlsx_file.read_eo_models_xlsx()
Итерируемся по загруженному файлу с моделями.
Обновляем ранее созданные записи или создаем новые, если не находим в мастер-таблице