import os
from dotenv import load_dotenv

load_dotenv()  # read .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SLACK_WEBHOOK  = os.getenv("SLACK_WEBHOOK_URL")
EMAIL_USER     = os.getenv("EMAIL_USER")
EMAIL_PASS     = os.getenv("EMAIL_PASS")

# Dummy API base URLs
FAKE_STORE_URL = "https://fakestoreapi.com"
DUMMY_JSON_URL = "https://dummyjson.com"
