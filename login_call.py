import requests

# Define the API URL
url = 'http://localhost:5001/login'

# JSON payload with username and password
payload = {'username': 'Dhruv', 'password': '123'}

# Send a POST request to the API
response = requests.post(url, json=payload)

# Print the response
print(response.json())


import requests

# Define the API URL for creating a user
create_user_url = 'http://localhost:5001/create_user'

# JSON payload with username and password for the new user
new_user_payload = {'username': 'Sham', 'password': '123'}

# Send a POST request to create a new user
create_user_response = requests.post(create_user_url, json=new_user_payload)

# Print the response
print(create_user_response.json())
