import requests

url = 'http://127.0.0.1:5000/process_image'
image_path = 'Specimen_001.tif'
payload = {'image_path': image_path}
response = requests.post(url, json=payload)
print(response)
# print(response.json())


# input_data = {
#     'specimen_name': 'Specimen_001',
#     'sections_image_path': [
#         r'C:\Users\PrashantMore\Desktop\API_builder\API_builder/Specimen_001\sections_images\4.png',
#         r'C:\Users\PrashantMore\Desktop\API_builder\API_builder\Specimen_001\sections_images\3.png',
#         r'C:\Users\PrashantMore\Desktop\API_builder\API_builder\Specimen_001\sections_images\2.png',
#         r'C:\Users\PrashantMore\Desktop\API_builder\API_builder\Specimen_001\sections_images\1.png'
#     ]
# }
# url_2 = 'http://127.0.0.1:5001/process_analysis'
# payload_2 = input_data
# response_2 = requests.post(url_2, json=payload_2)

# print(response_2.json())



# url = 'http://127.0.0.1:5000/result'
 
# input_data = {'project_key':1}
# response = requests.post(url,json=input_data)
 
# print(response.json())