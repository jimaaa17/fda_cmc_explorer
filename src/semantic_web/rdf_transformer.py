import json
import os
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

# Namespaces
FDA = Namespace("http://example.org/fda/quality/")
EX = Namespace("http://example.org/resource/")

def transform_to_rdf(input_file, output_file):
    """
    Transforms FDA JSON data into RDF (Turtle) format.
    """
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return

    print(f"Loading data from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    g = Graph()
    g.bind("fda", FDA)
    g.bind("dcterms", DCTERMS)
    g.bind("skos", SKOS)
    g.bind("ex", EX)

    print(f"Transforming {len(data)} records to RDF...")
    
    for record in data:
        event_id = record.get("event_id")
        if not event_id:
            continue
            
        event_uri = EX[f"event/{event_id}"]
        
        # Type definition
        g.add((event_uri, RDF.type, FDA.RecallEvent))
        
        # Basic Literals
        if record.get("recall_number"):
            g.add((event_uri, FDA.recallNumber, Literal(record["recall_number"])))
        
        if record.get("recalling_firm"):
            g.add((event_uri, FDA.recallingFirm, Literal(record["recalling_firm"])))
            
        if record.get("reason_for_recall"):
            g.add((event_uri, FDA.reasonForRecall, Literal(record["reason_for_recall"], lang="en")))
            
        if record.get("report_date"):
             # Format YYYYMMDD to proper XSD Date if needed, for now using string
            g.add((event_uri, DCTERMS.date, Literal(record["report_date"])))

        # Link to Failure Type Concept
        failure_type = record.get("failure_type")
        if failure_type:
            # Create a slug for the concept
            concept_slug = failure_type.lower().replace(" ", "_").replace("/", "_")
            concept_uri = FDA[f"failure_type/{concept_slug}"]
            
            g.add((event_uri, FDA.hasFailureType, concept_uri))
            g.add((concept_uri, RDF.type, SKOS.Concept))
            g.add((concept_uri, SKOS.prefLabel, Literal(failure_type, lang="en")))

    print(f"Serialized {len(g)} triples.")
    g.serialize(destination=output_file, format="turtle")
    print(f"RDF data saved to {output_file}")

if __name__ == "__main__":
    # Default paths for testing
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    INPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "fda_quality_events.json")
    OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "fda_knowledge_graph.ttl")
    
    transform_to_rdf(INPUT_PATH, OUTPUT_PATH)
