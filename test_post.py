import requests

url = 'http://localhost:8000/take_action'
data = {
    "action": "asdf"
}

response = requests.post(url, json=data)
json_response = response.json()
observation = json_response.get("observation")

print(observation)
