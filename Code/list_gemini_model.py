import google.generativeai as genai
import os

def configure_api():
    api_key = "AIzaSyBVqdeZ90TK7H510tZOtZyrZvQHuQQIz9Y"
    if not api_key:
        print("API key not found. Please set GEMINI_API_KEY as an environment variable.")
        exit()
    try:
        genai.configure(api_key=api_key)
        print("API configured successfully.")
    except Exception as e:
        print(f"Error configuring API: {e}")
        raise

def test_gemini_model():
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-001')
        response = model.generate_content("Explain the concept of compound interest.")
        print("Model Response:", response.text)
    except Exception as e:
        print(f"Error using Gemini Pro: {e}")

if __name__ == '__main__':
    configure_api()    
    test_gemini_model()
