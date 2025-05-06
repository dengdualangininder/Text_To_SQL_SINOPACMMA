import google.generativeai as genai
import os
from dotenv import load_dotenv
import datetime
import config
import re

def add_spaces_around_keywords(sql_query):
    """Adds spaces around SQL keywords to prevent syntax errors."""
    keywords = ["WHERE", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "JOIN", "AND", "OR", "NOT", "IN", "BETWEEN", "LIKE", "HAVING", "GROUP BY", "ORDER BY", "LIMIT", "SELECT", "FROM", "UPDATE", "DELETE", "INSERT", "INTO", "VALUES"]
    for keyword in keywords:
        sql_query = re.sub(r"(\b" + keyword + r"\b)", r" \1 ", sql_query)
    return sql_query

# Load environment variables from .env file
load_dotenv()

# Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Please set the GEMINI_API_KEY environment variable in the .env file.")
    exit()

def generate_sql(natural_language_query, schema_info, temperature=0.0):
    """Generates SQL query using Gemini API."""
    try:
        schema = schema_info
        prompt = config.SQL_TEMPLATE.format(schema=schema, question=natural_language_query, COMPANYKEY=config.COMPANYKEY)
        print(f"Prompt: {prompt}")

        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Define safety settings to reduce restrictions
        safety_settings = {
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE"
        }

        # Generate content using the Gemini API
        response = model.generate_content(
            prompt,
            generation_config={"temperature": temperature},
            safety_settings=safety_settings
        )

        # Extract the generated SQL query from the response
        sql_query = response.text.strip()
        # Add spaces around keywords
        sql_query = add_spaces_around_keywords(sql_query)
        return sql_query

    except Exception as e:
        error_message = f"Error generating SQL query: {e}"
        print(error_message)
        return None

def generate_description(prompt, temperature=0.0):
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

        # Define safety settings to reduce restrictions
        safety_settings = {
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE"
        }

        # Generate content using the Gemini API
        response = model.generate_content(
            prompt,
            generation_config={"temperature": temperature},
            safety_settings=safety_settings
        )

        # Extract the generated conversational description from the response
        description = response.text.strip()

        return description

    except Exception as e:
        error_message = f"Error generating conversational description: {e}"
        print(error_message)
        return None

if __name__ == '__main__':
    pass