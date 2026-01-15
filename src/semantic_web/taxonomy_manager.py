
import json
import os
import sys
from collections import Counter
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import SKOS, RDF

# Ensure we can import from parent directory if needed, 
# but assuming this run from root or python path is set.
# We will try to import OpenFDAConnector relative to this file's package structure
try:
    from ingestion.openfda_connector import OpenFDAConnector
except ImportError:
    # Add src to sys.path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from ingestion.openfda_connector import OpenFDAConnector

FDA = Namespace("http://example.org/fda/quality/")

class TaxonomyManager:
    """
    Manages the lifecycle of the FDA Quality Taxonomy.
    Merges real data from OpenFDA with user-defined extensions.
    """

    def __init__(self, extensions_file=None):
        self.extensions_file = extensions_file
        self.hierarchy = {
            "level_1": self._get_base_domains(),
            "level_2": {},
            "level_3": []  # reserved for future granular concepts
        }
        self.category_map = self._build_category_map()

    def _get_base_domains(self):
        """Defines the static Level 1 Domains."""
        return {
            "Manufacturing": {
                "definition": "Failures related to production, facilities, and equipment.",
                "children": ["CGMP Violation", "Batch Record Issue", "Particulate Matter", "Impurity/Contamination", "Sterility Issue"]
            },
            "Quality Control": {
                "definition": "Failures related to testing, specifications, and stability.",
                "children": ["Specification Failure", "Stability Failure", "Subpotent", "Superpotent", "Dissolution Failure"]
            },
            "Packaging & Labeling": {
                "definition": "Failures related to product identification, packaging integrity, and labeling.",
                "children": ["Labeling Error", "Packaging Defect", "Expiration Date Issue", "Carton/Insert Error"]
            },
            "Device Malfunction": {
                "definition": "Failures related to mechanical, software, or electrical device components.",
                "children": ["Software Algorithm Error", "Component Failure", "Battery Failure", "Sensor Issue"]
            }
        }

    def _build_category_map(self):
        """Creates a reverse lookup: Category Name -> Domain Name"""
        mapping = {}
        for domain, props in self.hierarchy["level_1"].items():
            for cat in props["children"]:
                mapping[cat] = domain
        return mapping

    def name_to_uri(self, name):
        """Convert human-readable name to URI-friendly ID"""
        slug = name.lower().replace(" ", "-").replace("/", "-").replace(".", "").replace(",", "").strip()
        slug = "".join([c if c.isalnum() or c == "-" else "" for c in slug])
        return slug

    def fetch_openfda_data(self):
        """Fetches and processes real data from OpenFDA."""
        print("Fetching aggregation data from OpenFDA API...")
        data = OpenFDAConnector.get_all_enforcement_by_reason(limit=500)
        
        if not data or "results" not in data:
            print("Failed to fetch taxonomy data from API.")
            return

        results = data["results"]
        print(f"Analyzing {len(results)} records from OpenFDA...")

        # Initialize Level 2 counts for known categories
        for cat in self.category_map.keys():
            if cat not in self.hierarchy["level_2"]:
                 self.hierarchy["level_2"][cat] = {
                     "count": 0, 
                     "examples": [], 
                     "parent": self.category_map[cat],
                     "source": "OpenFDA"
                 }

        keyword_map = self._get_keyword_map()

        for r in results:
            reason = r.get("reason_for_recall", "")
            reason_lower = reason.lower()
            if not reason:
                continue

            category = "Other Quality Issue"
            for kw, cat in keyword_map.items():
                if kw in reason_lower:
                    category = cat
                    break
            
            if category in self.hierarchy["level_2"]:
                self.hierarchy["level_2"][category]["count"] += 1
                if len(self.hierarchy["level_2"][category]["examples"]) < 3:
                    self.hierarchy["level_2"][category]["examples"].append(reason[:100] + "...")

    def load_extensions(self):
        """Loads user-defined extensions from JSON."""
        if not self.extensions_file or not os.path.exists(self.extensions_file):
            print(f"No extensions file found at {self.extensions_file}")
            return

        print(f"Loading extensions from {self.extensions_file}...")
        try:
            with open(self.extensions_file, 'r') as f:
                ext_data = json.load(f)
            
            for item in ext_data.get("extensions", []):
                term = item["term"]
                domain = item["domain"]
                category = item.get("category") 
                definition = item.get("definition", "")
                examples = item.get("examples", [])

                # Logic:
                # 1. If term maps to an existing Category, add examples/definition to it?
                #    OR treat 'term' as a NEW Category or a specific Failure Type (Level 3)?
                #    The user prompt example showed "AI Hallucination" under "Software Algorithm Error".
                #    This implies AI Hallucination could be a Level 3 concept OR a new Level 2.
                #    Let's treat explicitly defined extensions as Level 3 concepts for now, 
                #    linked to a Level 2 Category.
                
                # Check if domain exists
                if domain not in self.hierarchy["level_1"]:
                    # Create new Domain if user wants!
                    self.hierarchy["level_1"][domain] = {
                        "definition": "User defined domain",
                        "children": []
                    }

                # Ensure Category exists (or create it)
                if category and category not in self.hierarchy["level_2"]:
                     self.hierarchy["level_2"][category] = {
                         "count": 0,
                         "examples": [],
                         "parent": domain,
                         "source": "Extension"
                     }
                     # Add to domain children
                     if category not in self.hierarchy["level_1"][domain]["children"]:
                         self.hierarchy["level_1"][domain]["children"].append(category)

                # Add the Extension Item as a Level 3 Concept
                self.hierarchy["level_3"].append({
                    "term": term,
                    "parent_category": category, # Links to Level 2
                    "definition": definition,
                    "examples": examples
                })
                print(f"Added extension: {term} -> {category}")

        except Exception as e:
            print(f"Error loading extensions: {e}")

    def generate_ttl(self, output_file):
        """Generates the SKOS TTL file."""
        g = Graph()
        g.bind("skos", SKOS)
        g.bind("fda", FDA)
        g.bind("dc", Namespace("http://purl.org/dc/terms/"))
        
        scheme_uri = FDA["scheme/failure_types"]
        g.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
        g.add((scheme_uri, SKOS.prefLabel, Literal("FDA Failure Types", lang="en")))
        g.add((scheme_uri, SKOS.definition, Literal("Hierarchical vocabulary with dynamic extensions.", lang="en")))

        # LEVEL 1: Domains
        for domain, data in self.hierarchy["level_1"].items():
            domain_uri = FDA[f"domain/{self.name_to_uri(domain)}"]
            g.add((domain_uri, RDF.type, SKOS.Concept))
            g.add((domain_uri, SKOS.prefLabel, Literal(domain, lang="en")))
            g.add((domain_uri, SKOS.definition, Literal(data["definition"], lang="en")))
            g.add((domain_uri, SKOS.inScheme, scheme_uri))
            g.add((domain_uri, SKOS.topConceptOf, scheme_uri))
            g.add((scheme_uri, SKOS.hasTopConcept, domain_uri))

        # LEVEL 2: Categories
        for cat_name, data in self.hierarchy["level_2"].items():
            cat_uri = FDA[f"failure_type/{self.name_to_uri(cat_name)}"]
            parent_uri = FDA[f"domain/{self.name_to_uri(data['parent'])}"]
            
            g.add((cat_uri, RDF.type, SKOS.Concept))
            g.add((cat_uri, SKOS.prefLabel, Literal(cat_name, lang="en")))
            g.add((cat_uri, SKOS.inScheme, scheme_uri))
            g.add((cat_uri, SKOS.broader, parent_uri))
            g.add((parent_uri, SKOS.narrower, cat_uri))
            g.add((cat_uri, SKOS.note, Literal(f"Source: {data.get('source', 'System')}", lang="en")))
            
            if data["count"] > 0:
                 g.add((cat_uri, SKOS.note, Literal(f"Frequency: {data['count']} records", lang="en")))

            for ex in data["examples"]:
                g.add((cat_uri, SKOS.example, Literal(ex, lang="en")))

        # LEVEL 3: Extensions (Specific Failure Modes)
        for ext in self.hierarchy["level_3"]:
            term_uri = FDA[f"failure_type/{self.name_to_uri(ext['term'])}"]
            parent_uri = FDA[f"failure_type/{self.name_to_uri(ext['parent_category'])}"]

            g.add((term_uri, RDF.type, SKOS.Concept))
            g.add((term_uri, SKOS.prefLabel, Literal(ext["term"], lang="en")))
            g.add((term_uri, SKOS.inScheme, scheme_uri))
            g.add((term_uri, SKOS.broader, parent_uri))
            g.add((parent_uri, SKOS.narrower, term_uri))
            
            if ext["definition"]:
                g.add((term_uri, SKOS.definition, Literal(ext["definition"], lang="en")))
            
            for ex in ext["examples"]:
                 g.add((term_uri, SKOS.example, Literal(ex, lang="en")))

        # Write to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        g.serialize(destination=output_file, format="turtle")
        print(f"Taxonomy saved to {output_file}")

    def _get_keyword_map(self):
        """Returns the keyword mapping logic."""
        return {
            "impurity": "Impurity/Contamination",
            "contamination": "Impurity/Contamination",
            "sterile": "Sterility Issue",
            "sterility": "Sterility Issue",
            "microbial": "Sterility Issue",
            "cgmp": "CGMP Violation",
            "gmp": "CGMP Violation",
            "batch": "Batch Record Issue",
            "specification": "Specification Failure",
            "failed results": "Specification Failure",
            "label": "Labeling Error",
            "carton": "Carton/Insert Error",
            "package": "Packaging Defect",
            "particulate": "Particulate Matter",
            "glass": "Particulate Matter",
            "stability": "Stability Failure",
            "subpotent": "Subpotent",
            "superpotent": "Superpotent",
            "software": "Software Algorithm Error",
            "device": "Component Failure"
        }
