import os
from pyshacl import validate
from rdflib import Graph

def validate_graph(data_graph_path, shapes_graph_path):
    """
    Validates the data graph against the SHACL shapes.
    """
    if not os.path.exists(data_graph_path):
        print(f"Data file not found: {data_graph_path}")
        return False
        
    if not os.path.exists(shapes_graph_path):
        print(f"Shapes file not found: {shapes_graph_path}")
        return False

    print(f"Loading data graph: {data_graph_path}")
    data_graph = Graph()
    data_graph.parse(data_graph_path, format="turtle")

    print(f"Loading shapes graph: {shapes_graph_path}")
    # Shapes are loaded automatically by pyshacl if passed as string path, 
    # but loading into Graph ensures parsing is correct first.
    shapes_graph = Graph()
    shapes_graph.parse(shapes_graph_path, format="turtle")

    print("Running validation...")
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=False,
        debug=False
    )

    if conforms:
        print("Validation SUCCESS: Data conforms to SHACL shapes.")
    else:
        print("Validation FAILED:")
        print(results_text)
    
    return conforms

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "fda_knowledge_graph.ttl")
    SHAPES_PATH = os.path.join(BASE_DIR, "data", "shapes", "fda_shapes.ttl")

    validate_graph(DATA_PATH, SHAPES_PATH)
