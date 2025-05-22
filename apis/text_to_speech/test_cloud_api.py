from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
# Path to your downloaded service account key
SERVICE_ACCOUNT_FILE = "api-client-key.json"

# Your private Cloud Run endpoint
TARGET_AUDIENCE = "https://buddy-milo-img-598905806145.europe-west4.run.app"

# Authenticate using the service account to get an identity token
credentials = service_account.IDTokenCredentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    target_audience=TARGET_AUDIENCE
)

credentials.refresh(Request())

# Prepare headers including Authorization and your custom API key
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "x-api-key": API_KEY
}

# File to upload
files = {
    "file": open("../../samples/test1.wav", "rb")
}

# Send POST request to /transcribe
response = requests.post(f"{TARGET_AUDIENCE}/transcribe", headers=headers, files=files)

# Print response
print("Status Code:", response.status_code)
print("Response:", response.text)
