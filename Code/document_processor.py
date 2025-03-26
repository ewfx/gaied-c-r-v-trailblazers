from google.cloud import documentai

def extract_text_from_pdf(file_path, project_id, processor_id, location="us"):
    client = documentai.DocumentProcessorServiceClient()
    with open(file_path, "rb") as f:
        file_content = f.read()

    raw_document = documentai.RawDocument(content=file_content, mime_type="application/pdf")
    request = documentai.ProcessRequest(
        name=f"projects/{project_id}/locations/{location}/processors/{processor_id}",
        raw_document=raw_document
    )
    result = client.process_document(request=request)
    return result.document.text

if __name__ == "__main__":
    # file_path = r"C:\Users\SATHISH JAYAPAL\OneDrive\Documents\Hackathon\DocumentCloud\File1.pdf"  # Path to your PDF file
    # file_path = r"C:\Users\SATHISH JAYAPAL\OneDrive\Documents\Hackathon\DocumentCloud\Commercial Loan Request for Business Expansion.eml"  # Path to your PDF file
    project_id = "project_id"
    processor_id = "processor_id"
    location = "us"  # Adjust if your processor is in a different location

    text = extract_text_from_pdf(file_path, project_id, processor_id, location)
    print("Extracted Text:")
    print(text)

