import requests
from dotenv import load_dotenv
import os
import base64

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Directory containing the images
images_dir = r'C:\Users\luzpa\OneDrive\Documentos\5to_uni\multiagentes\tec-2024B-1\assets\sample-images'

# Iterate over all files in the directory
for filename in os.listdir(images_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png')):  # Add other image extensions if necessary
        image_path = os.path.join(images_dir, filename)
        base64_image = encode_image(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"What’s in this image ({filename})?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        print(f"Response for {filename}:")
        print(response.json())
