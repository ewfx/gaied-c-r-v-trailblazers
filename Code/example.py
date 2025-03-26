import json

# Assuming `response_text` is the text you want to convert to JSON
response_text = '{"caseId": "500gK000001lWOrQAM", "request_type": "Inquiry", "summary": "Test summary"}'

try:
    # Convert text to JSON
    response_json = json.loads(response_text)

    # Log the converted JSON
    print("Converted JSON:", response_json)

    # Check and log the data type of the converted JSON
    print("Data type of response_json:", type(response_json))
except json.JSONDecodeError as e:
    # Handle JSON decoding errors
    print("Error decoding JSON:", e)
