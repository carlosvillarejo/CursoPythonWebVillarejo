import requests

response = requests.get('https://api.github.com')

propiedades = {"status": response.status_code,"content/body": response.text}

print(f"Propiedades: {propiedades}")

