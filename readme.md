Таблица Eo_DB - это мастер-файл.

Eo_data_conflicts - это таблица конфликтов.
Конфликт может создать внешний файл. Конфликт может разрешить или загрущка sap-data или загрузка внешнего файла.

expected_operation_period_years = db.Column(db.Integer) # расчетый период эксплуатации.
  expected_operation_finish_date = db.Column(db.DateTime, default = date_time_plug) # расчетный срок завершения эксплуатации
  expected_operation_status_code = db.Column(db.String, db.ForeignKey('operation_statusDB.operation_status_code')) # статус в котором должно находиться оборудование на текущую дату
  expected_operation_status_code_date = db.Column(db.DateTime) # текущая дата снятия отчета в котором должно находиться оборудование