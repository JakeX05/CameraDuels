import os
import requests
from pyairtable import Api, Base


AIRTABLE_API_KEY = "patDL8LZpOZBiIqJn.42b2add520805ab6497dd71d782fb03860d4fa2b67e7284b3fa99e0f521e934e"
BASE_ID = "appkzoV3T5OcsljQl"  
TABLE_NAME = "tbl4TdhgfK0Qt5k6f"
ACCESS_TOKEN = os.environ.get('AIRTABLE_API_KEY')

api = Api(ACCESS_TOKEN)
base = Base(api, BASE_ID)
table = base.table(TABLE_NAME)

def get_person_info(name=None, email=None):
    """
    Fetch all information about a person based on their name or email.
    """
    # Ensure either name or email is provided
    if not name and not email:
        return "Please provide a name or email to search."

    # Set the search filter
    filter_formula = None
    if name:
        filter_formula = f"{{Name}} = '{name}'"
    elif email:
        filter_formula = f"{{Email}} = '{email}'"

    # Search for matching records
    records = table.all(formula=filter_formula)

    # Check if any record is found
    if records:
        person_info = records[0]['fields']
        keys_to_remove = ['Linkedin', 'Resume', "Images", "Created By"]
        for key in keys_to_remove:
            person_info.pop(key, None)
        return dict_to_string(person_info)  # Return the fields of the first matching record
    else:
        return "No matching record found."

def dict_to_string(data):
    lines = []
    for key, value in data.items():
        # Format each key-value pair
        if isinstance(value, list):
            # Join list items into a comma-separated string
            value_str = ", ".join(str(item) for item in value)
            lines.append(f"{key}: {value_str}")
        elif isinstance(value, dict):
            # Recursively convert nested dictionaries to strings
            nested_str = dict_to_string(value)
            lines.append(f"{key}:\n  {nested_str.replace('\n', '\n  ')}")  # Indent nested dictionaries
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)

