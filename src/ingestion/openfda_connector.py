import requests
import json
import os

# Configuration
API_URL = "https://api.fda.gov/drug/enforcement.json"
LIMIT = 200
SEARCH_TERMS = [
    "reason_for_recall:impurity",
    "reason_for_recall:impurities",
    "reason_for_recall:sterility",
    "reason_for_recall:sterile",
    "reason_for_recall:cgmp",
    "reason_for_recall:gmp",
    "reason_for_recall:batch",
    "reason_for_recall:contamination",
    "reason_for_recall:microbial",
    "reason_for_recall:failed"
]

# Path handling for Data Science scaffold
# Script is in src/ingestion/, data is in data/raw/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_FILE = os.path.join(DATA_DIR, "fda_quality_events.json")

def fetch_data():
    """Fetches data from openFDA API."""
    # Construct query: (term1) OR (term2) ...
    # requests will URL-encode the spaces to + or %20 which is acceptable
    search_query = " OR ".join(SEARCH_TERMS)
    
    params = {
        "search": search_query,
        "limit": LIMIT
    }
    
    print(f"Fetching data from {API_URL}...")
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def extract_fields(record):
    """Extracts relevant fields from a single API record."""
    reason = record.get("reason_for_recall", "")
    desc = record.get("product_description", "")
    
    # Simple logic to determine failure type base on matched keyword in reason
    failure_type = "Other Quality Issue"
    lower_reason = reason.lower()
    
    if any(x in lower_reason for x in ["impurity", "impurities", "contamination"]):
        failure_type = "Impurity/Contamination"
    elif any(x in lower_reason for x in ["sterility", "sterile", "microbial"]):
        failure_type = "Sterility Issue"
    elif any(x in lower_reason for x in ["cgmp", "gmp"]):
        failure_type = "CGMP Violation"
    elif "batch" in lower_reason:
        failure_type = "Batch Record Issue"
    elif "failed" in lower_reason:
         failure_type = "Specification Failure"

    return {
        "event_id": record.get("event_id"),
        "recall_number": record.get("recall_number"),
        "recalling_firm": record.get("recalling_firm"),
        "status": record.get("status"),
        "classification": record.get("classification"),
        "reason_for_recall": reason,
        "product_description": desc,
        "failure_type": failure_type,
        "report_date": record.get("report_date"),
        "country": record.get("country"),
        "state": record.get("state"),
        "city": record.get("city")
    }

def main():
    data = fetch_data()
    
    if data and "results" in data:
        results = data["results"]
        print(f"Found {len(results)} records.")
        
        extracted_data = [extract_fields(r) for r in results]
        
        # Save to file
        with open(OUTPUT_FILE, "w") as f:
            json.dump(extracted_data, f, indent=4)
        
        print(f"Successfully saved {len(extracted_data)} records to {OUTPUT_FILE}")
    else:
        print("No results found or error occurred.")

if __name__ == "__main__":
    main()
