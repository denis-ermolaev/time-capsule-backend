```python
"""
        Первая строка, статус
        1 - Доступ запрещён, капсула не открыта ИЛИ успешное создание капсулы
        2 - Текст получен, по времени или экстренному доступу
        3 - Экстренный доступ, + 1 попытка
        4 - время захода не правильное
        5 - экстренный доступ запрошен, время назначено
        6 - экстренный доступ запрошен, время скрыто и не показывается
        7 - экстренный доступ сброшен Используется когда ЭД не реализовался при режиме opening_days_mode
        8 - Экстренный доступ откроется только после даты открытия капсулы
        """
        if self.final_console_output["status"] == "1":
            print("1")
        elif self.final_console_output["status"] == "2":
            print("2")
            print(self.final_console_output["text"])
        elif self.final_console_output["status"] == "3":
            print("3")
            print(self.final_console_output["num_access"])
            print(self.final_console_output["start_limit"])
            print(self.final_console_output["end_limit"])
        elif self.final_console_output["status"] == "4":
            print("4")
            print(self.final_console_output["num_access"])
            print(self.final_console_output["start_limit"])
            print(self.final_console_output["end_limit"])
        elif self.final_console_output["status"] == "5":
            print("5")
            print(self.final_console_output["num_access"])
            print(self.final_console_output["start_limit"])
            print(self.final_console_output["end_limit"])
        elif self.final_console_output["status"] == "6":
            print("6")
        elif self.final_console_output["status"] == "7":
            print("7")
        elif self.final_console_output["status"] == "8":
            print("8")
```

```json
{
  "username": "millennium2",
  "password": "1234"
}


{
  "title": "Ну первая",
  "description": "string",
  "date_open": "2025-06-09T15:09:04.788Z",
  "private": false,
  "emergency_access": true,
  "ea_after_open": true,
  "ea_random": true,
  "ea_random_ratio": 0,
  "ea_time_separation": "string"
}

{
  "title": "Ну вторая",
  "description": "string",
  "date_open": "2025-07-09T15:09:04.788Z",
  "private": false,
  "emergency_access": true,
  "ea_after_open": true,
  "ea_random": true,
  "ea_random_ratio": 0,
  "ea_time_separation": "string"
}

{
  "title": "Ну третья",
  "description": "string",
  "date_open": "2025-08-09T15:09:04.788Z",
  "private": false,
  "emergency_access": true,
  "ea_after_open": true,
  "ea_random": true,
  "ea_random_ratio": 0,
  "ea_time_separation": "string"
}


{
  "title": "Ну четвёртая",
  "description": "string",
  "date_open": "2025-09-09T15:09:04.788Z",
  "private": false,
  "emergency_access": true,
  "ea_after_open": true,
  "ea_random": true,
  "ea_random_ratio": 0,
  "ea_time_separation": "string"
}

{
  "title": "А",
  "description": "string",
  "date_open": "2026-09-09T15:09:04.788Z",
  "private": false,
  "emergency_access": true,
  "ea_after_open": true,
  "ea_random": true,
  "ea_random_ratio": 0,
  "ea_time_separation": "string"
}

{
  "title": "Я",
  "description": "string",
  "date_open": "2026-10-09T15:09:04.788Z",
  "private": false,
  "emergency_access": true,
  "ea_after_open": true,
  "ea_random": true,
  "ea_random_ratio": 0,
  "ea_time_separation": "string"
}
```
