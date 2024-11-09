import requests
import json
import time
import re
from datetime import datetime


# Replace this with your OpenRouter API key
API_KEY = "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"  # <-- Put your API key here

def get_date_from_llm(query):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "Return only the start and end dates in YYYY-MM-DD format, separated by a comma if there are two dates."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.1
            }
        )
        
        result = response.json()
        if 'error' in result:
            return f"Error: {result['error']}"
            
        date = result['choices'][0]['message']['content'].strip()
        return date

    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
query= "give me the dates of the lincoln presidency, just return two lines start_date: YYYY-MM-DD, end_date: YYYY-MM-DD, it has to be just that text as i jave to copy it in a code, i do not need more info than that"
date = get_date_from_llm(query)
print(date)

# Regular expression to extract the start and end dates
date_pattern = r"start_date: (\d{4}-\d{2}-\d{2}), end_date: (\d{4}-\d{2}-\d{2})"

# Use re.search to find the matches
match = re.search(date_pattern, date)

if match:
    # Extract the date strings
    start_date_str = match.group(1)
    end_date_str = match.group(2)
    
    # Convert to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    # Output the result
    print("start_date =", start_date)
    print("end_date =", end_date)
else:
    print("No matching dates found.")