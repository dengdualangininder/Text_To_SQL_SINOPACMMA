import streamlit as st
import sqlite3
import gemini_client
import config
import os
from dotenv import load_dotenv
import schema_parser
import re
import datetime
import json

# Security Exception
class SecurityException(Exception):
    pass

def filter_user_input(user_input):
    banned_phrases = ["忽略", "刪除", "其他公司", "ignore", "delete", "other companies"]
    if any(phrase in user_input for phrase in banned_phrases):
        raise SecurityException("檢測到危險指令")

# Load environment variables from .env file
load_dotenv()

# Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Please set the GEMINI_API_KEY environment variable in the .env file.")
    st.stop()

# Database file
DATABASE_FILE = "data.db"
MEMORY_FILE = "memory.txt"

def query_database(sql_query):
    """Queries the SQLite database and returns the results."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor() #創建cursor用以執行SQL語句
        cur.execute(sql_query)
        rows = cur.fetchall()
        # Convert data to strings to handle encoding issues
        string_rows = []
        for row in rows:
            string_rows.append(tuple(str(x) for x in row))
        return string_rows
    except sqlite3.Error as e:
        st.error(f"Error querying database: {e}")
        return None
    finally:
        if conn:
            conn.close()

def load_history():
    """Loads history from memory.txt."""
    try:
        with open(MEMORY_FILE, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
    return history

def delete_history_item(index):
    """Deletes a history record and clears the input box."""
    del st.session_state.conversation_history[index]
    st.session_state.natural_language_query = ""

def main():
    st.title("CorpQuery-智能數據引擎")

    # Initialize session state for conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = load_history()

    if "natural_language_query" not in st.session_state:
        st.session_state.natural_language_query = ""

    # User input for natural language query
    natural_language_query = st.text_input("請輸入查詢：", key="natural_language_query", value=st.session_state.natural_language_query)

    try:
        filter_user_input(natural_language_query)
    except SecurityException as e:
        st.error(str(e))
        st.stop()

    # Define a more comprehensive schema for the Gemini API
    schema_info = {
        "員工薪資": [
            {"name": "員工編號", "type": "INTEGER", "description": "員工的唯一識別碼 (INTEGER, PRIMARY KEY, Example: 12345)"},
            {"name": "員工姓名", "type": "TEXT", "description": "員工的姓名 (TEXT, Example: 王小明, 李四, 張三)"},
            {"name": "薪資", "type": "REAL", "description": "員工的薪資 (INTEGER, Example: 50000, 60000, 70000)"},
            {"name": "部門", "type": "TEXT", "description": "員工的部門 (TEXT, FOREIGN KEY referencing 部門資訊.部門名稱, Example: Sales, Marketing, Engineering)"},
            {"name": "職稱", "type": "TEXT", "description": "員工的職稱 (TEXT, Example: Engineer, Manager, Analyst)"},
            {"name": "到職日期", "type": "TEXT", "description": "員工的到職日期 (TEXT, YYYY-MM-DD, Example: 2022-01-01, 2023-05-15, 2024-03-10)"},
            {"name": "公司金鑰", "type": "TEXT", "description": "公司的識別碼 (TEXT, Example: 6224)"},
            {"name": "薪資日期", "type": "TEXT", "description": "薪資的日期 (TEXT, YYYY-MM-DD, Example: 2024-04-18)"}
        ],
        "部門資訊": [
            {"name": "部門編號", "type": "INTEGER", "description": "部門的唯一識別碼 (INTEGER, PRIMARY KEY, Example: 1, 2, 3)"},
            {"name": "部門名稱", "type": "TEXT", "description": "部門的名稱 (TEXT, Example: Sales, Marketing, Engineering)"},
            {"name": "部門主管", "type": "TEXT", "description": "部門的主管姓名 (TEXT, Example: 陳經理, 林主任, 黃組長)"},
            {"name": "部門人數", "type": "INTEGER", "description": "部門的員工總數 (INTEGER, PRIMARY KEY, Example: 10, 20, 30)"},
            {"name": "地點", "type": "TEXT", "description": "部門的地點 (TEXT, Example: New York, London, Tokyo)"},
            {"name": "公司金鑰", "type": "TEXT", "description": "公司的識別碼 (TEXT, Example: 6224)"}
        ],
        "臺幣單筆付款交易明細": [
            {"name": "付款金額", "type": "REAL", "description": "付款的金額 (REAL, Example: 100, 200, 300)"},
            {"name": "費用類型", "type": "TEXT", "description": "費用的類型 (TEXT, Example: 水費, 電費, 瓦斯費)"},
            {"name": "付款人資訊", "type": "TEXT", "description": "付款人的資訊 (TEXT, Example: John Smith, David Lee, Mary Chen)"},
            {"name": "收款人資訊", "type": "TEXT", "description": "收款人的資訊 (TEXT, Example: Water Company, Electric Company, Gas Company)"},
            {"name": "交易日期", "type": "TEXT", "description": "交易的日期 (TEXT, YYYY-MM-DD, Example: 2025-01-01, 2025-02-15, 2024-03-10)"},
            {"name": "公司金鑰", "type": "TEXT", "description": "公司的識別碼 (TEXT, Example: 6224)"},
            {"name": "付款備註", "type": "TEXT", "description": "付款的備註 (TEXT, Example: 材料費, 辦公室租金, 廣告費)"}
        ]
    }

    # Generate SQL query using Gemini API
    if st.session_state.natural_language_query:
        if st.session_state.natural_language_query.strip():
            with st.spinner("Generating SQL query..."):
                sql_query = gemini_client.generate_sql(st.session_state.natural_language_query, schema_info)

            if sql_query:
                # Remove "```sql" from the beginning of the query
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
                sql_query = sql_query.replace("\n", "")

                # Add spaces around FROM and WHERE
                sql_query = sql_query.replace("FROM", " FROM ").replace("WHERE", " WHERE ")

                # Enforce 公司金鑰 condition
                company_key = config.COMPANYKEY
                # Enforce 公司金鑰 condition
                sql_query = re.sub(r"公司金鑰\s*=\s*(\".*?\"|'.*?')", f"公司金鑰 = '{company_key}'", sql_query, flags=re.IGNORECASE)
                if "WHERE" not in sql_query.upper():
                    sql_query = f"SELECT * FROM ({sql_query}) WHERE 公司金鑰 = '{company_key}'"

                # Extract employee number from the natural language query
                match = re.search(r"員工(\d+)", st.session_state.natural_language_query)
                if match:
                    employee_number = match.group(1)
                    employee_name = f"員工 {employee_number}"
                    # Replace the incorrect employee name in the SQL query with the correct one
                    sql_query = sql_query.replace("'員工姓名'", f"'{employee_name}'")

                # Query the database
                try:
                    print(f"Executing SQL query: {sql_query}")
                    with st.spinner("Executing SQL query..."):
                        results = query_database(sql_query)

                except sqlite3.Error as e:
                    st.error(f"Error querying database: {e}. Please check the generated SQL query and the database schema.")
                    results = None

                # Generate a conversational description of the query results
                results_string = ""
                if results:
                    for row in results:
                        results_string += str(row) + "\n"
                else:
                    results_string = "The SQL query returned no results."

                # 1st Summarization
                with st.spinner("Generating conversational description..."):
                    now = datetime.datetime.now()
                    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    description_prompt = f"""You are a helpful assistant that always responds in Traditional Chinese. The current time is {current_time}.

                    If the user's query involves calculating salaries "this month" or "currently", use the current date as the salary date.

                    Generate a conversational description of the query results.
                    Do not include the SQL query in the description.
                    Do not mention anything about '公司金鑰'，user don't know what is '公司金鑰', just explain it is the filter that belong user's company.
                    User Natural language query: {st.session_state.natural_language_query}
                    Query Results: {results_string}
                    """

                    if results_string == "The SQL query returned no results.":
                        description_prompt += """
                        Explain why there might be no data.
                        """

                    description = gemini_client.generate_description(description_prompt)
                print(f"1st description: {description}")

                if description:
                    # Display the results
                    st.write(description)
                    #st.write(results) Debug用

                    # Update conversation history
                    now = datetime.datetime.now()
                    timestamp = now.strftime("%Y-%m-%d %H:%M")
                    st.session_state.conversation_history.append((st.session_state.natural_language_query, description, timestamp))
                else:
                    st.error("Failed to generate a conversational description of the query results.")

                # Save the SQL query to a .txt file
            file_path = "output.txt"
            with open(file_path, "w") as f:
                f.write(sql_query)
            st.success(f"SQL query saved to {file_path}")
        else:
            st.error("Failed to generate SQL query.")

    # Export to CSV
    import create_db
    conn = create_db.create_connection()
    create_db.main()
    conn.close()

    # Display conversation history
    st.subheader("歷史紀錄")
    for i, item in enumerate(st.session_state.conversation_history):
        if len(item) == 2:
            query, response = item
            timestamp = "N/A"
        else:
            query, response, timestamp = item
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(f"👤 尊貴的客戶: {query}")
            st.markdown(f"🤖 CorpQuery: {response}")
            st.markdown(f"🕒 {timestamp}")
        with col2:
            def delete_callback(i):
                del st.session_state.conversation_history[i]
                st.session_state.natural_language_query = ""
            st.button("刪除", key=f"delete_{i}", on_click=delete_callback, args=(i,))

if __name__ == "__main__":
    main()
