import requests

class SalesforceAPIClient:
    def __init__(self, instance_url, access_token):
        self.instance_url = instance_url
        self.access_token = access_token

    def update_case(self, case_id, update_data):
        url = f"{self.instance_url}/services/data/v56.0/sobjects/Case/{case_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.patch(url, json=update_data, headers=headers)

        if response.status_code == 204:
            return {"message": "Case updated successfully"}
        else:
            return {"error": response.json()}

# Example usage:
# client = SalesforceAPIClient("https://your-instance.salesforce.com", "your-access-token")
# result = client.update_case("5003j00001ABC123", {"Status": "Closed"})
# print(result)

#client = SalesforceAPIClient("https://orgfarm-7836299064-dev-ed.develop.my.salesforce.com", "Replace with your valid API key")
#result = client.update_case("500gK000000zS6lQAE", {"Status": "Closed"})
#print(result)
