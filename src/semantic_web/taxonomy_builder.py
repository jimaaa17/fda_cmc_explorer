

import os
import sys

# Add src to python path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from semantic_web.taxonomy_manager import TaxonomyManager

def build_taxonomy(output_file, extensions_file):
    """
    Orchestrates the taxonomy build process using TaxonomyManager.
    """
    print("Initializing Taxonomy Manager...")
    manager = TaxonomyManager(extensions_file)
    
    # 1. Fetch Real Data (Base Layer)
    manager.fetch_openfda_data()
    
    # 2. Load Extensions (User Layer)
    manager.load_extensions()
    
    # 3. Generate Output
    manager.generate_ttl(output_file)

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed", "failure_taxonomy.ttl")
    EXTENSIONS_PATH = os.path.join(BASE_DIR, "data", "config", "taxonomy_extensions.json")
    
    build_taxonomy(OUTPUT_PATH, EXTENSIONS_PATH)

