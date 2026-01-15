import os
from rdflib import Graph, URIRef, Literal
from rdflib.plugin import register, Store
from rdflib_sqlalchemy import registerplugins

# Register SQLAlchemy Store plugin
registerplugins()

def persist_graph(ttl_file_path, db_url="sqlite:///fda_graph.db"):
    """
    Reads a TTL file and persists it to a SQL database.
    """
    if not os.path.exists(ttl_file_path):
        print(f"TTL file not found: {ttl_file_path}")
        return

    # Use a specific identifier for the graph
    identifier = URIRef("http://example.org/fda/quality/graph")
    
    # Open SQL store
    store = Graph(store="SQLAlchemy", identifier=identifier)
    store.open(db_url, create=True)
    
    print(f"Loading data from {ttl_file_path} into {db_url}...")
    # Load data into the store
    # Note: parse() on a store-backed graph adds the triples to the store
    store.parse(ttl_file_path, format="turtle")
    
    print(f"Persisted {len(store)} triples to database.")
    
    # Verify by counting
    print("Verification Query (Count):")
    # Simple count check
    count = 0
    for _ in store.triples((None, None, None)):
        count += 1
    print(f"Total Triples in DB: {count}")
    
    store.close()

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "fda_knowledge_graph.ttl")
    DB_PATH = os.path.join(BASE_DIR, "data", "processed", "fda_graph.db")
    DB_URL = f"sqlite:///{DB_PATH}"

    persist_graph(DATA_PATH, DB_URL)
