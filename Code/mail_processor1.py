import imaplib
import email
import os
import json
import re  # Add this import for sanitizing filenames
import google.generativeai as genai  # Add this import for Google Generative AI
from document_processor import extract_text_from_pdf  # Import the function from document_processor
from salesforce_api_client import SalesforceAPIClient  # Import Salesforce API client
from model_response_parse import parse_gemini_response  # Add this import

# Gmail IMAP server details
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# Configuration
EMAIL_ACCOUNT = 'Replace with your email address'  # Replace with your email address
PASSWORD = 'Replace with pass Key'  # Replace with the generated app password
UID = '22'  # Replace with a valid UID from the list
SAVE_DIR = r'Replace with you directory path'  # Replace with the directory path to save emails

def connect_to_gmail():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        print('Logged in successfully!')
        return mail
    except Exception as e:
        print(f'Error connecting to Gmail: {e}')
        exit()

def process_pdfs_in_folder(folder_path, project_id, processor_id, location="us"):
    try:
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith('.pdf'):
                file_path = os.path.join(folder_path, file_name)
                print(f'Processing PDF: {file_path}')
                try:
                    extracted_text = extract_text_from_pdf(file_path, project_id, processor_id, location)
                    text_file_path = os.path.join(folder_path, f'{os.path.splitext(file_name)[0]}_extracted.txt')
                    with open(text_file_path, 'w', encoding='utf-8') as text_file:
                        text_file.write(extracted_text)
                    print(f'Extracted text saved to: {text_file_path}')
                except Exception as e:
                    print(f'Error processing PDF {file_name}: {e}')
    except Exception as e:
        print(f'Error iterating PDFs in folder: {e}')

def list_available_models(api_key):
    try:
        # Authenticate with the API key
        genai.configure(api_key=api_key)

        # List available models
        models = genai.list_models()
        print("Available models:")
        for model in models:
            print(f"Model ID: {model['id']}, Supported Methods: {model['supportedMethods']}")
    except Exception as e:
        print(f"Error listing models: {e}")

def classify_email_with_gemini(api_key, email_subject, email_body, attachments_text, case_id):
    try:
        
        gemini_response = analyze_with_gemini(api_key, email_subject, email_body, attachments_text, case_id)

        if gemini_response:
            print(f'Classification result: {gemini_response}')
        else:
            print('Failed to classify the email.')
    except Exception as e:
        print(f'Error classifying email: {e}')

def process_eml_and_txt_files_in_folder(folder_path, api_key, case_id, salesforce_client):
    """
    Process .eml and .txt files in the folder, classify the email content using Google Generative AI,
    and update the case record in Salesforce with the response.
    """
    try:
        email_subject = "Aggregated Email Content"
        email_body = ""
        attachments_text = []

        # List all files in the folder
        files = os.listdir(folder_path)
        if not files:
            print(f"No files found in folder: {folder_path}")
            return

        # Process each file and aggregate content
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            if file_name.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as text_file:
                    attachments_text.append(text_file.read())
            elif file_name.lower().endswith('.eml'):
                with open(file_path, 'rb') as eml_file:
                    raw_email = eml_file.read()
                msg = email.message_from_bytes(raw_email)
                email_subject = msg.get('Subject', email_subject)
                email_body += f"\n{extract_email_body(None, msg)}"
            else:
                print(f'Skipping unsupported file type: {file_name}')

        # Combine attachments_text into a single string
        attachments_text_combined = "\n".join(attachments_text)

        # Call classify_email_with_gemini once with aggregated content
        response = analyze_with_gemini(api_key, email_subject, email_body, attachments_text_combined, case_id)
        #print(f"Classification Response: {response}")

        # Update the case record in Salesforce with the response
        if response.get("error") is None:  # Fix the condition to check for None
            update_data = {
                "Case_Type__c": response.get("request_type"),
                "Case_Sub_Type__c": response.get("sub_request_type"),
                "Summary__c": response.get("summary"),
                "Intent__c": response.get("intent"),
                "Sentiment__c": response.get("sentiment"),
                "Confidence_Score__c": response.get("confidence"),
                "Additional_Information__c": response.get("additional_info")
            }
            salesforce_response = salesforce_client.update_case(case_id, update_data)
            print(f"Salesforce Update Response: {salesforce_response}")
        else:
            print(f"Error in classification response: {response['error']}")
    except Exception as e:
        print(f'Error processing files in folder: {e}')

def fetch_and_save_email_by_uid(mail, uid):
    """
    Fetch an email by UID, save it locally, and process its attachments.
    """
    try:
        mail.select('inbox')
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK':
            print('Failed to fetch email')
            return

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject = msg.get('Subject', 'No_Subject')
        
        # Sanitize the subject to remove invalid characters
        sanitized_subject = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', subject)
        
        # Create a folder for the UID
        uid_folder = os.path.join(SAVE_DIR, uid)
        if not os.path.exists(uid_folder):
            os.makedirs(uid_folder)

        # Save the email as a .eml file
        filename = f'{sanitized_subject}.eml'
        filepath = os.path.join(uid_folder, filename)
        with open(filepath, 'wb') as f:
            f.write(raw_email)

        print(f'Email saved to: {filepath}')

        # Extract and save attachments
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                attachment_filename = part.get_filename()
                if attachment_filename:
                    sanitized_attachment_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', attachment_filename)
                    attachment_path = os.path.join(uid_folder, sanitized_attachment_name)
                    with open(attachment_path, 'wb') as attachment_file:
                        attachment_file.write(part.get_payload(decode=True))
                    print(f'Attachment saved to: {attachment_path}')

        # Process PDFs in the UID folder
        project_id = "Replace with your project id"  # Replace with your Google Cloud project ID
        processor_id = "Replace with your Dcoument processor Id"  # Replace with your Document AI processor ID
        location = "us"  # Adjust if your processor is in a different location
        process_pdfs_in_folder(uid_folder, project_id, processor_id, location)

        return uid_folder
    except Exception as e:
        print(f'Error fetching or saving email: {e}')
        return None

def extract_email_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() in ["text/plain", "text/html"]:
                    return part.get_payload(decode=True).decode(errors="ignore")
        return msg.get_payload(decode=True).decode(errors="ignore")

def list_email_uids(mail):
    try:
        mail.select('inbox')
        result, data = mail.uid('search', None, 'ALL')
        if result != 'OK':
            print('Failed to fetch UIDs')
            return []

        uids = [uid.decode('utf-8') for uid in data[0].split()]  # Decode UIDs
        print(f'Available UIDs: {uids}')
        return uids
    except Exception as e:
        print(f'Error listing UIDs: {e}')
        return []
    
def analyze_with_gemini(api_key, email_subject, email_body, attachments_text, case_id):
    """
    Analyze email content using Google Generative AI and include caseId in the prompt and response.
    """
    # Authenticate with the API key
    genai.configure(api_key=api_key)

    prompt = f"""
    You are an AI assistant specialized in understanding financial emails related to commercial banking loan servicing.
    Your task is to analyze the given email content and perform the following tasks:
 
    1. **Classify**: Determine the most appropriate **Request Type** and **Sub-Request Type**.
    2. **Following are the comma separated Request Types**:Loan Request, Loan Account Inquiry, Loan Modification, Loan Repayment, Loan Default, Loan Transfer, Collateral Issues, Loan Closure, Loan Status Inquiry, Loan Payment Issues, Loan Documentation, Loan Foreclosure, Settlements and Compromises (SETC).
    3. **Following are the comma separated Sub-Request Types**:New Loan Application, Loan Pre-Approval, Loan Balance Inquiry, Loan Payment Schedule, Interest Rate Information, Loan Account Statement, Loan Restructuring, Loan Forbearance, Interest Rate Adjustment, Loan Payoff Request, Partial Payment Inquiry, Payment Due Date Change, Late Payment Assistance, Loan Default Notification, Loan Transfer to Another Bank, Loan Assumption Inquiry, Title Release Request, Property Lien Removal, Loan Account Closure Confirmation, No Due Certificate Request, Application Status Check, Disbursement Status, Payment Not Reflected, Failed Auto-Debit, Loan Agreement Copy, Document Submission Confirmation, Foreclosure Charges Inquiry, Foreclosure Process, Loan Settlement Request, Debt Restructuring Proposal.
    4. **Summarize**: Provide a concise summary of the email.
    5. **Urgency**: Determine the urgency of the request based on the sender's language (High, Medium, Low).
    6. **Identify Intent**: Clearly state the sender's primary intent.
    7. **Perform Sentiment Analysis**: Classify sentiment as **Positive**, **Negative**, or **Neutral**.
    8. **Please extract any supporting content or key fields that would help substantiate the sender's claim or serve as proof. Look for information such as**:
 
        Payment Details: Any transaction IDs, payment confirmation numbers, or bank statements mentioned.
 
        Dates: Mention of specific dates or time frames (e.g., payment dates, requested resolution dates).
 
        Account Information: Account numbers, reference numbers, or other identifying details related to the service or transaction.
 
        Attachments: Any files, screenshots, or links that are referenced or attached that may serve as proof.
 
        Previous Correspondence: Mentions of previous interactions or case numbers.
 
        Other Supporting Evidence: Any statements that indicate the sender has proof of their claim (e.g., "I have attached the receipt," "I was charged incorrectly on my statement," etc.).

        Add these additonal information only if it is revelant and nessesary and add new liner for each information.

    **Email Details**:
    - Case ID: {case_id}
    - Subject: {email_subject}
    - Body: {email_body}
    - Attachments (Extracted Text if Applicable): {attachments_text}

    **Output Format**:
    {{
      "caseId": "{case_id}",
      "request_type": "string",
      "sub_request_type": "string",
      "summary": "string",
      "Urgency": "string",
      "intent": "string",
      "sentiment": "string",
      "additional_info": "string",
      "confidence": float,
      "error": "string"
    }}
    """

    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-001")
        response = model.generate_content(prompt)

        # Log the raw response for debugging
        #print("Raw response:", response)
        # Check and log the data type of response.text
        #print("Data type of response:", type(response))

        # Log the raw response for debugging
        print("Raw response from Gemini:", response.text)
        # Check and log the data type of response.text
        print("Data type of response.text:", type(response.text))

        # Covert the response to JSON
        parsed_response = parse_gemini_response(response.text)  # Fix the function call
        # Log the converted JSON
        print("Converted JSON:", parsed_response)
        
        return parsed_response
    except json.JSONDecodeError:
        # Log the raw response if parsing fails
        print("Error: Failed to parse response from Gemini. Raw response was not in JSON format.")
        #print("Raw response:", response.text)
        return {"caseId": case_id, "error": "Failed to parse response"}
    except Exception as e:
        print(f"Error: {e}")
        return {"caseId": case_id, "error": str(e)}

def main(data):
    """
    Main function to process the payload.
    :param data: Dictionary containing Salesforce payload.
    """
    try:
        mail = connect_to_gmail()
        # Extract UID and caseId from the payload
        uid = data.get("UID__c")
        case_id = data.get("caseId")
        if not uid or not case_id:
            print("Error: UID__c or caseId is missing from the payload.")
            return

        # List UIDs to verify
        uids = list_email_uids(mail)
        if uid not in uids:  # Compare as strings
            print(f'Provided UID {uid} is not valid. Please use one of the available UIDs: {uids}')
            return

        # Fetch and process the email by UID
        uid_folder = fetch_and_save_email_by_uid(mail, uid)
        if not uid_folder:
            print("Error: Failed to fetch and save email.")
            return

        # Process all .eml and .txt files in the folder
        api_key = "Replace with your valid API key"  # Replace with your valid API key
        salesforce_client = SalesforceAPIClient(
            instance_url="Replace with your salesforce Instance",  # Replace with your Salesforce instance URL
            access_token="Replace with access token"  # Replace with your Salesforce access token
        )
        process_eml_and_txt_files_in_folder(uid_folder, api_key, case_id, salesforce_client)
    except Exception as e:
        print(f"Error in main processing: {e}")
    finally:
        mail.logout()

if __name__ == '__main__':
    main()
    # Example usage to list models
    #api_key = "Replace with your valid API key"  # Replace with your valid API key
    #list_available_models(api_key)
