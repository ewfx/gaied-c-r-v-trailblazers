import imaplib
import email
import os
import pytesseract
from pdfminer.high_level import extract_text
from PIL import Image
from io import BytesIO
from docx import Document

class MailExtractorWithAttachmentProcessing:
    def __init__(self, mail_server, email_id, password, uid_log_file):
        self.mail_server = mail_server
        self.email_id = email_id
        self.password = password
        self.uid_log_file = uid_log_file
        self.processed_uids = self.load_processed_uids()

    def load_processed_uids(self):
        if os.path.exists(self.uid_log_file):
            with open(self.uid_log_file, "r") as file:
                return set(file.read().splitlines())
        return set()

    def save_processed_uid(self, uid):
        with open(self.uid_log_file, "a") as file:
            file.write(f"{uid}\n")

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.mail_server)
        self.mail.login(self.email_id, self.password)
        self.mail.select("inbox")

    def fetch_emails(self):
        result, data = self.mail.uid("search", None, "ALL")
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
        print(f"Processing email: {subject}")

        # Save and process attachments
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename:
                    file_data = part.get_payload(decode=True)
                    self.process_attachment(filename, file_data)

        # Mark UID as processed
        self.processed_uids.add(uid)
        self.save_processed_uid(uid)

    def process_attachment(self, filename, file_data):
        print(f"Processing attachment: {filename}")
        if filename.endswith(".pdf"):
            self.extract_from_pdf(file_data)
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            self.extract_from_image(file_data)
        elif filename.endswith(".docx"):
            self.extract_from_word(file_data)
        else:
            print(f"Unsupported file type: {filename}")

    def extract_from_pdf(self, file_data):
        with open("temp.pdf", "wb") as temp_file:
            temp_file.write(file_data)
        text = extract_text("temp.pdf")
        os.remove("temp.pdf")
        print(f"Extracted text from PDF:\n{text}")

    def extract_from_image(self, file_data):
        image = Image.open(BytesIO(file_data))
        text = pytesseract.image_to_string(image)
        print(f"Extracted text from image:\n{text}")

    def extract_from_word(self, file_data):
        with open("temp.docx", "wb") as temp_file:
            temp_file.write(file_data)
        doc = Document("temp.docx")
        os.remove("temp.docx")
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        print(f"Extracted text from Word document:\n{text}")

    def close_connection(self):
        self.mail.logout()

# Example usage:
# extractor = MailExtractorWithAttachmentProcessing(
#     "imap.gmail.com", "your-email@gmail.com", "your-password", "uid_log.txt"
# )
# extractor.connect()
# extractor.fetch_emails()
# extractor.close_connection()
