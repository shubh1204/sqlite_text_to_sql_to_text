import pandas as pd
import sqlite3
import json


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, data=None):
        if data:
            self.cursor.executemany(query, data)
        else:
            self.cursor.execute(query)

    def commit_and_close(self):
        self.conn.commit()
        self.conn.close()


class TableManager:
    def __init__(self, db):
        self.db = db

    def create_tables(self):
        self.db.execute_query("""
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY,
            ProductName TEXT,
            Category TEXT,
            Description TEXT,
            Brand TEXT,
            Price REAL,
            Quantity INTEGER,
            SupplierID TEXT,
            ReorderLevel INTEGER,
            CreatedDate TEXT
        )
        """)

        self.db.execute_query("""
        CREATE TABLE IF NOT EXISTS Suppliers (
            SupplierID TEXT PRIMARY KEY,
            SupplierName TEXT,
            Address TEXT,
            City TEXT,
            State TEXT,
            Country TEXT,
            PhoneNumber TEXT,
            Email TEXT,
            ContactPerson TEXT,
            CreatedDate TEXT
        )
        """)

        self.db.execute_query("""
        CREATE TABLE IF NOT EXISTS Inventory (
            InventoryID TEXT PRIMARY KEY,
            ProductID INTEGER,
            WarehouseID TEXT,
            QuantityAvailable INTEGER,
            QuantityReserved INTEGER,
            QuantityDamaged INTEGER,
            LastRestockedDate TEXT,
            CreatedDate TEXT,
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        )
        """)

        self.db.execute_query("""
        CREATE TABLE IF NOT EXISTS Warehouses (
            WarehouseID TEXT PRIMARY KEY,
            WarehouseName TEXT,
            Location TEXT,
            ManagerName TEXT,
            PhoneNumber TEXT,
            Capacity INTEGER,
            CurrentOccupancy INTEGER,
            CreatedDate TEXT
        )
        """)

        self.db.execute_query("""
        CREATE TABLE IF NOT EXISTS Orders (
            OrderID TEXT PRIMARY KEY,
            CustomerID TEXT,
            ProductID INTEGER,
            QuantityOrdered INTEGER,
            OrderDate TEXT,
            ShippingDate TEXT,
            Status TEXT,
            TotalPrice REAL,
            CreatedDate TEXT,
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        )
        """)


class DataInserter:
    def __init__(self, db_name):
        self.db_name = db_name

    def write_json_to_db(self, json_files):
        """
        Reads data from JSON files and writes to the respective tables in the SQLite database.

        :param json_files: Dictionary containing table names as keys and JSON file paths as values.
        :param db_name: Name of the SQLite database.
        """
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            for table, file_path in json_files.items():
                # Read JSON file into a Pandas DataFrame
                data = pd.read_json(file_path)

                # Write DataFrame to the database
                data.to_sql(table, conn, if_exists="append", index=False)
                print(f"Data from {file_path} written to {table} table successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Close the database connection
            conn.close()

    import sqlite3
    import json

    def write_nested_json_to_db(self, json_files):
        """
        Reads nested JSON files and writes the data to their respective tables in the SQLite database.

        :param json_files: Dictionary containing table names as keys and JSON file paths as values.
        :param db_name: Name of the SQLite database.
        """
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            for file_path in json_files.values():
                # Read JSON file
                with open(file_path, 'r') as file:
                    data = json.load(file)

                # Iterate over each table in the JSON data
                for table_name, records in data.items():
                    # Convert the list of records into rows for the database
                    if records:
                        # Extract columns from the first record
                        columns = ', '.join(records[0].keys())
                        placeholders = ', '.join(['?'] * len(records[0]))

                        # Prepare the SQL insert query
                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

                        # Insert all records into the database
                        cursor.executemany(query, [tuple(record.values()) for record in records])
                        print(f"Data written to {table_name} table successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Commit the changes and close the database connection
            conn.commit()
            conn.close()
