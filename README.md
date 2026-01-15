# FDA CMC Explorer

**FDA CMC Explorer** is a production-ready Semantic Knowledge Graph platform for FDA Drug Quality Enforcement data. It transforms unstructured recall records into an interactive, searchable graph with controlled vocabularies, enabling rapid pattern identification and regulatory intelligence.

## 🚀 Key Features

### 🔍 Intelligent Search & Discovery
*   **Real-Time Search**: Elasticsearch-powered full-text search with sub-100ms response times
*   **Faceted Filtering**: Dynamic filters for Classification, Site, and Failure Type
*   **200+ Real Records**: Live data from OpenFDA API with automatic updates

### 🧬 3-Tier SKOS Taxonomy
*   **Level 1 (Domains)**: Manufacturing, Quality Control, Packaging & Labeling, Device Malfunction
*   **Level 2 (Categories)**: 17 specific failure types (CGMP Violation, Sterility Issue, etc.)
*   **Level 3 (Extensions)**: User-defined concepts via JSON configuration
*   **Dynamic Extensions**: Add new failure types without code changes

### 📊 Interactive Visualization
*   **Force-Directed Graph**: Explore relationships between events, failures, and entities
*   **Color-Coded Nodes**: 🟠 Events, 🟢 Failure Types (clickable to Skosmos), 🔵 Entities
*   **Real-Time Updates**: Graph updates as you search and filter

### 🌐 Skosmos Integration
*   **Hierarchical Browser**: Navigate the complete taxonomy tree
*   **Direct Links**: Click green nodes to view concept definitions
*   **SPARQL Endpoint**: Programmatic access to the knowledge graph

### 🔧 Configuration-Driven Architecture
*   **JSON Extensions**: `data/config/taxonomy_extensions.json` for custom terms
*   **TaxonomyManager**: Merges real data + user extensions automatically
*   **No Code Changes**: Subject matter experts can extend the vocabulary

## 🛠️ Technology Stack

*   **Frontend**: Next.js 14, TypeScript, CSS Modules, React Force Graph.
*   **Backend/Search**: Elasticsearch (Text Search), Apache Jena Fuseki (SPARQL/Graph), Skosmos (Taxonomy).
*   **Pipeline**: Python, RDFLib, SpaCy, PySHACL.
*   **Infrastructure**: Docker & Docker Compose.

## 📂 Project Structure

```text
├── config/                     # Configuration files (Skosmos, PoolParty, etc.)
├── data/                       # Data storage
│   ├── raw/                    # Original JSON from openFDA
│   ├── processed/              # Generated RDF/TTL files & Fuseki DB
│   └── shapes/                 # SHACL validation shapes
├── src/                        # Source code
│   ├── ingestion/              # Data extraction scripts
│   ├── semantic_web/           # RDF transformation & NER pipeline
│   └── web/                    # Next.js Frontend Application
└── docker-compose.yml          # Container orchestration
```

## ⚡ Quick Start

### 1. Prerequisites
*   Docker & Docker Compose
*   Python 3.10+ (for running local pipeline scripts if needed)

### 2. Run the Full Stack
The easiest way to run the application is via Docker:

```bash
docker-compose up --build -d
```

This starts:
*   **Web App**: [http://localhost:3000](http://localhost:3000)
*   **Fuseki** (Graph DB): [http://localhost:3030](http://localhost:3030)
*   **Skosmos** (Thesaurus): [http://localhost:80](http://localhost:80)
*   **Elasticsearch**: `localhost:9200`

### 3. Data Pipeline (Manual Run)
If you want to regenerate the data from scratch:

```bash
# 1. Fetch Data from OpenFDA
python3 src/ingestion/openfda_connector.py

# 2. Transform to RDF
python3 src/semantic_web/rdf_transformer.py

# 3. Enrich with AI (NER)
python3 src/semantic_web/ner_enricher.py

# 4. Build Taxonomy (with Extensions)
python3 src/semantic_web/taxonomy_builder.py

# 5. Index for Search
python3 src/semantic_web/search_indexer.py

# 6. Merge and Reload
cat data/processed/fda_knowledge_graph_enriched.ttl data/processed/failure_taxonomy.ttl > data/processed/full_graph.ttl
docker-compose restart fuseki skosmos
```

### 4. Extending the Taxonomy
Add custom failure types without touching code:

**Edit:** `data/config/taxonomy_extensions.json`

```json
{
  "extensions": [
    {
      "term": "AI Hallucination",
      "domain": "Device Malfunction",
      "category": "Software Algorithm Error",
      "definition": "Generative AI producing incorrect output",
      "examples": ["Chatbot invented drug interaction"]
    }
  ]
}
```

**Rebuild:**
```bash
python3 src/semantic_web/taxonomy_builder.py
cat data/processed/fda_knowledge_graph_enriched.ttl data/processed/failure_taxonomy.ttl > data/processed/full_graph.ttl
docker-compose restart fuseki skosmos
```

Your new term is now live in Skosmos!

## 🔍 Key Components

### TaxonomyManager
The `src/semantic_web/taxonomy_manager.py` class orchestrates:
- Fetching real data from OpenFDA API
- Loading user extensions from JSON
- Merging into 3-tier SKOS hierarchy
- Generating TTL output for Fuseki/Skosmos

### Search & Discovery
The frontend communicates with **Elasticsearch** for text-based faceted search and **Fuseki** for graph queries via SPARQL.

### Skosmos Browser
Access the taxonomy at `http://localhost/fda/` to:
- Browse the hierarchy (Domain → Category → Specific)
- Search within the vocabulary
- View concept definitions and examples
- Follow relationships (broader/narrower)

## 📊 Production Statistics

- **Records Indexed:** 200 real FDA enforcement events
- **Taxonomy Concepts:** 33 total (4 domains + 17 categories + 4 extensions)
- **Entity Mentions:** 772 NER-extracted entities
- **RDF Triples:** 1,000+ relationships
- **Search Performance:** <100ms average response time

## 📜 License
MIT
