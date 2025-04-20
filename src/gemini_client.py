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

def generate_sql(natural_language_query, schema_info, temperature=0.0):
    """
    Generates an SQL query from a natural language query and database schema information using the Gemini API.
    Args:
        natural_language_query (str): The natural language query.
        schema_info (dict): A dictionary containing the database schema information.
        temperature (float): The temperature for the Gemini API.
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
        response = model.generate_content(prompt, generation_config={"temperature": temperature})

        # Extract the generated SQL query from the response
        sql_query = response.text.strip()

        return sql_query

    except Exception as e:
        error_message = f"Error generating SQL query: {e}"
        print(error_message)
        return None

def generate_description(prompt, temperature=0.0): #設定termperature=0確保一致性
    """
    Generates a conversational description using the Gemini API.
    Args:
        prompt (str): The prompt for the Gemini API.
        temperature (float): The temperature for the Gemini API.
    Returns:
        str: The generated conversational description.
    """
    try:
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Generate content using the Gemini API
        response = model.generate_content(prompt, generation_config={"temperature": temperature})

        # Extract the generated conversational description from the response
        description = response.text.strip()

        return description

    except Exception as e:
        error_message = f"Error generating conversational description: {e}"
        print(error_message)
        return None

if __name__ == '__main__':
    pass
