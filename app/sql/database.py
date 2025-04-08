import sqlite3
from datetime import datetime


def create_tables(connection):
    try:
        with connection:
            query = """
                CREATE TABLE IF NOT EXISTS ProductsGuide (
                    id INTEGER PRIMARY KEY,
                    article TEXT NOT NULL,
                    name TEXT,
                    price INTEGER
                )
            """
            connection.execute(query)

            query = """
                CREATE TABLE IF NOT EXISTS Transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT DEFAULT (datetime('now', 'localtime')),
                    article TEXT NOT NULL,
                    product_name TEXT,
                    receipt INTEGER DEFAULT 0,
                    shipment INTEGER DEFAULT 0,
                    comment TEXT,
                    surname TEXT
                )
            """
            connection.execute(query)

            query = """
                CREATE TABLE IF NOT EXISTS Balances (
                    article TEXT PRIMARY KEY,
                    product_name TEXT,
                    total_receipt INTEGER DEFAULT 0,
                    total_shipment INTEGER DEFAULT 0,
                    balance INTEGER DEFAULT 0
                )
            """
            connection.execute(query)

            print("All tables created successfully")
    except Exception as e:
        print("Error creating tables:", e)


def create_triggers(connection):
    try:
        with connection:
            query = """
            CREATE TRIGGER IF NOT EXISTS update_balances_after_insert
            AFTER INSERT ON Transactions
            BEGIN
                -- Обновляем существующую запись в Balances для данного артикула
                UPDATE Balances
                SET total_receipt = (SELECT IFNULL(SUM(receipt), 0) FROM Transactions WHERE article = NEW.article),
                    total_shipment = (SELECT IFNULL(SUM(shipment), 0) FROM Transactions WHERE article = NEW.article),
                    balance = ABS(
                        (SELECT IFNULL(SUM(receipt), 0) FROM Transactions WHERE article = NEW.article) -
                        (SELECT IFNULL(SUM(shipment), 0) FROM Transactions WHERE article = NEW.article)
                    )
                WHERE article = NEW.article;

                -- Если записи для данного артикула ещё нет, вставляем новую запись
                INSERT OR IGNORE INTO Balances (article, product_name, total_receipt, total_shipment, balance)
                VALUES (
                    NEW.article,
                    NEW.product_name,
                    (SELECT IFNULL(SUM(receipt), 0) FROM Transactions WHERE article = NEW.article),
                    (SELECT IFNULL(SUM(shipment), 0) FROM Transactions WHERE article = NEW.article),
                    ABS(
                        (SELECT IFNULL(SUM(receipt), 0) FROM Transactions WHERE article = NEW.article) -
                        (SELECT IFNULL(SUM(shipment), 0) FROM Transactions WHERE article = NEW.article)
                    )
                );
            END;
            """
            connection.execute(query)
            print("Triggers created successfully.")
    except Exception as e:
        print("Error creating triggers:", e)


def initialize_database(db_path="warehouse.db"):
    connection = sqlite3.connect(db_path)
    create_tables(connection)
    create_triggers(connection)
    connection.close()
    print("Database initialization complete.")

def main():
    initialize_database()


if __name__ == "__main__":
    main()
