departments_table = """
CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT,
    location TEXT,
    COMPANYKEY TEXT
);
"""

transactions_table = """
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    transaction_date TEXT,
    amount REAL,
    description TEXT,
    COMPANYKEY TEXT
);
"""
