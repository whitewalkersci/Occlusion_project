import requests

url = 'http://127.0.0.1:5000/process_image'
image_path = '/home/whitewalker/Desktop/Sciverse_2/Occlusion_project/final_pipeline/assets/merged/Specimen_001.tif'
payload = {'image_path': image_path}
response = requests.post(url, json=payload)

print(response.json())



# sections_image_path = ['/home/whitewalker/Desktop/Sciverse_2/API/database/sections/3.png', '/home/whitewalker/Desktop/Sciverse_2/API/database/sections/2.png', '/home/whitewalker/Desktop/Sciverse_2/API/database/sections/1.png', '/home/whitewalker/Desktop/Sciverse_2/API/database/sections/0.png']
# url = 'http://127.0.0.1:5000/process_analysis'
# payload = {'sections_image_path': sections_image_path}
# response = requests.post(url, json=payload)

# print(response.json())