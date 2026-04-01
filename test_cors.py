import requests

url = "http://localhost:5000/api/login"
headers = {
    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "Content-Type"
}

try:
    response = requests.options(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Headers:")
    for key, value in response.headers.items():
        if "Access-Control" in key:
            print(f"  {key}: {value}")
except Exception as e:
    print(f"Error: {e}")
