import requests

# url = 'http://127.0.0.1:5001/process_image'
# image_path = '/home/whitewalker/Desktop/Sciverse_2/Specimen_001.tif'
# payload = {'image_path': image_path}
# response = requests.post(url, json=payload)

# print(response.json())


# Define the input JSON
input_data = {
    'specimen_name': 'Specimen_001',
    'sections_image_path': [
        '/home/whitewalker/Desktop/Sciverse_2/Occlusion_project/database/Specimen_001/sections_images/4.png',
        '/home/whitewalker/Desktop/Sciverse_2/Occlusion_project/database/Specimen_001/sections_images/3.png',
        '/home/whitewalker/Desktop/Sciverse_2/Occlusion_project/database/Specimen_001/sections_images/2.png',
        '/home/whitewalker/Desktop/Sciverse_2/Occlusion_project/database/Specimen_001/sections_images/1.png'
    ]
}
url_2 = 'http://127.0.0.1:5001/process_analysis'
payload_2 = input_data
response_2 = requests.post(url_2, json=payload_2)

print(response_2)