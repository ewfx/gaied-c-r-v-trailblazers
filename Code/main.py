from core.email_processor import process_email
from core.sentiment_analysis import analyze_sentiment
from core.intent_extraction import extract_intent
from core.image_analysis import analyze_attachments
from core.salesforce_integration import classify_and_route_case

def main():
    # Placeholder for email data
    email_data = {
        "subject": "Loan Application Issue",
        "body": "I need help with my loan application process.",
        "attachments": []
    }


    # Step 1: Process email content
    processed_email = process_email(email_data)

    # Step 2: Perform sentiment analysis
    sentiment = analyze_sentiment(processed_email["body"])

    # Step 3: Extract intent
    intent = extract_intent(processed_email["body"])

    # Step 4: Analyze attachments (if any)
    if email_data["attachments"]:
        attachment_analysis = analyze_attachments(email_data["attachments"])
    else:
        attachment_analysis = None

    # Step 5: Classify and route case
    classify_and_route_case(processed_email, sentiment, intent, attachment_analysis)

if __name__ == "__main__":
    main()
