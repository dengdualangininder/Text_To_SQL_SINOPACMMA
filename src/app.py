import streamlit as st
import sqlite3
import gemini_client
import config
import os
from dotenv import load_dotenv
import schema_parser
import re

# Load environment variables from .env file
load_dotenv()

# Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Please set the GEMINI_API_KEY environment variable in the .env file.")
    st.stop()

# Database file
DATABASE_FILE = "data.db"

def query_database(sql_query):
    """Queries the SQLite database and returns the results."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor() #創建cursor用以執行SQL語句
        cur.execute(sql_query)
        rows = cur.fetchall()
        return rows
    except sqlite3.Error as e:
        st.error(f"Error querying database: {e}")
        return None
    finally:
        if conn:
            conn.close()

def main():
    st.title("MMAQube-text to SQL 查詢系統")

    # User input for natural language query
    natural_language_query = st.text_input("請輸入查詢：")

    if natural_language_query:
        # Define a more comprehensive schema for the Gemini API
        schema_info = {
            "員工薪資": [
                {"name": "員工編號", "type": "INTEGER", "description": "員工的唯一識別碼 (INTEGER, PRIMARY KEY, Example: 123)"},
                {"name": "員工姓名", "type": "TEXT", "description": "員工的姓名 (TEXT, Example: 王小明)"},
                {"name": "薪資", "type": "REAL", "description": "員工的薪資 (REAL, Example: 50000)"},
                {"name": "部門", "type": "TEXT", "description": "員工所屬的部門 (TEXT, Example: Sales)"},
                {"name": "公司金鑰", "type": "TEXT", "description": "公司的識別碼 (TEXT, Example: 6224)"},
                {"name": "薪資日期", "type": "TEXT", "description": "薪資的日期 (TEXT, YYYY-MM-DD, Example: 2024-04-18)"}
            ],
            "部門資訊": [
                {"name": "部門編號", "type": "INTEGER", "description": "部門的唯一識別碼 (INTEGER, PRIMARY KEY, Example: 1)"},
                {"name": "部門名稱", "type": "TEXT", "description": "部門的名稱 (TEXT, Example: Sales)"},
                {"name": "地點", "type": "TEXT", "description": "部門的地點 (TEXT, Example: New York)"},
                {"name": "公司金鑰", "type": "TEXT", "description": "公司的識別碼 (TEXT, Example: 6224)"}
            ]
        }

        # Generate SQL query using Gemini API
        with st.spinner("Generating SQL query..."):
            sql_query = gemini_client.generate_sql(natural_language_query, schema_info)

        if sql_query:
            # Remove "```sql" from the beginning of the query
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            sql_query = sql_query.replace("\n", "")

            # Add spaces around FROM and WHERE
            sql_query = sql_query.replace("FROM", " FROM ").replace("WHERE", " WHERE ")

            # Enforce 公司金鑰 condition
            company_key = config.COMPANYKEY
            # Enforce 公司金鑰 condition
            sql_query = re.sub(r"WHERE\s+公司金鑰\s*=\s*('.*?')", f"WHERE 公司金鑰 = '{company_key}'", sql_query, flags=re.IGNORECASE)
            if "WHERE" not in sql_query.upper():
                sql_query += f" AND 公司金鑰 = '{company_key}'"

            # Extract employee number from the natural language query
            match = re.search(r"員工(\d+)", natural_language_query)
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
                description_prompt = f"""You are a helpful assistant that always responds in Traditional Chinese. 

                Generate a conversational description of the following SQL query and results:

                SQL Query: {sql_query}

                Query Results: {results_string}

                If the query returned no results, explain why there might be no data. If the query includes a filter on the '公司金鑰' column, suggest that the user may be trying to access data that does not belong to their organization, without explicitly mentioning the value of the '公司金鑰' column.
                """

                description = gemini_client.generate_sql(description_prompt, schema_info)
            print(f"1st description: {description}")

            if description:
                # Display the results
                st.write(description)
            else:
                st.error("Failed to generate a conversational description of the query results.")

            # Save the SQL query to a .txt file
            file_path = "output.txt"
            with open(file_path, "w") as f:
                f.write(sql_query)
            st.success(f"SQL query saved to {file_path}")
        else:
            st.error("Failed to generate SQL query.")

if __name__ == "__main__":
    main()
