from flask import Flask, request, jsonify
import mail_processor1  # Import the mail processor module

app = Flask(__name__)

@app.route('/api/data', methods=['POST'])
def handle_post():
    # Get JSON data from the request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Validate Salesforce-specific payload structure
    required_fields = ["caseId", "subject", "description", "status", "UID__c"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Process the Salesforce payload
    response = {
        "message": "Data received successfully",
        "caseId": data["caseId"],
        "subject": data["subject"],
        "description": data["description"],
        "status": data["status"],
        "UID__c": data["UID__c"]
    }

    # Invoke mail_processor1's main function with the payload
    mail_processor1.main(data)

    return jsonify(response), 200

if __name__ == '__main__': 
    app.run(debug=True)
