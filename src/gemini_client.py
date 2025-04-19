import google.generativeai as genai
import os
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file
load_dotenv()

# Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Please set the GEMINI_API_KEY environment variable in the .env file.")
    exit()

def generate_sql(natural_language_query, schema_info):
    """
    Generates an SQL query from a natural language query and database schema information using the Gemini API.
    Args:
        natural_language_query (str): The natural language query.
        schema_info (dict): A dictionary containing the database schema information.
    Returns:
        str: The generated SQL query.
    """
    try:
        # Construct the prompt for the Gemini API
        prompt = f"""You are a helpful assistant that always responds in Traditional Chinese. 

        Generate SQL query based on the following natural language query and database schema. Always include a WHERE clause to filter the results by the '公司金鑰' column. Return only a single SQL query. The 員工薪資 table has a foreign key relationship with the 部門資訊 table on the 部門 column.

        Natural Language Query:
        {natural_language_query}

        Database Schema:
        {schema_info}
        """

        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Generate content using the Gemini API
        response = model.generate_content(prompt)

        # Extract the generated SQL query from the response
        sql_query = response.text.strip()

        return sql_query

    except Exception as e:
        error_message = f"Error generating SQL query: {e}"
        print(error_message)
        return None

if __name__ == '__main__':
    pass
