import requests

def list_available_models():
    api_key = "AIzaSyBVqdeZ90TK7H510tZOtZyrZvQHuQQIz9Y"
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print("Available Models:")
        for model in models:
            print(f"Model: {model['name']}, Description: {model.get('description', 'No Description')}")
    else:
        print(f"Failed to fetch models. Error: {response.text}")

if __name__ == '__main__':    
    list_available_models()
    