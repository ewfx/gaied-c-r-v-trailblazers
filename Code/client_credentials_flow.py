import requests

def get_access_token(client_id, client_secret):
    url = "https://login.salesforce.com/services/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json()  # Contains access_token and instance_url
    else:
        error_details = response.json()
        print("Error:", error_details.get("error"))
        print("Error Description:", error_details.get("error_description"))
        return {"error": error_details}

# Example usage:
# Replace with your Salesforce connected app credentials
# client_id = "your-client-id"
# client_secret = "your-client-secret"
# token_response = get_access_token(client_id, client_secret)
# print(token_response)
