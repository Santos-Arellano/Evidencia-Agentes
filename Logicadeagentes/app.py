from flask import Flask, request, jsonify
import os
from constants import positions
from Evidencia2_Sinservidor import start
import shutil
import subprocess

app = Flask(__name__)

# Folder to save uploaded images
UPLOAD_FOLDER_startingViews = 'uploads'
if not os.path.exists(UPLOAD_FOLDER_startingViews):
    os.makedirs(UPLOAD_FOLDER_startingViews)

# Folder to save uploaded drone images
UPLOAD_FOLDER_droneViews = 'droneUploads'
if not os.path.exists(UPLOAD_FOLDER_droneViews):
    os.makedirs(UPLOAD_FOLDER_droneViews)

# Route to receive the image from Unity (starting views)
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image file found'}), 400
    
    image_file = request.files['image']

    if image_file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    save_path = os.path.join(UPLOAD_FOLDER_startingViews, image_file.filename)
    image_file.save(save_path)
    
    return jsonify({'status': 'success', 'message': f'Image saved at {save_path}'})

# Route to receive the drone image from Unity (drone views)
@app.route('/upload_drone_image', methods=['POST'])
def upload_drone_image():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image file found'}), 400

    image_file = request.files['image']

    if image_file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    # Save the image with the filename provided by Unity
    save_path = os.path.join(UPLOAD_FOLDER_droneViews, image_file.filename)
    
    try:
        # Save the image
        image_file.save(save_path)
        print(f"Drone image saved at: {save_path}")  # Log the save action
    except Exception as e:
        print(f"Error saving the image: {e}")
        return jsonify({'status': 'error', 'message': f"Failed to save the image: {str(e)}"}), 500

    # Trigger the OpenAI batch processor after the image is uploaded
    try:
        # Run the external OpenAI batch script
        process = subprocess.Popen(['python', '../vision_model/demo.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()  # Capture stdout and stderr

        if process.returncode == 0:
            print("OpenAI batch processor finished successfully")
            print(f"Output: {stdout.decode('utf-8')}")
        else:
            print(f"OpenAI batch processor failed with return code {process.returncode}")
            print(f"Error: {stderr.decode('utf-8')}")
            return jsonify({'status': 'error', 'message': 'Failed to complete OpenAI batch processor'}), 500

    except Exception as e:
        print(f"Error starting OpenAI batch processor: {e}")
        return jsonify({'status': 'error', 'message': f"Error starting OpenAI batch processor: {str(e)}"}), 500


    except Exception as e:
        print(f"Error starting OpenAI batch processor: {e}")
        return jsonify({'status': 'error', 'message': f"Error starting OpenAI batch processor: {str(e)}"}), 500
    
    # Return success response
    return jsonify({'status': 'success', 'message': f'Drone image saved at {save_path}'}), 200



# Route to clear the folders for starting views and drone images
@app.route('/clear_folders', methods=['POST'])
def clear_folders():
    try:
        # Clear the 'uploads' folder
        for filename in os.listdir(UPLOAD_FOLDER_startingViews):
            file_path = os.path.join(UPLOAD_FOLDER_startingViews, filename)
            os.remove(file_path)

        # Clear the 'droneUploads' folder
        for filename in os.listdir(UPLOAD_FOLDER_droneViews):
            file_path = os.path.join(UPLOAD_FOLDER_droneViews, filename)
            os.remove(file_path)

        return jsonify({'status': 'success', 'message': 'Folders cleared successfully'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

    
# Route to start the simulation and move objects
@app.route('/move', methods=['POST'])
def move_object():
    global positions
    start()
    return jsonify({'status': 'success'})

# Route to get the current position
@app.route('/move', methods=['GET'])
def get_position():
    if positions:
        return jsonify(positions.pop(0))
    else:
        return jsonify({'status': 'error', 'message': 'No positions available'}), 404

# Route to clear the positions
@app.route('/move', methods=['PUT'])
def delete_positions():
    global positions
    positions.clear()

    return jsonify({'status': 'success', 'message': 'Positions cleared'})

# Route to handle capture trigger (POST)
@app.route('/trigger_capture', methods=['GET', 'POST'])
def trigger_capture():
    if request.method == 'POST':
        data = request.get_json()
        if data and data.get('action') == 'capture':
            print("Capture trigger received via POST")
            return jsonify({'status': 'success'}), 200
    elif request.method == 'GET':
        print("Capture trigger received via GET")
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'failure', 'message': 'Invalid request'}), 400


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)


