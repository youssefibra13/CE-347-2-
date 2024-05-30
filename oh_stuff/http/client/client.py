import requests

# Define the endpoint URL of the remote server
url = 'https://agents.socratics.ai:8080/ootd'

# Define the data to be sent
data = {
    'lower_body': 'https://raw.githubusercontent.com/levihsu/OOTDiffusion/main/run/examples/garment/051946_1.jpg',   # Replace with your actual number
    'upper_body': 'https://raw.githubusercontent.com/levihsu/OOTDiffusion/main/run/examples/garment/00055_00.jpg'  # Replace with your actual number
}

# Define the file to be sent
files = {
    'body': ('model_8.png', open('model_8.png', 'rb'), 'image/png')
}

# Send the POST request with data and file
response = requests.post(url, data=data, files=files)

# Check the response
if response.status_code == 200:
    print('Data sent successfully!')
    f = open('image_output_y.jpg', 'wb')
    f.write(response.content)
    f.close()
else:
    print('Failed to send data. Status code:', response.status_code)
    print('Response:', response.text)
