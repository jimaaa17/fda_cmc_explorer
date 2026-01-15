import spacy
import os
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS

# Namespaces
FDA = Namespace("http://example.org/fda/quality/")

def enrich_data(input_ttl_path, output_ttl_path):
    """
    Reads the RDF graph, finds product descriptions, runs NER, and adds links.
    """
    if not os.path.exists(input_ttl_path):
        print(f"Input file not found: {input_ttl_path}")
        return

    print("Loading SpaCy model...")
    nlp = spacy.load("en_core_web_sm")

    print(f"Loading knowledge graph: {input_ttl_path}")
    g = Graph()
    g.parse(input_ttl_path, format="turtle")
    g.bind("fda", FDA)

    # Find events with product descriptions (logic: in original JSON described, here we map from JSON properties or check if we kept it in RDF)
    # Wait, the previous transformer only mapped reasonForRecall and few others.
    # Let's assume we might need to re-read the JSON to get the text or if we added it to RDF.
    # Checking rdf_transformer.py... it didn't map product_description explicitly.
    # To save time, we will scan the JSON source again for text, but link to the URI constructed by event_id.
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    JSON_PATH = os.path.join(BASE_DIR, "data", "raw", "fda_quality_events.json")
    
    import json
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)

    print("Enriching graph with extracted entities...")
    count = 0
    for record in data:
        event_id = record.get("event_id")
        text = record.get("product_description", "") + " " + record.get("reason_for_recall", "")
        
        if not event_id or not text.strip():
            continue

        doc = nlp(text)
        event_uri = URIRef(f"http://example.org/resource/event/{event_id}")

        for ent in doc.ents:
            # We focus on ORG (Companies), GPE (Locations)
            if ent.label_ in ["ORG", "GPE"]:
                text_clean = ent.text.strip()
                
                # Heuristic/Guard: Skip obvious false positives from NER
                if ent.label_ == "ORG" and (text_clean.startswith("Failed ") or "Impurities" in text_clean or len(text_clean) > 50):
                    continue
                
                # Safer slug generation: replace non-alphanumeric chars with _
                import re
                entity_slug = re.sub(r'[^a-zA-Z0-9]', '_', text_clean.lower())
                entity_slug = re.sub(r'_+', '_', entity_slug).strip('_')
                
                entity_uri = URIRef(f"http://example.org/resource/entity/{entity_slug}")
                
                # Link event to entity
                g.add((event_uri, FDA.mentionsEntity, entity_uri))
                
                # Define entity
                g.add((entity_uri, RDF.type, FDA.Entity))
                g.add((entity_uri, RDF.type, SKOS.Concept))
                g.add((entity_uri, RDFS.label, Literal(ent.text)))
                g.add((entity_uri, SKOS.prefLabel, Literal(ent.text)))
                g.add((entity_uri, FDA.entityType, Literal(ent.label_)))
                count += 1
    
    print(f"Added {count} entity mentions.")
    g.serialize(destination=output_ttl_path, format="turtle")
    print(f"Enriched graph saved to {output_ttl_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    INPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "fda_knowledge_graph.ttl")
    OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "fda_knowledge_graph_enriched.ttl")
    
    enrich_data(INPUT_PATH, OUTPUT_PATH)
