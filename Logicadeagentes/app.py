from flask import Flask, request, jsonify
import os
from constants import positions
from Evidencia2_Sinservidor import start

app = Flask(__name__)

# Folder to save uploaded images
UPLOAD_FOLDER_startingViews = 'uploads'
if not os.path.exists(UPLOAD_FOLDER_startingViews):
    os.makedirs(UPLOAD_FOLDER_startingViews)

# Route to receive the image from Unity
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

@app.route('/move', methods=['POST'])
def move_object():
    global positions
    start()
    return jsonify({'status': 'success'})

@app.route('/move', methods=['GET'])
def get_position():
    if positions:
        return jsonify(positions.pop(0))
    else:
        return jsonify({'status': 'error'}), 404
    
@app.route('/move', methods=['PUT'])
def delete_positions():
    global positions
    positions.clear()

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000) 