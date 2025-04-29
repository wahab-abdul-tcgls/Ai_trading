import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("UPSTOX_API_KEY")
API_SECRET = os.getenv("UPSTOX_API_SECRET")
REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")
AUTH_CODE = os.getenv("UPSTOX_AUTH_CODE")

url = "https://api.upstox.com/v2/login/authorization/token"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {
    "code": AUTH_CODE,
    "client_id": API_KEY,
    "client_secret": API_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code"
}

response = requests.post(url, headers=headers, data=data)
print(response.json())
