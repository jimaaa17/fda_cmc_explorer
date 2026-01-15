import json
import os
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import SKOS, RDF

# Namespaces
FDA = Namespace("http://example.org/fda/quality/")

def build_taxonomy(input_file, output_file):
    """
    Scans the JSON input for failure types and reasons to build a SKOS taxonomy.
    """
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return

    print("Scanning data for taxonomy concepts...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    g = Graph()
    g.bind("skos", SKOS)
    g.bind("fda", FDA)
    
    # Root Concept Scheme
    scheme_uri = FDA["scheme/failure_types"]
    g.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
    g.add((scheme_uri, SKOS.prefLabel, Literal("FDA Failure Types", lang="en")))

    failure_types = set()
    
    for record in data:
        ft = record.get("failure_type")
        if ft:
            failure_types.add(ft)
    
    print(f"Found {len(failure_types)} unique failure types.")

    for ft in failure_types:
        slug = ft.lower().replace(" ", "_").replace("/", "_")
        concept_uri = FDA[f"failure_type/{slug}"]
        
        g.add((concept_uri, RDF.type, SKOS.Concept))
        g.add((concept_uri, SKOS.inScheme, scheme_uri))
        g.add((concept_uri, SKOS.prefLabel, Literal(ft, lang="en")))
        g.add((scheme_uri, SKOS.hasTopConcept, concept_uri))

    g.serialize(destination=output_file, format="turtle")
    print(f"Taxonomy saved to {output_file}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    INPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "fda_quality_events.json")
    OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "failure_taxonomy.ttl")
    
    build_taxonomy(INPUT_PATH, OUTPUT_PATH)
