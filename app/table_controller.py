from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import load_workbook

def cash_rest():
    rest = pd.read_excel('table.xlsx', skiprows=3, index_col=1, sheet_name='Склад_остатки')
    price = pd.read_excel('table.xlsx', index_col=1, sheet_name='справочник_товаров')
    rest = pd.merge(rest, price, how='left', on='Наименование товара')
    rest['total'] = rest['Стоимость'] * rest['Остаток']
    total_rest = round(rest['total'].sum())
    print(rest)
    return total_rest

def rest_of_good(article):
    rest = pd.read_excel('table.xlsx', skiprows=3, sheet_name='Склад_остатки')
    price = pd.read_excel('table.xlsx', sheet_name='справочник_товаров')
    rest = pd.merge(rest, price, how='left', on='Наименование товара')
    rest['total'] = rest['Стоимость'] * rest['Остаток']
    article = int(article)
    res = rest.loc[rest['артикул_y'] == article]
    if rest.empty == True:
        s = "Нет товара с таким артикулом"
    elif res['Остаток'].empty:
        s = "Остатоков этого товара нет на складе"
    else:
        s1 = f"{res['Наименование товара']}"
        n = s1[5:(s1.find("\n"))]
        s2 = f"{res['Остаток']}"
        count = s2[5:(s2.find("."))]
        s3 = f"{res['total']}"
        cost = s3[5:(s3.find("\n"))]
        s = f'{n} \t{count} штук\t{cost} рублей'
    return s

def rest_of_controllers():
    rest = pd.read_excel('table.xlsx', skiprows=3, index_col=False, sheet_name='Склад_остатки')
    res = rest.loc[(rest['Наименование товара'].str.contains("Контроллер |контроллер "))]
    res = res[['Наименование товара', 'Остаток']]
    res = res.groupby(['Наименование товара'], as_index=False, sort=False).agg('sum')
    name = res['Наименование товара'].to_frame()
    count = res['Остаток'].to_frame()
    s = ""
    for i in range(0, name['Наименование товара'].count()):
        if np.isnan(count['Остаток'][i]) or count['Остаток'][i] == 0:
            continue
        else:
            s += f"{name['Наименование товара'][i]} {round(int(count['Остаток'][i]))} штук\n"
    if s == "":
        return "Нет остатков контроллеров на складе"
    return s

def shipments(n):
    warehouse_move = pd.read_excel('table.xlsx', sheet_name='Движение_склад')
    price = pd.read_excel('table.xlsx', sheet_name='справочник_товаров')
    if n == 0:
        warehouse_move = warehouse_move[ datetime.today() - pd.to_datetime(warehouse_move['Дата']) <= timedelta(days=7)]
    elif n == 1:
        warehouse_move = warehouse_move[datetime.today() - pd.to_datetime(warehouse_move['Дата']) <= timedelta(days=30)]
    warehouse_move = pd.merge(warehouse_move, price, how='left', on='Наименование товара')
    warehouse_move['sum'] = warehouse_move['Стоимость'] * warehouse_move['Отгрузка']
    res = warehouse_move[['Наименование товара', 'Отгрузка', 'sum']]
    res = res.groupby(['Наименование товара'], as_index=False, sort=False).agg('sum')
    name = res['Наименование товара'].to_frame()
    count = res['Отгрузка'].to_frame()
    cost = res['sum'].to_frame()
    s = ""
    for i in range(0, name['Наименование товара'].count()):
        if np.isnan(count['Отгрузка'][i]) or count['Отгрузка'][i] == 0:
            continue
        else:
            s += f"{name['Наименование товара'][i]} {round(int(count['Отгрузка'][i]))} штук {cost['sum'][i]} рублей\n"
    if s == "":
        return "Нет отгрузок за данный период времени"
    return s

def delivery(n):
    warehouse_move = pd.read_excel('table.xlsx', sheet_name='Движение_склад')
    if n == 0:
        warehouse_move = warehouse_move[ datetime.today() - pd.to_datetime(warehouse_move['Дата']) <= timedelta(days=7)]
    elif n == 1:
        warehouse_move = warehouse_move[datetime.today() - pd.to_datetime(warehouse_move['Дата']) <= timedelta(days=30)]
    price = pd.read_excel('table.xlsx', sheet_name='справочник_товаров')
    warehouse_move = pd.merge(warehouse_move, price, how='left', on='Наименование товара')
    warehouse_move['sum'] = warehouse_move['Стоимость'] * warehouse_move['Поступление']
    res = warehouse_move[['Наименование товара', 'Поступление', 'sum']]
    res = res.groupby(['Наименование товара'], as_index=False, sort=False).agg('sum')
    name = res['Наименование товара'].to_frame()
    count = res['Поступление'].to_frame()
    cost = res['sum'].to_frame()
    s = ""
    for i in range(0, name['Наименование товара'].count()):
        if np.isnan(count['Поступление'][i]) or count['Поступление'][i] == 0:
            continue
        else:
            s += f"{name['Наименование товара'][i]} {round(int(count['Поступление'][i]))} штук {cost['sum'][i]} рублей\n"
    if s == "":
        return "Нет поступлений за данный период времени"
    return s

def article():
    name = pd.read_excel('table.xlsx', index_col=1, sheet_name='справочник_товаров')
    s = name['артикул'].to_string()
    return s

def post_new(name, type, amount):
    date = datetime.today().strftime('%d.%m.%Y')
    if type == "shipment":
        new_data = {'Дата': [date], 'Наименование товара': [f'{name}'], 'Поступление': [0], 'Отгрузка': [int(amount)], 'Комментарий': ['Отгрузка tg-bot']}
    else:
        new_data = {'Дата': [date], 'Наименование товара': [f'{name}'], 'Поступление': [int(amount)], 'Отгрузка': [0], 'Комментарий': ['Поступление tg-bot']}
    new_data = pd.DataFrame.from_dict(new_data)
    wb = load_workbook(filename = "table.xlsx")
    ws = wb["Движение_склад"]
    for r in dataframe_to_rows(new_data, header=False, index=False):
        ws.append(r)
    wb.save("table.xlsx")
    print('done')

def is_coorect_article(article):
    try:
        goods = pd.read_excel('table.xlsx', sheet_name='справочник_товаров')
        goods = goods.loc[goods['артикул'] == int(article)]
        s1 = f"{goods['Наименование товара']}"
        print(goods)
        if goods.empty == True:
            return 0
        return s1[6:(s1.find("\n"))]
    except:
        return 0
    