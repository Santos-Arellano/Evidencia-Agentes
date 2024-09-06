import os
import base64
import json
import requests
import time
from PIL import Image
import io
import random

# Function to compress and encode an image in low-res mode (512x512)
def compress_and_encode_image_low_res(image_path, quality=70):
    try:
        # Open the image
        img = Image.open(image_path)

        # Resize the image to 512x512 for low-res mode
        img = img.resize((512, 512), Image.Resampling.LANCZOS)

        # Save it temporarily to a buffer in memory
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)  # Reduce quality for smaller size

        # Convert the buffer to base64
        base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return base64_image
    except Exception as e:
        print(f"Error compressing and encoding image {image_path} in low-res mode: {e}")
        return None

# Function to process a single image and send the request in low-res mode
def process_image_low_res(image_path, openai_url, openai_key):
    # Compress and encode the image in low-res mode
    base64_image = compress_and_encode_image_low_res(image_path)

    if not base64_image:
        print(f"Skipping image {image_path} due to encoding error in low-res mode.")
        return  # Skip processing if there was an error with encoding

    # Prepare the request data for low-res mode
    request_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": ("what is in this image?"
                )
            },
            {
                "role": "user",
                "content": f"data:image/jpeg;base64,{base64_image}"
            }
        ],
        "max_tokens": 85  # Lower token limit for low-res mode
    }

    try:
        # Send the request
        response = requests.post(
            openai_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}"
            },
            json=request_data
        )

        if response.status_code == 200:
            response_json = response.json()
            print(f"Low-res image {os.path.basename(image_path)} uploaded successfully.")
            print(f"Response: {json.dumps(response_json, indent=4)}")

            # Optional: Save the response JSON to a file
            json_save_path = os.path.join("responses", f"{os.path.basename(image_path)}.json")
            with open(json_save_path, 'w') as json_file:
                json.dump(response_json, json_file, indent=4)
            print(f"Response saved to {json_save_path}")

        elif response.status_code == 429:
            print(f"Rate limit hit for {os.path.basename(image_path)}. Retrying in low-res mode...")
            time.sleep(10)  # Retry logic
            process_image_low_res(image_path, openai_url, openai_key)
        else:
            print(f"Failed to upload the file {os.path.basename(image_path)}. Status code: {response.status_code}, Response: {response.text}")

    except Exception as e:
        print(f"An error occurred while sending the request for {os.path.basename(image_path)}: {e}")

# Function to pick a random image
def pick_random_image(images_dir):
    try:
        # Get the list of all image files in the directory
        image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

        # Check if the directory contains any images
        if not image_files:
            print("No images found in the directory.")
            return None

        # Pick a random image
        random_image = random.choice(image_files)
        random_image_path = os.path.join(images_dir, random_image)

        print(f"Randomly selected image: {random_image_path}")
        return random_image_path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to process images sequentially in low-res mode (now picks a random image)
def process_images_sequentially_low_res(images_dir, openai_url, openai_key):
    if not os.path.exists(images_dir):
        print(f"Error: The directory {images_dir} does not exist.")
        return

    # Create a directory to save the JSON responses if it doesn't exist
    if not os.path.exists('responses'):
        os.makedirs('responses')

    # Pick a random image from the folder
    random_image_path = pick_random_image(images_dir)

    if random_image_path:
        process_image_low_res(random_image_path, openai_url, openai_key)
    else:
        print("No image to process.")

if __name__ == "__main__":
    # Adjust these paths and credentials
    images_dir = os.path.abspath('droneUploads')
    openai_url = "https://api.openai.com/v1/chat/completions"

    # process_images_sequentially_low_res(images_dir, openai_url, openai_key)
