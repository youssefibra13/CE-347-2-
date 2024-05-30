from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def receive_data():
    # Retrieve the 'top' and 'bottom' form data
    top = request.form.get('top')
    bottom = request.form.get('bottom')
    
    # Retrieve the file from the form data
    model_file = request.files.get('model')

    if top is None or bottom is None or model_file is None:
        return jsonify({'error': 'Missing data'}), 400

    # Save the uploaded file
    model_file.save(f'recv_folder\\{model_file.filename}')
    
    # Convert 'top' and 'bottom' to integers (if needed)
    try:
        top = int(top)
        bottom = int(bottom)
    except ValueError:
        return jsonify({'error': 'Invalid number format for top or bottom'}), 400

    # Respond with a JSON object confirming receipt
    response = {
        'message': 'Data received successfully',
        'top': top,
        'bottom': bottom,
        'model_filename': model_file.filename
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host = '127.0.0.1', port=3300, debug=True)
