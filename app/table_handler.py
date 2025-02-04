import pandas as pd
import openpyxl as xl


def cash_rest():
    rest = pd.read_excel('/Users/gori/Desktop/TgBot/app/table.xlsx', skiprows=3, index_col=1, sheet_name='Склад_остатки')
    price = pd.read_excel('/Users/gori/Desktop/TgBot/app/table.xlsx', index_col=1, sheet_name='справочник_товаров')
    rest = pd.merge(rest, price, how='left', on='Наименование товара')
    rest['total'] = rest['Стоимость'] * rest['Остаток']
    total_rest = round(rest['total'].sum())
    print(rest)
    return total_rest



