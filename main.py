import pandas as pd
from class_deinitions.database import Database, TableManager, DataInserter

if __name__ == "__main__":
    # Database setup
    db = Database("inventory_management.db")
    table_manager = TableManager(db)
    table_manager.create_tables()

    # Insert data using Pandas DataFrame
    data_inserter = DataInserter('inventory_management.db')
    json_files = {
        "Inventory": "data/inventory.json",
        "Orders": "data/orders.json",
        "Products": "data/products.json",
        "Suppliers": "data/suppliers.json",
        "Warehouses": "data/warehouses.json"
    }

    # Insert the DataFrame into the Products table
    data_inserter.write_nested_json_to_db(json_files)

    # Commit changes and close the database connection
    db.commit_and_close()
    print("Data inserted successfully using Pandas DataFrame!")
