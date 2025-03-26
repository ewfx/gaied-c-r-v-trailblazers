import imaplib
import email
import os
import json
import pytesseract
import requests
import mysql.connector
from pdfminer.high_level import extract_text
from PIL import Image
from io import BytesIO
from docx import Document
import google.generativeai as genai
from email.utils import decode_rfc2231

# Configure Gemini API
genai.configure(api_key="YOUR_GEMINI_API_KEY")

class EmailProcessor:
    def __init__(self, mail_server, email_id, password, uid_log_file, gemini_api_url, mysql_config):
        self.mail_server = mail_server
        self.email_id = email_id
        self.password = password
        self.uid_log_file = uid_log_file
        self.gemini_api_url = gemini_api_url
        self.mysql_config = mysql_config
        self.processed_uids = self.load_processed_uids()

    def load_processed_uids(self):
        if os.path.exists(self.uid_log_file):
            with open(self.uid_log_file, "r") as file:
                return set(file.read().splitlines())
        return set()

    def save_processed_uid(self, uid):
        with open(self.uid_log_file, "a") as file:
            file.write(f"{uid}\n")

    def connect_to_mail(self):
        self.mail = imaplib.IMAP4_SSL(self.mail_server)
        self.mail.login(self.email_id, self.password)
        self.mail.select("inbox")

    def fetch_emails(self):
        result, data = self.mail.uid("search", None, "UNSEEN")  # Fetch only unread emails
        if result != "OK":
            print("Failed to fetch emails.")
            return

        uids = data[0].split()
        for uid in uids:
            uid = uid.decode("utf-8")
            if uid in self.processed_uids:
                continue

            result, msg_data = self.mail.uid("fetch", uid, "(RFC822)")
            if result != "OK":
                print(f"Failed to fetch email with UID {uid}.")
                continue

            raw_email = msg_data[0][1]
            self.process_email(uid, raw_email)

    def process_email(self, uid, raw_email):
        msg = email.message_from_bytes(raw_email)
        subject = msg["subject"]
        body = self.extract_email_body(msg)
        print(f"Processing email: {subject}")

        attachments_data = []
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename:
                    filename = decode_rfc2231(filename)  # Decode filename safely
                    file_data = part.get_payload(decode=True)
                    attachments_data.append(self.process_attachment(filename, file_data))

        gemini_response = self.analyze_with_gemini(subject, body, attachments_data)
        if gemini_response:
            self.store_in_database(uid, gemini_response)

        self.processed_uids.add(uid)
        self.save_processed_uid(uid)

    def extract_email_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() in ["text/plain", "text/html"]:
                    return part.get_payload(decode=True).decode(errors="ignore")
        return msg.get_payload(decode=True).decode(errors="ignore")

    def process_attachment(self, filename, file_data):
        print(f"Processing attachment: {filename}")
        if filename.endswith(".pdf"):
            return self.extract_from_pdf(file_data)
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            return self.extract_from_image(file_data)
        elif filename.endswith(".docx"):
            return self.extract_from_word(file_data)
        else:
            print(f"Unsupported file type: {filename}")
            return ""

    def extract_from_pdf(self, file_data):
        with open("temp.pdf", "wb") as temp_file:
            temp_file.write(file_data)
        try:
            text = extract_text("temp.pdf")
        except Exception:
            print("PDF extraction error, using alternative method.")
            from PyPDF2 import PdfReader
            reader = PdfReader("temp.pdf")
            text = "".join(page.extract_text() or "" for page in reader.pages)
        os.remove("temp.pdf")
        return text

    def extract_from_image(self, file_data):
        image = Image.open(BytesIO(file_data))
        return pytesseract.image_to_string(image)

    def extract_from_word(self, file_data):
        with open("temp.docx", "wb") as temp_file:
            temp_file.write(file_data)
        try:
            doc = Document("temp.docx")
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error extracting from Word document: {e}")
            text = ""
        os.remove("temp.docx")
        return text

    def analyze_with_gemini(self, email_subject, email_body, attachments_text):
        prompt = f"""
        You are an AI assistant specialized in understanding financial emails related to commercial banking loan servicing. 
        Your task is to analyze the given email content and perform the following tasks:

        1. **Classify**: Determine the most appropriate **Request Type** and **Sub-Request Type**.
        2. **Summarize**: Provide a concise summary of the email.
        3. **Identify Intent**: Clearly state the sender's primary intent.
        4. **Perform Sentiment Analysis**: Classify sentiment as **Positive**, **Negative**, or **Neutral**.

        **Email Details**:
        - Subject: {email_subject}
        - Body: {email_body}
        - Attachments (Extracted Text if Applicable): {attachments_text}

        **Output Format**:
        {{
          "request_type": "string",
          "sub_request_type": "string",
          "summary": "string",
          "intent": "string",
          "sentiment": "string",
          "confidence": float,
          "error": "string"
        }}
        """

        try:
            model = genai.ChatModel(model_name="gemini-pro")
            response = model.start_chat().send_message(prompt)
            return json.loads(response.text)
        except json.JSONDecodeError:
            print("Error: Failed to parse response from Gemini.")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def store_in_database(self, uid, gemini_response):
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            cursor = connection.cursor()

            query = """
            INSERT INTO email_processing_results (uid, request_type, request_sub_type, summarisation, sentiment_analysis)
            VALUES (%s, %s, %s, %s, %s)
            """
            data = (
                uid,
                gemini_response.get("request_type"),
                gemini_response.get("sub_request_type"),
                gemini_response.get("summary"),
                gemini_response.get("sentiment"),
            )
            cursor.execute(query, data)
            connection.commit()
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def close_mail_connection(self):
        self.mail.logout()

# Example Usage
# mysql_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "your-password",
#     "database": "email_processing"
# }
# processor = EmailProcessor(
#     "imap.gmail.com", "your-email@gmail.com", "your-password", "uid_log.txt",
#     "https://gemini-api-url.com/process", mysql_config
# )
# processor.connect_to_mail()
# processor.fetch_emails()
# processor.close_mail_connection()
