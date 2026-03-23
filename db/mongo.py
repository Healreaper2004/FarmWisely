from pymongo import MongoClient
import os
from dotenv import load_dotenv   # ✅ ADD THIS

load_dotenv()  # ✅ ADD THIS

# ⚠️ Never hardcode credentials
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise EnvironmentError(
        "MONGO_URI environment variable is not set. "
        "Add it to your .env file or export it before running the app."
    )

client = MongoClient(MONGO_URI)

db = client["farmwisely"]

cases_collection = db["cases"]
raw_collection   = db["raw_submissions"]