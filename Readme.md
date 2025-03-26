🎯 **Introduction** Our Gen AI-powered email classification and OCR solution is designed to automate email triage in commercial bank lending services. By leveraging AI, the solution classifies emails, extracts relevant data from emails and attachments, detects primary intent, handles multi-request emails, implements priority-based extraction, identifies duplicate emails, and integrates Google Gemini AI API for enhanced classification accuracy.

- ![image](https://github.com/user-attachments/assets/1be3a716-64e7-46fc-9eb9-cd1b8bcc7585)
- 
🎥 **Demo**
- 📹 Video Demo: 
https://github.com/ewfx/gaied-c-r-v-trailblazers/blob/main/Recordings/video2706239219.mp4


💡 **Inspiration** Commercial bank lending operations receive a high volume of emails with multiple attachments, often requiring manual processing. Our solution reduces human effort, minimizes errors, and accelerates email triage through intelligent automation.

⚙️ **What It Does**

- Classifies emails using AI-driven intent recognition
- Extracts key information from email bodies and attachments using OCR
- Detects and handles multi-request emails
- Implements priority-based data extraction
- Identifies and flags duplicate emails
- Provides accurate sentiment analysis

🛠️ **How We Built It**

Implementation Details:

• Salesforce Integration:

o Utilize Salesforce's REST API to send notifications to the Python service upon case creation.

o The Python service can use the simple-salesforce library to interact with Salesforce for case updates.

• Email Retrieval:

o The Python service connects to the mail server using protocols like IMAP to fetch the email content and attachments.

• File Storage:

o Organize emails and attachments in directories named by unique identifiers to maintain a structured file system.

• Google Document AI Integration:

o Use the Google Cloud Document AI Python client library to process attachments and extract text.

• Email Extraction + Classification with Gemini API:

o Leverage Google's Gemini API to classify email content into predefined categories.

• Google Vertex AI Platform:

o Utilize Vertex AI for the pretrained models

• Salesforce Duplicate Management:

o Implement Salesforce's Duplicate Management features to identify and handle duplicate cases, ensuring data integrity and preventing redundant processing. 

• Omni-Channel Routing and Prioritization:

o Configure Salesforce's Omni-Channel to route and prioritize cases to agents based on predefined routing configurations, agent skills, and availability. 

🚧 **Challenges We Faced**

- Ensuring accurate intent classification for diverse email content
- Extracting relevant data from complex attachments
- Managing API response latency
- Model evaluation from the public available LLM's

🏃 **How to Run**

1. Clone the repository:

git clone https://github.com/ewfx/gaied-c-r-v-trailblazers.git

1. Install dependencies:

pip install -r requirements.txt

1. Run the project:

uvicorn main:app --reload

🏗️ **Tech Stack**

- 🔹 **Frontend:** Salesforce Case Managament
- 🔹 **Backend:**  Salesforce + Python
- 🔹 **Database:** Salesforce
- 🔹 **AI Services:** Google Gemini AI API + Document AI + Vertex AI 
- 🔹 **OCR:** google Document AI
- 🔹 **AI Platform:** Google Cloud Vertex AI

👥 **Team**

- Team Name - CRV Trailblazers
- Teammate - 
- ` `Rajesh J 
- Yashmith Kumar
- Avinash Mishra
- Narasimha Gundurao
- Shashikanth BK

