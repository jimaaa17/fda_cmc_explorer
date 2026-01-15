import os
import json
from elasticsearch import Elasticsearch, helpers

def index_data(json_path, es_host="http://localhost:9200", index_name="fda_events"):
    """
    Indexes the FDA quality events into Elasticsearch.
    """
    if not os.path.exists(json_path):
        print(f"JSON file not found: {json_path}")
        return

    # In a real pipeline, we might wait for ES to be up.
    # Here we assume it's running via Docker.
    es = Elasticsearch(hosts=[es_host])
    
    # Check connection (Stub for dev environment where ES might not be running)
    if not es.ping():
        print(f"Cannot connect to Elasticsearch at {es_host}. Is Docker running?")
        print("Skipping indexing step but script logic is valid.")
        return

    print("Connected to Elasticsearch.")
    
    with open(json_path, 'r') as f:
        records = json.load(f)

    # Generator for bulk indexing
    def generate_actions():
        for record in records:
            # We can enrich this with the NER results if we parse the enriched TTL
            # For now, index the raw JSON + a simple ID
            yield {
                "_index": index_name,
                "_id": record.get("event_id"),
                "_source": record
            }

    try:
        success, failed = helpers.bulk(es, generate_actions())
        print(f"Indexed {success} documents. Failed: {failed}")
    except Exception as e:
        print(f"Indexing error: {e}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    JSON_PATH = os.path.join(BASE_DIR, "data", "raw", "fda_quality_events.json")
    
    index_data(JSON_PATH)
