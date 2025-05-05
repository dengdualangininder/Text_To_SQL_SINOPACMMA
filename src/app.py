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
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.json') # Get absolute path
EXCHANGE_RATES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exchange_rates.json') # Get absolute path

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

    # Load database schema from JSON file
    with open(SCHEMA_FILE, 'r') as f:
        schema_info = json.load(f)

    # Load exchange rates from JSON file
    with open(EXCHANGE_RATES_FILE, 'r') as f:
        exchange_rates = json.load(f)

    # User input for natural language query
    natural_language_query = st.text_input("請輸入查詢：", key="natural_language_query", value=st.session_state.natural_language_query)

    try:
        filter_user_input(natural_language_query)
    except SecurityException as e:
        st.error(str(e))
        st.stop()

    # Check if database exists, create if not
    if not os.path.exists(DATABASE_FILE):
        import create_db
        conn = create_db.create_connection()
        create_db.main()
        conn.close()

    # Generate SQL query using Gemini API
    if st.session_state.natural_language_query:
        if st.session_state.natural_language_query.strip():
            with st.spinner("Generating SQL query..."):
                prompt = {
                    "query": st.session_state.natural_language_query,
                    "schema": schema_info,
                    "exchange_rates": exchange_rates,
                    "query": st.session_state.natural_language_query,
                    "schema": schema_info,
                    "exchange_rates": exchange_rates,
                    "instructions": "When the user's query involves currency conversion, use the 匯率資料表 table to get the exchange rates. The table contains the exchange rates against TWD for USD, JPY, EUR, and HKD.  The table has columns 幣別 (currency), 生效日期 (effective date), 匯率 (exchange rate), 匯率類型 (exchange rate type), and 公司金鑰 (company key). The 生效日期 (effective date) in the 匯率資料表 table represents the exchange rate for that specific date and does not need to match the transaction date in other tables.  Also, consider the new 帳戶餘額表 table which has columns 帳戶 (account), 餘額 (balance), 幣別 (currency), 最低安全餘額 (minimum safe balance), and 公司金鑰 (company key). DO NOT include the condition `H.生效日期 = T.交易日期` in the SQL query."
                }
                sql_query = gemini_client.generate_sql(prompt, schema_info)

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
                    No need to translate Results value
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
                if sql_query:
                    file_path = "output.txt"
                    with open(file_path, "w") as f:
                        f.write(sql_query)
                    st.success(f"SQL query saved to {file_path}")
                else:
                    st.error("Failed to generate SQL query.")
        else:
            st.error("Failed to generate SQL query.")    

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
