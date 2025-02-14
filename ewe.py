import math
import pandas as pd

# Исходные параметры
N_total = 10000                # Общее количество пользователей
R_ad = 5                      # Доход от рекламы (₽/мес)
P_lite = 200                    # Цена подписки Lite (₽/мес)
P_pro = 1200                    # Цена подписки PRO (₽/мес)
K_free = 1000                 # Токены Free на пользователя
K_lite = 2000                # Токены Lite на пользователя
K_pro = 5000                   # Токены PRO на пользователя
Usage_factor = 0.8              # Коэффициент использования токенов
PackageTokens = 10000000         # Токенов в одном пакете
PackagePrice = 285000             # Цена пакета (₽)
Salary_designer = 100000         # ЗП дизайнера (₽/мес)
Salary_manager = 150000          # ЗП менеджера (₽/мес)
Salary_programmer = 130000       # ЗП программиста (₽/мес)
FreelanceRate = 60000           # Затраты на фрилансеров (₽/мес)
T_development = 3               # Время разработки (мес)
ServerCost_dev = 20000           # Серверы во время разработки (₽/мес)
ServerCost_prod = 15000         # Серверы после запуска (₽/мес)
Months = 12                     # Период расчёта (мес)

# Конверсия пользователей
Retention_free = 0.6  # 60% остаются на бесплатном тарифе
Conversion_lite = 0.1  # 10% переходят на Lite
Conversion_pro = 0.05  # 5% переходят на PRO

N_free = N_total * Retention_free
N_lite = N_total * Conversion_lite
N_pro = N_total * Conversion_pro

# Доходы за период
Revenue_ad    = N_free * R_ad * Months
Revenue_lite  = N_lite * P_lite * Months
Revenue_pro   = N_pro * P_pro * Months
Revenue_total = Revenue_ad + Revenue_lite + Revenue_pro

# Потребление токенов
K_free_total = N_free * K_free * Usage_factor * Months
K_lite_total = N_lite * K_lite * Usage_factor * Months
K_pro_total  = N_pro * K_pro * Usage_factor * Months
K_total      = K_free_total + K_lite_total + K_pro_total

# Затраты на токены
Number_of_packages = math.ceil(K_total / PackageTokens)
Cost_tokens = Number_of_packages * PackagePrice

# Затраты на команду (разработка + поддержка)
Cost_team_dev = (Salary_designer + Salary_manager + Salary_programmer) * T_development
Cost_team_support = (Salary_manager + Salary_programmer) * (Months - T_development)
Cost_team_total = Cost_team_dev + Cost_team_support

# Затраты на фрилансеров
Cost_freelance = FreelanceRate * T_development

# Затраты на серверы (разработка + продакшн)
Cost_server_dev = ServerCost_dev * T_development
Cost_server_prod = ServerCost_prod * (Months - T_development)
Cost_server_total = Cost_server_dev + Cost_server_prod

# Общие затраты
Cost_total = Cost_tokens + Cost_team_total + Cost_freelance + Cost_server_total

# Прибыль
Profit = Revenue_total - Cost_total

# Расчёт ARPU (выручка на одного пользователя)
ARPU = Revenue_total / N_total

# Расчёт COGS (себестоимость на одного пользователя)
COGS = (Cost_tokens + Cost_server_total) / N_total

# Валовая прибыль на единицу
Gross_Profit = ARPU - COGS

# Расчёт точки безубыточности (количество пользователей)
Fixed_Costs = Cost_team_total + Cost_freelance + Cost_server_total  # Фиксированные затраты
BreakEven_Users = Fixed_Costs / (ARPU - COGS)

# Средняя продолжительность жизни клиента (LTV)
Retention_rate = Retention_free  # Используем retention для бесплатных пользователей (можно уточнить для всех)
Avg_Lifetime = 1 / (1 - Retention_rate)

# Расчёт LTV
LTV = ARPU * Avg_Lifetime

# Расчёт стоимости привлечения клиента (CAC)
Marketing_Expenses = Revenue_ad + Revenue_lite + Revenue_pro  # Это условно считаем как расходы на маркетинг
New_Users = N_lite + N_pro  # Сумма новых пользователей Lite и PRO
CAC = Marketing_Expenses / New_Users

# Формирование таблицы результатов финансов
data_financial = {
    "Показатель": [
        "Доход от рекламы",
        "Доход от подписки Lite",
        "Доход от подписки PRO",
        "Общий доход",
        "Затраты на токены",
        "Затраты на команду",
        "Затраты на фрилансеров",
        "Затраты на серверы",
        "Общие затраты",
        "Прибыль"
    ],
    "Значение (₽)": [
        Revenue_ad,
        Revenue_lite,
        Revenue_pro,
        Revenue_total,
        Cost_tokens,
        Cost_team_total,
        Cost_freelance,
        Cost_server_total,
        Cost_total,
        Profit
    ]
}

df_financial = pd.DataFrame(data_financial)

# Формирование таблицы результатов unit economics
data_unit_economics = {
    "Показатель": [
        "Точка безубыточности (пользователей)",
        "ARPU (выручка на одного пользователя)",
        "COGS (себестоимость на одного пользователя)",
        "Валовая прибыль на единицу",
        "LTV (пожизненная ценность клиента)",
        "CAC (стоимость привлечения клиента)"
    ],
    "Значение": [
        round(BreakEven_Users, 2),
        round(ARPU, 2),
        round(COGS, 2),
        round(Gross_Profit, 2),
        round(LTV, 2),
        round(CAC, 2)
    ]
}

df_unit_economics = pd.DataFrame(data_unit_economics)

# Вывод таблиц
print("Финансовые результаты:")
print(df_financial)
print("\nРезультаты unit economics:")
print(df_unit_economics)

print('Инвест запрос')

print('Затраты на фрилансера', FreelanceRate*3)
print('ЗП дизайнера ', (Salary_designer*3)/3)
print('ЗП менеджера', (Salary_manager*3)/3)
print('ЗП программиста', (Salary_programmer*3)/3)
print('Стоимость серверов', ServerCost_dev*3)

print('Суммарная стоимость инвест запроса:', (FreelanceRate+Salary_designer/3+ Salary_manager/3+Salary_programmer/3+ServerCost_dev)*3 )
