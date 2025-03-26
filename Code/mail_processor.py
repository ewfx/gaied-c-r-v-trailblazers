import imaplib
import email
import os
import re  # Add this import for sanitizing filenames
from document_processor import extract_text_from_pdf  # Import the function from document_processor

# Gmail IMAP server details
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# Configuration
EMAIL_ACCOUNT = 'hackathonwf@gmail.com'
PASSWORD = 'psea ivmc pfyl zyvq'  # Replace with the generated app password
UID = '22'  # Replace with a valid UID from the list
SAVE_DIR = r'C:\Users\SATHISH JAYAPAL\OneDrive\Documents\Hackathon\mailStorage'

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

def fetch_and_save_email_by_uid(mail, uid):
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
        project_id = "astute-anchor-454305-s2"  # Replace with your Google Cloud project ID
        processor_id = "21b59efa90354825"  # Replace with your Document AI processor ID
        location = "us"  # Adjust if your processor is in a different location
        process_pdfs_in_folder(uid_folder, project_id, processor_id, location)
    except Exception as e:
        print(f'Error fetching or saving email: {e}')

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

def main():
    mail = connect_to_gmail()
    # List UIDs to verify
    uids = list_email_uids(mail)
    if UID not in uids:  # Compare as strings
        print(f'Provided UID {UID} is not valid. Please use one of the available UIDs: {uids}')
        mail.logout()
        return

    fetch_and_save_email_by_uid(mail, UID)
    mail.logout()

if __name__ == '__main__':
    main()
