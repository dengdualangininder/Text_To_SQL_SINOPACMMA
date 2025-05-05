import sqlite3
import random
import datetime
import csv
import json

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

def populate_salaries(conn, num_records=5):
    """Populates the 員工薪資 table with fake data."""
    sql = """
    INSERT INTO 員工薪資 (員工編號, 員工姓名, 薪資, 部門, 職稱, 到職日期, 公司金鑰, 薪資日期)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.cursor()
    employee_names = ["Johnny Hsiao", "Mark Wu", "Jerry Chang", "Grace Chen"]
    job_titles = ["Engineer", "Manager", "Analyst", "Developer", "Designer", "Tester"]
    departments = ["Sales", "Marketing", "Engineering", "HR", "IT", "Finance", "Research", "Operations"]
    for i in range(min(num_records, len(employee_names))):
        employee_id = i + 1
        employee_name = employee_names[i]
        salary = random.randrange(50, 150, 10) * 1000
        department = departments[i % len(departments)]
        job_title = random.choice(job_titles)
        hire_date = f"{random.randint(2020, 2024)}-{random.randint(1, 12):02}-{random.randint(1, 28):02}"
        month = random.randint(1, 4)
        day = random.randint(1, 22)
        salary_date = f"2025-{month:02}-{day:02}"
        company_key = random.choice(["6224", "6225", "6226"]) if i > 0 else "6224"
        values = (employee_id, employee_name, salary, department, job_title, hire_date, company_key, salary_date)
        cur.execute(sql, values)
    conn.commit()
    print("Populated 員工薪資 table")
    cur.execute("SELECT COUNT(*) FROM 員工薪資")
    count = cur.fetchone()[0]
    print(f"Number of rows in 員工薪資: {count}")

def populate_departments(conn, num_records=2):
    """Populates the 部門資訊 table with fake data."""
    sql = """
    INSERT INTO 部門資訊 (部門編號, 部門名稱, 部門主管, 部門人數, 地點, 公司金鑰)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    cur = conn.cursor()
    departments = ["Sales", "Marketing", "Engineering", "HR", "IT", "Finance", "Research", "Operations"]
    locations = ["New York", "London", "Tokyo", "Sydney", "Paris", "Berlin", "Singapore", "Hong Kong"]
    managers = ["Coolson", "CT Pan"]
    for i in range(num_records):
        department_id = i + 1
        department_name = departments[i] if i < len(departments) else "Other"
        manager = managers[i % (len(managers))]
        employee_count = random.randint(5, 50)
        location = random.choice(locations)
        company_key = "6224"
        values = (department_id, department_name, manager, employee_count, location, company_key)
        cur.execute(sql, values)
    conn.commit()
    print("Populated 部門資訊 table")
    cur.execute("SELECT COUNT(*) FROM 部門資訊")
    count = cur.fetchone()[0]
    print(f"Number of rows in 部門資訊: {count}")

def populate_twd_payment_details(conn, num_records=3):
    """Populates the 交易明細 table with fake data."""
    sql = """
    INSERT INTO 交易明細 (付款金額, 費用類型, 付款人資訊, 收款人資訊, 交易日期, 公司金鑰, 付款備註, 帳戶, 幣別)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.cursor()
    charge_types = ["Water Bill", "Electricity Bill", "Gas Bill", "Materials", "Rent", "Advertising", "Utilities", "Salaries"]
    payer_info = ["John Smith", "David Lee", "Mary Chen"]
    payee_info = ["Water Company", "Electric Company", "Gas Company"]
    payment_memos = ["材料費", "辦公室租金", "廣告費", "水電費", "薪資"]
    accounts = ["臺幣帳戶1", "臺幣帳戶2", "日幣帳戶", "美金帳戶", "歐元帳戶", "港幣帳戶"]
    currencies = ["TWD", "JPY", "USD", "EUR", "HKD"]
    account_currency_map = {
        "臺幣帳戶1": "TWD",
        "臺幣帳戶2": "TWD",
        "日幣帳戶": "TWD",
        "美金帳戶": "USD",
        "歐元帳戶": "EUR",
        "港幣帳戶": "HKD"
    }
    payment_memo_charge_map = {
        "材料費": "Materials",
        "辦公室租金": "Rent",
        "廣告費": "Advertising",
        "水電費": "Utilities",
        "薪資": "Salaries"
    }
    num_records = 20
    for i in range(num_records):
        payment_amount = round(random.uniform(100, 1000), 0)
        payment_memo = random.choice(payment_memos)
        charge_type = payment_memo_charge_map[payment_memo]
        payer = payer_info[i % len(payer_info)]
        payee = payee_info[i % len(payee_info)]
        month = random.randint(1, 4)
        day = random.randint(1, 22)
        transaction_date = f"2025-{month:02}-{day:02}"
        company_key = random.choice(["6224", "6225", "6226"])
        account = random.choice(accounts)
        currency = account_currency_map[account]
        values = (payment_amount, charge_type, payer, payee, transaction_date, company_key, payment_memo, account, currency)
        cur.execute(sql, values)
    conn.commit()
    print("Populated 交易明細 table")
    cur.execute("SELECT COUNT(*) FROM 交易明細")
    count = cur.fetchone()[0]
    print(f"Number of rows in 交易明細: {count}")

def populate_exchange_rates(conn):
    """Populates the 匯率資料表 table with data."""
    sql = """
    INSERT INTO 匯率資料表 (幣別, 生效日期, 匯率, 匯率類型, 公司金鑰)
    VALUES (?, ?, ?, ?, ?)
    """
    cur = conn.cursor()
    company_key = '6224'
    effective_date = datetime.date(2025, 5, 5).strftime("%Y-%m-%d")
    exchange_rate_type = "即期匯率"

    # Load exchange rates from JSON file
    with open("exchange_rates.json", 'r') as f:
        exchange_rates = json.load(f)

    for key, rate in exchange_rates.items():
        if key.startswith("TWD_"):
            currency = key[4:]
            values = (currency, effective_date, rate, exchange_rate_type, company_key)
            cur.execute(sql, values)

    conn.commit()
    print("Populated 匯率資料表 table")
    cur.execute("SELECT COUNT(*) FROM 匯率資料表")
    count = cur.fetchone()[0]
    print(f"Number of rows in 匯率資料表: {count}")

def populate_account_balances(conn):
    """Populates the 帳戶餘額表 table with initial data."""
    sql = """
    INSERT INTO 帳戶餘額表 (帳戶, 餘額, 幣別, 最低安全餘額, 公司金鑰)
    VALUES (?, ?, ?, ?, ?)
    """
    cur = conn.cursor()
    accounts = ["臺幣帳戶1", "臺幣帳戶2", "日幣帳戶", "美金帳戶", "歐元帳戶", "港幣帳戶"]
    exchange_rates = {
        "USD": 0.03,
        "JPY": 3.5,
        "EUR": 0.032,
        "HKD": 0.38
    }
    account_currency_map = {
        "臺幣帳戶1": "TWD",
        "臺幣帳戶2": "TWD",
        "日幣帳戶": "JPY",
        "美金帳戶": "USD",
        "歐元帳戶": "EUR",
        "港幣帳戶": "HKD"
    }
    company_key = '6224'
    for account in accounts:
        currency = account_currency_map[account]
        if currency == "TWD":
            min_safe_balance = 1000
            balance = random.randint(500, 2000)
        else:
            rate = exchange_rates[currency]
            min_safe_balance = round(1000 * rate, 2)
            balance = int(round(random.uniform(500, 2000) * rate, 0))
        values = (account, balance, currency, min_safe_balance, company_key)
        cur.execute(sql, values)
    conn.commit()
    print("Populated 帳戶餘額表 table")
    cur.execute("SELECT COUNT(*) FROM 帳戶餘額表")
    count = cur.fetchone()[0]
    print(f"Number of rows in 帳戶餘額表: {count}")

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
        print(f"Data from {table_name}: {rows}")

        # Get column names
        column_names = [description[0] for description in cur.description]
        for row in rows:
            print(row)

        # Write to CSV file
        with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
            import csv
            csv_writer = csv.writer(csvfile)
            # Write header row
            csv_writer.writerow(column_names)
            # Convert amount columns to integers
            new_rows = []
            for row in rows:
                if table_name == "員工薪資":
                    new_row = (row[0], row[1], int(row[2]), row[3], row[4], row[5], row[6], row[7])
                elif table_name == "部門資訊":
                    new_row = (row[0], row[1], row[2], int(row[3]), row[4], row[5])
                elif table_name == "交易明細":
                    new_row = (int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
                elif table_name == "匯率資料表":
                    new_row = (row[0], row[1], row[2], row[3], '6224')
                elif table_name == "帳戶餘額表":
                    new_row = (row[0], row[1], row[2], row[3], '6224')
                else:
                    new_row = row
                new_rows.append(new_row)
            # Write data rows
            csv_writer.writerows(new_rows)
        print(f"Exported {table_name} to {filename}")
    except sqlite3.Error as e:
        print(f"Error exporting {table_name}: {e}")

def main():
    conn = create_connection()
    if conn is not None:
        # Define table creation statements
        account_balance_table_sql = """
        CREATE TABLE IF NOT EXISTS 帳戶餘額表 (
            帳戶 TEXT PRIMARY KEY,
            餘額 REAL,
            幣別 TEXT,
            最低安全餘額 REAL,
            公司金鑰 TEXT,
            FOREIGN KEY (帳戶) REFERENCES 交易明細(帳戶)
        );
        """

        salaries_table_sql = """
        CREATE TABLE IF NOT EXISTS 員工薪資 (
            員工編號 INTEGER PRIMARY KEY,
            員工姓名 TEXT,
            薪資 REAL,
            部門 TEXT,
            職稱 TEXT,
            到職日期 TEXT,
            公司金鑰 TEXT,
            薪資日期 TEXT
        );
        """

        departments_table_sql = """
        CREATE TABLE IF NOT EXISTS 部門資訊 (
            部門編號 INTEGER PRIMARY KEY,
            部門名稱 TEXT,
            部門主管 TEXT,
            部門人數 TEXT,
            地點 TEXT,
            公司金鑰 TEXT
        );
        """

        twd_payment_details_table_sql = """
        CREATE TABLE IF NOT EXISTS 交易明細 (
            付款金額 REAL,
            費用類型 TEXT,
            付款人資訊 TEXT,
            收款人資訊 TEXT,
            交易日期 TEXT,
            公司金鑰 TEXT,
            付款備註 TEXT,
            帳戶 TEXT,
            幣別 TEXT
        );
        """

        exchange_rates_table_sql = """
        CREATE TABLE IF NOT EXISTS 匯率資料表 (
            幣別 TEXT,
            生效日期 TEXT,
            匯率 REAL,
            匯率類型 TEXT,
            公司金鑰 TEXT,
            PRIMARY KEY (幣別, 生效日期)
        );
        """

        # Drop existing tables (if they exist)
        try:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS 員工薪資")
            cur.execute("DROP TABLE IF EXISTS 部門資訊")
            cur.execute("DROP TABLE IF EXISTS 交易明細")
            cur.execute("DROP TABLE IF EXISTS 匯率資料表")
            cur.execute("DROP TABLE IF EXISTS 帳戶餘額表")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error dropping tables: {e}")

        # Create tables
        create_table(conn, account_balance_table_sql)
        create_table(conn, salaries_table_sql)
        create_table(conn, departments_table_sql)
        create_table(conn, twd_payment_details_table_sql)
        create_table(conn, exchange_rates_table_sql)

        # Populate tables with fake data
        populate_salaries(conn)
        populate_departments(conn)
        populate_twd_payment_details(conn)
        populate_exchange_rates(conn)
        populate_account_balances(conn)

        # Display table data
        display_table_data(conn, "員工薪資")
        display_table_data(conn, "部門資訊")
        display_table_data(conn, "交易明細")
        display_table_data(conn, "匯率資料表")
        display_table_data(conn, "帳戶餘額表")

        # Export to CSV
        export_to_csv(conn, "員工薪資", "員工薪資.csv")
        export_to_csv(conn, "部門資訊", "部門資訊.csv")
        export_to_csv(conn, "交易明細", "單筆付款交易明細.csv")
        export_to_csv(conn, "匯率資料表", "匯率資料表.csv")
        export_to_csv(conn, "帳戶餘額表", "帳戶餘額表.csv")

        conn.close()
    else:
        print("Cannot create database connection.")

if __name__ == "__main__":
    main()
