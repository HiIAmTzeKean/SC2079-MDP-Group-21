import requests


ip_address = "192.168.21.25:5000"  # Replace with the actual IP address
endpoint = "path"  # Replace with the actual endpoint
url = f"http://{ip_address}/{endpoint}"

body = {
    "obstacles": [
        {
            "x": 19,
            "y": 19,
            "d": 6,
            "id": 1
        }
    ]
}

content_type = "application/json"
headers = {
    "Content-Type": content_type
}
response = requests.post(url, json=body)
print(response.text)