import os
# Since pylode can be complex to install and run inside all environments, 
# this script is a lightweight documentation generator that mimics the output 
# or wraps pylode if available. 

# For this environment, we will generate a simple markdown report of the ontology.

from rdflib import Graph, RDF, RDFS, OWL, DCTERMS

def generate_docs(ontology_path, output_path):
    """
    Generates a Markdown documentation file from the ontology TTL.
    """
    if not os.path.exists(ontology_path):
        print(f"Ontology file not found: {ontology_path}")
        return

    g = Graph()
    g.parse(ontology_path, format="turtle")
    
    with open(output_path, 'w') as f:
        # Title & Meta
        for s, p, o in g.triples((None, RDF.type, OWL.Ontology)):
            title = g.value(s, DCTERMS.title) or "Ontology Documentation"
            desc = g.value(s, DCTERMS.description) or ""
            f.write(f"# {title}\n\n")
            if desc:
                f.write(f"{desc}\n\n")
        
        # Classes
        f.write("## Classes\n")
        for s, p, o in g.triples((None, RDF.type, RDFS.Class)):
            label = g.value(s, RDFS.label) or s
            comment = g.value(s, RDFS.comment) or ""
            f.write(f"### {label}\n")
            f.write(f"- **URI**: `{s}`\n")
            if comment:
                f.write(f"- **Description**: {comment}\n")
            f.write("\n")
            
        # Properties
        f.write("## Properties\n")
        for s, p, o in g.triples((None, RDF.type, RDF.Property)):
            label = g.value(s, RDFS.label) or s
            comment = g.value(s, RDFS.comment) or ""
            f.write(f"### {label}\n")
            f.write(f"- **URI**: `{s}`\n")
            if comment:
                f.write(f"- **Description**: {comment}\n")
            f.write("\n")
            
    print(f"Documentation generated at {output_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ONTOLOGY_PATH = os.path.join(BASE_DIR, "data", "processed", "ontology.ttl")
    OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "ontology_docs.md")
    
    generate_docs(ONTOLOGY_PATH, OUTPUT_PATH)
