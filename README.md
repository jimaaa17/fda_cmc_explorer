# FDA CMC Explorer

**FDA CMC Explorer** is a comprehensive Semantic Search and Discovery platform for FDA Drug Quality Enforcement Reports. It combines a robust data ingestion pipeline with a Knowledge Graph (Fuseki/SKOS) and a modern Next.js frontend to enable "CMC-style" discovery of quality defects, failure types, and risk classifications.

## 🚀 Features

*   **5-Stage Data Pipeline**: Ingestion -> semantic enrichment (NER) -> Validation (SHACL) -> Persistence -> Documentation.
*   **Knowledge Graph**: Powered by Apache Jena Fuseki, using SKOS for taxonomy management.
*   **AI Enrichment**: Uses SpaCy for Named Entity Recognition (NER) to link reports to entities (Manufacturers, Sites).
*   **Next.js Frontend**: A "Product-Grade" dashboard with:
    *   **Faceted Search**: Filter by System (Impurity, Stability), Site, and Risk.
    *   **Graph Visualization**: Interactive force-directed graph of report relationships.
    *   **Dark Mode UI**: Premium aesthetic with glassmorphism effects.
*   **Skosmos Integration**: Integrated thesaurus browser for FDA failure types.

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
# 1. Fetch Data
python3 src/ingestion/openfda_connector.py

# 2. Transform to RDF
python3 src/semantic_web/rdf_transformer.py

# 3. Enrich with AI (NER)
python3 src/semantic_web/ner_enricher.py

# 4. Validate Data
python3 src/semantic_web/validator.py
```

## 🔍 Key Components

### Search & Discovery
The frontend communicates with **Elasticsearch** for text-based faceted search and **Fuseki** for graph queries.

### Semantic Validation
We use **SHACL** (`data/shapes/fda_shapes.ttl`) to ensure every `RecallEvent` has a valid `recurrence` date, `classification`, and linked `failure_type`.

## 📜 License
MIT
