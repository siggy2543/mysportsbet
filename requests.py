import requests

def fetch_espn_data():
    # Replace `your_api_key` and `endpoint_url` with actual values
    headers = {'Authorization': 'Bearer your_api_key'}
    response = requests.get('endpoint_url', headers=headers)
    return response.json()

# Use scheduler like Celery or a cronjob to preiodically fetch data
# and update your app's database or in-memory store

response = requests.get('https://api.example.com/teams')
data = response.json()