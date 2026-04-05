from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Mongo URI securely
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise EnvironmentError(
        "MONGO_URI environment variable is not set. "
        "Add it to your .env file or export it before running the app."
    )

# Create MongoDB client
client = MongoClient(MONGO_URI)

# Select database
db = client["farmwisely"]

# Collections
cases_collection = db["cases"]
raw_collection = db["raw_submissions"]

# ===========================
# ✅ NEW: HELPER FUNCTIONS
# ===========================

def get_cases_collection():
    """Return cases collection (for CBR engine)"""
    return cases_collection


def get_raw_collection():
    """Return raw submissions collection"""
    return raw_collection


def insert_case(case_data):
    """Insert processed anonymized case"""
    return cases_collection.insert_one(case_data)


def insert_raw_submission(data):
    """Store raw (non-anonymized) data before processing"""
    return raw_collection.insert_one(data)


def fetch_all_cases():
    """Fetch all cases (used in similarity matching)"""
    return list(cases_collection.find({}))


def fetch_cases_by_crop(crop):
    """Filter cases by crop (optimization for CBR)"""
    return list(cases_collection.find({"context.crop": crop}))


def close_connection():
    """Close MongoDB connection (optional cleanup)"""
    client.close()