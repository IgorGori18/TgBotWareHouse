from collections import defaultdict
import sqlite3
import os



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'sql', 'warehouse.db')


def get_db_connection():
    connection = sqlite3.connect(db_path, timeout=10)
    return connection

def cash_rest():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            SELECT SUM(B.balance * P.price) AS total_cash
            FROM Balances AS B
            JOIN ProductsGuide AS P ON B.article = P.article;
        """
        cursor.execute(query)
        result = cursor.fetchone()
        total_cash = result[0] if result[0] is not None else 0
        connection.close()
        return total_cash
    except Exception as e:
        print("Ошибка при расчёте общего остатка денег:", e)
        return None

def rest_of_good(article):
    try:
        connеction = get_db_connection()
        cursor = connеction.cursor()

        # Используем LEFT JOIN, чтобы даже если для товара отсутствует запись в Balances, вернуть 0 остаток.
        query = """
            SELECT P.name, P.price, IFNULL(B.balance, 0) AS balance
            FROM ProductsGuide P
            LEFT JOIN Balances B ON P.article = B.article
            WHERE P.article = ?
        """
        cursor.execute(query, (article.strip(),))
        result = cursor.fetchone()
        connеction.close()

        if not result:
            return f"Товар с артикулом '{article}' не найден."

        product_name, price, balance = result

        if balance == 0:
            return f"Остатков товара с артикулом '{article}' нет на складе."

        total_cost = price * balance
        return (
            f"Товар: {product_name}\n"
            f"Артикул: {article}\n"
            f"Остаток: {balance} шт\n"
            f"Общая стоимость: {total_cost} руб"
        )

    except Exception as e:
        return f"Ошибка при получении данных: {e}"


def rest_of_controllers():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Выбираем артикул, наименование товара и остаток для товаров, содержащих "FS_ST"
        query = """
            SELECT article, product_name, balance
            FROM Balances
            WHERE article LIKE '%FS_ST%' COLLATE NOCASE
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        connection.close()

        result_string = ""
        for row in rows:
            article, prod_name, total_balance = row
            if total_balance is None or total_balance == 0:
                continue
            result_string += f"🔸 {article}: {prod_name} {int(total_balance)} штук\n"

        if result_string == "":
            return "Нет остатков контроллеров на складе"
        return result_string

    except Exception as e:
        return f"Ошибка при получении данных: {e}"



def shipments(n):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if n == 0:
            days = 7
        elif n == 1:
            days = 30
        else:
            connection.close()
            return "Некорректный параметр периода. Используйте 0 (7 дней) или 1 (30 дней)."

        # SQL-запрос: выбираем наименование товара, суммарное количество отгрузок и общую стоимость отгрузок.
        query = f"""
            SELECT T.product_name, 
                   SUM(T.shipment) AS total_shipment, 
                   SUM(T.shipment * P.price) AS total_value
            FROM Transactions T
            JOIN ProductsGuide P ON T.article = P.article
            WHERE T.shipment > 0 
              AND datetime(T.date) >= datetime('now', '-{days} days')
            GROUP BY T.product_name
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        connection.close()

        result_str = ""
        for row in rows:
            product_name, total_shipment, total_value = row
            # Если количество отгрузок равно нулю или None, пропускаем запись
            if not total_shipment or total_shipment == 0:
                continue
            result_str += f"🔸 {product_name} {int(total_shipment)} штук {int(total_value)} рублей\n"

        if result_str == "":
            return "Нет отгрузок за данный период времени"
        return result_str

    except Exception as e:
        return f"Ошибка при получении данных: {e}"

def delivery(n):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if n == 0:
            days = 7
        elif n == 1:
            days = 30
        else:
            connection.close()
            return "Некорректный параметр периода. Используйте 0 (7 дней) или 1 (30 дней)."

        # SQL-запрос: выбираем наименование товара, суммарное количество поступлений и общую стоимость поступлений.
        query = f"""
            SELECT T.product_name, 
                   SUM(T.receipt) AS total_receipt, 
                   SUM(T.receipt * P.price) AS total_value
            FROM Transactions T
            JOIN ProductsGuide P ON T.article = P.article
            WHERE T.receipt > 0 
              AND datetime(T.date) >= datetime('now', '-{days} days')
            GROUP BY T.product_name
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        connection.close()

        result_str = ""
        for row in rows:
            product_name, total_receipt, total_value = row
            if not total_receipt or total_receipt == 0:
                continue
            result_str += f"🔸 {product_name} {int(total_receipt)} штук {int(total_value)} рублей\n"

        if result_str == "":
            return "Нет поступлений за данный период времени"
        return result_str

    except Exception as e:
        return f"Ошибка при получении данных: {e}"


def employees_work():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            SELECT T.surname, T.article, T.product_name,
                   MIN(CASE WHEN T.receipt > 0 THEN T.date END) AS receipt_date,
                   MIN(CASE WHEN T.shipment > 0 THEN T.date END) AS shipment_date,
                   SUM(T.receipt) AS total_receipt,
                   SUM(T.shipment) AS total_shipment,
                   SUM((T.receipt - T.shipment) * P.price) AS total_money
            FROM Transactions T
            JOIN ProductsGuide P ON T.article = P.article
            GROUP BY T.surname, T.article, T.product_name
            ORDER BY T.surname
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        connection.close()

        if not rows:
            return "Нет данных по сотрудникам"

        # Группировка данных по фамилии сотрудника
        employee_data = defaultdict(lambda: {"products": [], "total_money": 0})
        for row in rows:
            surname, article, product_name, receipt_date, shipment_date, total_receipt, total_shipment, total_money = row
            if surname is None:
                surname = "Неизвестно"
            employee_data[surname]["products"].append(
                (article, product_name, receipt_date, shipment_date, total_receipt, total_shipment)
            )
            employee_data[surname]["total_money"] += total_money if total_money is not None else 0

        result = ""
        # Формируем отчёт для каждого сотрудника
        for surname, data in employee_data.items():
            # Фильтруем только те записи, где есть хотя бы поступление или отгрузка
            filtered_products = [
                (article, prod, r_date, s_date, r, s)
                for article, prod, r_date, s_date, r, s in data["products"]
                if (r != 0 or s != 0)
            ]
            if not filtered_products:
                continue  # пропускаем сотрудника, если нет ненулевых записей
            result += f"{surname}:\n"
            # Поступления
            result += "🟢 Поступило:\n"
            for article, product, receipt_date, _, receipt, _ in filtered_products:
                if receipt != 0:
                    date_str = receipt_date if receipt_date is not None else "нет данных"
                    result += f"    [{article}] - {product}: {int(receipt)} шт (Дата: {date_str})\n"
            # Отгрузки
            result += "🔴 Отгружено:\n"
            for article, product, _, shipment_date, _, shipment in filtered_products:
                if shipment != 0:
                    date_str = shipment_date if shipment_date is not None else "нет данных"
                    result += f"    [{article}] - {product}: {int(shipment)} шт (Дата: {date_str})\n"
            result += f"💰 Сумма: {int(data['total_money'])} руб\n\n"

        if result == "":
            return "Нет данных по сотрудникам с ненулевыми поступлениями/отгрузками."
        return result

    except Exception as e:
        return f"Ошибка при получении данных: {e}"


def get_product_name(connection, article):
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM ProductsGuide WHERE article = ?", (article,))
    result = cursor.fetchone()
    return result[0] if result else "Unknown"



def insert_transaction(connection, article, product_name, receipt, shipment, comment, surname):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Transactions (article, product_name, receipt, shipment, comment, surname)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (article, product_name, receipt, shipment, comment, surname))
    connection.commit()




