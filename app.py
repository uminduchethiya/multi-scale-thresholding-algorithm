import os
from flask import Flask, request, render_template
import numpy as np
from PIL import Image
import base64
import cv2

app = Flask(__name__)

def treshold(Thresholds, img_array):
    results = []  # Placeholder for tresh results

    for threshold in Thresholds:
        _, binary_image = cv2.threshold(img_array, threshold, 255, cv2.THRESH_BINARY)
        results.append(binary_image)

    return results

# Define a route for the main page
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')

        file = request.files['file']

        # Check if the file has a name
        if file.filename == '':
            return render_template('index.html', error='No selected file')

        # Check if the file is allowed
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return render_template('index.html', error='Invalid file extension')

        # Save the file to a temporary location
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        try:
            img = Image.open(file_path).convert("L")
            img_array = np.asarray(img)
        except Exception as e:
            return render_template('index.html', error=f"Error opening or converting image: {e}")

        # Perform treshold calculation
        thresholds = [50, 100, 150]
        results = treshold(thresholds, img_array)

        # Save the results to different files
        result_paths = []
        for idx, result in enumerate(results):
            result_filename = f"result_{idx + 1}.png"
            result_path = os.path.join('uploads', result_filename)
            cv2.imwrite(result_path, result)
            result_paths.append(result_path)

        # Convert the result paths to base64 for display in HTML
        encoded_result_paths = [base64.b64encode(open(result_path, 'rb').read()).decode('utf-8') for result_path in result_paths]

        # Encode the uploaded image data
        encoded_image = base64.b64encode(open(file_path, 'rb').read()).decode('utf-8')

        # Render the results
        return render_template('index.html', result_paths=encoded_result_paths, encoded_image=encoded_image)

    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
