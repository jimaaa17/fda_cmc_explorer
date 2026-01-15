import requests
import json
import os

class OpenFDAConnector:
    """Fetch real enforcement data from openFDA API"""
    
    BASE_URL = "https://api.fda.gov"
    
    @staticmethod
    def get_drug_enforcement(search_terms, limit=100):
        """Fetch drug enforcement records matching quality issues"""
        url = f"{OpenFDAConnector.BASE_URL}/drug/enforcement.json"
        
        # Construct query: (term1) OR (term2) ...
        # Join terms with OR
        search_query = " OR ".join(search_terms)
        
        params = {
            "search": f'reason_for_recall:({search_query})',
            "limit": limit
        }
        
        print(f"Fetching data from {url} with params: {params}")
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    @staticmethod
    def get_all_enforcement_by_reason(limit=500):
        """
        Fetches a large sample of enforcement reports to manually aggregate reasons,
        since the API does not support counting on text fields.
        """
        url = f"{OpenFDAConnector.BASE_URL}/drug/enforcement.json"
        
        # We fetch records, not counts
        params = {
            "limit": limit,
             # We only need the reason field to analyze
            "search": "_exists_:reason_for_recall"
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching aggregate sample: {e}")
            return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching aggregation data: {e}")
            return None

# Configuration
SEARCH_TERMS = [
    "impurity",
    "impurities",
    "sterility",
    "sterile",
    "cgmp",
    "gmp",
    "batch",
    "contamination",
    "microbial",
    "failed"
]
LIMIT = 200

# Path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_FILE = os.path.join(DATA_DIR, "fda_quality_events.json")

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
        "city": record.get("city"),
        "openfda_id": record.get("id", "") # Capture ID for linking
    }

def main():
    print("Starting OpenFDA Ingestion...")
    data = OpenFDAConnector.get_drug_enforcement(SEARCH_TERMS, LIMIT)
    
    if data and "results" in data:
        results = data["results"]
        print(f"Found {len(results)} records.")
        
        extracted_data = [extract_fields(r) for r in results]
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Save to file
        with open(OUTPUT_FILE, "w") as f:
            json.dump(extracted_data, f, indent=4)
        
        print(f"Successfully saved {len(extracted_data)} records to {OUTPUT_FILE}")
    else:
        print("No results found or error occurred.")

if __name__ == "__main__":
    main()
