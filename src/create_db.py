import sqlite3
import random

# Database file
DATABASE_FILE = "data.db"

def create_connection():
    """Creates a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn


def create_table(conn, table_sql):
    """Creates a table in the SQLite database."""
    try:
        c = conn.cursor()
        c.execute(table_sql)
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def populate_salaries(conn, company_key, num_records=5):
    """Populates the 員工薪資 table with fake data."""
    sql = """
    INSERT INTO 員工薪資 (員工編號, 員工姓名, 薪資, 部門, 公司金鑰, 薪資日期)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    cur = conn.cursor()
    for i in range(num_records):
        employee_id = i + 1
        employee_name = f"員工 {i+1}"
        salary = round(random.uniform(50000, 150000), 2)
        departments = ["Sales", "Marketing", "Engineering", "HR"]
        department = random.choice(departments)
        company_keys = ["6224", "6225", "6226"]
        company_key = random.choice(company_keys)
        salary_date = f"2024-{random.randint(1, 12):02}-{random.randint(1, 28):02}"
        values = (employee_id, employee_name, salary, department, company_key, salary_date)
        cur.execute(sql, values)
    conn.commit()
    print("Populated 員工薪資 table")
    cur.execute("SELECT COUNT(*) FROM 員工薪資")
    count = cur.fetchone()[0]
    print(f"Number of rows in 員工薪資: {count}")

def populate_departments(conn, company_key, num_records=2):
    """Populates the 部門資訊 table with fake data."""
    sql = """
    INSERT INTO 部門資訊 (部門編號, 部門名稱, 地點, 公司金鑰)
    VALUES (?, ?, ?, ?)
    """
    cur = conn.cursor()
    departments = ["Sales", "Marketing", "Engineering", "HR"]
    locations = ["New York", "London", "Tokyo", "Sydney"]
    company_keys = ["6224", "6225", "6226"]
    for i in range(num_records):
        department_id = i + 1
        department_name = departments[i] if i < len(departments) else "Other"
        location = random.choice(locations)
        company_key = random.choice(company_keys)
        values = (department_id, department_name, location, company_key)
        cur.execute(sql, values)
    conn.commit()
    print("Populated 部門資訊 table")
    cur.execute("SELECT COUNT(*) FROM 部門資訊")
    count = cur.fetchone()[0]
    print(f"Number of rows in 部門資訊: {count}")

def display_table_data(conn, table_name):
    """Displays all data from a table in the SQLite database."""
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()

        print(f"Data in {table_name}:")
        for row in rows:
            print(row)

    except sqlite3.Error as e:
        print(f"Error displaying data from {table_name}: {e}")

def export_to_csv(conn, table_name, filename):
    """Exports a table from the SQLite database to a CSV file."""
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()

        # Get column names
        column_names = [description[0] for description in cur.description]

        # Write to CSV file
        with open(filename, "w", newline="", encoding="big5") as csvfile:
            import csv
            csv_writer = csv.writer(csvfile)

            # Write header row
            csv_writer.writerow(column_names)

            # Write data rows
            csv_writer.writerows(rows)

        print(f"Exported {table_name} to {filename}")

    except sqlite3.Error as e:
        print(f"Error exporting {table_name}: {e}")

def main():
    conn = create_connection()
    if conn is not None:
        # Define table creation statements
        salaries_table_sql = """
        CREATE TABLE IF NOT EXISTS 員工薪資 (
            員工編號 INTEGER PRIMARY KEY,
            員工姓名 TEXT,
            薪資 REAL,
            部門 TEXT,
            公司金鑰 TEXT,
            薪資日期 TEXT
        );
        """

        departments_table_sql = """
        CREATE TABLE IF NOT EXISTS 部門資訊 (
            部門編號 INTEGER PRIMARY KEY,
            部門名稱 TEXT,
            地點 TEXT,
            公司金鑰 TEXT
        );
        """

        # Drop existing tables (if they exist)
        try:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS 員工薪資")
            cur.execute("DROP TABLE IF EXISTS 部門資訊")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error dropping tables: {e}")

        # Create tables
        create_table(conn, salaries_table_sql)
        create_table(conn, departments_table_sql)

        # Populate tables with fake data
        company_key = "6224"  # Replace with your actual company key
        populate_salaries(conn, company_key)
        populate_departments(conn, company_key)

        # Display table data
        display_table_data(conn, "員工薪資")
        display_table_data(conn, "部門資訊")

        # Export to CSV
        export_to_csv(conn, "員工薪資", "員工薪資.csv")
        export_to_csv(conn, "部門資訊", "部門資訊.csv")

        conn.close()
    else:
        print("Cannot create database connection.")

if __name__ == "__main__":
    main()
