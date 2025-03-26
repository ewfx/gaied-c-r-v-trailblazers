import json

def parse_gemini_response(response):
    try:
        # Extract the text containing the JSON
        #content_text = response.result.candidates[0].content.parts[0].text.strip()

        content_text = response

        # Remove the code block markers if present
        if content_text.startswith("```json") and content_text.endswith("```"):
            content_text = content_text[7:-3].strip()

        # Convert JSON string to Python dictionary
        parsed_data = json.loads(content_text)

        return parsed_data
    except Exception as e:
        print(f"Error parsing response: {e}")
        return None

# Example usage
#parsed_data = parse_gemini_response(response)
#print(parsed_data)
