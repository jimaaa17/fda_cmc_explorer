import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from elasticsearch import Elasticsearch
from SPARQLWrapper import SPARQLWrapper, JSON
import time

# -- Configurations --
ES_HOST = "http://localhost:9200"
FUSEKI_HOST = "http://localhost:3030/fda/sparql"
SKOSMOS_HOST = "http://localhost" # Maps to locahost:80 where skosmos runs

st.set_page_config(layout="wide", page_title="FDA Quality Graph")

# -- Clients --
@st.cache_resource
def get_es():
    return Elasticsearch(ES_HOST) # If this fails, check Docker

@st.cache_resource
def get_sparql():
    return SPARQLWrapper(FUSEKI_HOST)

# -- UI --
st.title("FDA Quality Event Knowledge Graph")
st.markdown("Unified view of Enforcement Reports, Semantic Graph, and Taxonomy.")

# Sidebar Search
st.sidebar.header("Search")
query = st.sidebar.text_input("Find events (e.g., 'impurity')", "impurity")
es = get_es()

if query:
    try:
        res = es.search(index="fda_events", body={"query": {"query_string": {"query": query}}}, size=10)
        hits = res['hits']['hits']
        st.sidebar.success(f"Found {len(hits)} matching reports.")
    except Exception as e:
        st.sidebar.error("Elasticsearch not connected.")
        hits = []
else:
    hits = []

# Selection
selected_id = None
if hits:
    options = {h['_id']: f"{h['_id']} - {h['_source'].get('recalling_firm', 'Unknown')}" for h in hits}
    selected_id = st.sidebar.radio("Select Report", list(options.keys()), format_func=lambda x: options[x])

# -- Main View --
col1, col2 = st.columns([1, 2])

if selected_id:
    # 1. Detail View (Source)
    # Find the full record
    record = next((h['_source'] for h in hits if h['_id'] == selected_id), None)
    
    with col1:
        st.subheader("Event Details")
        if record:
            st.json(record)
            
            # Link to Taxonomy if failure type exists
            ft = record.get("failure_type")
            if ft:
                # Construct likely URI concept slug
                slug = ft.lower().replace(" ", "_").replace("/", "_")
                # Direct link to Skosmos concept page
                skos_link = f"{SKOSMOS_HOST}/fda/en/page/failure_type/{slug}"
                st.markdown(f"**Failure Type**: [{ft}]({skos_link}) (Open in Thesaurus)")

    # 2. Graph View (Semantic)
    with col2:
        st.subheader("Semantic Graph")
        
        # SPARQL Query to get neighborhood of this event
        sparql = get_sparql()
        event_uri = f"http://example.org/resource/event/{selected_id}"
        
        # Query: Find direct properties + linked entities
        q = f"""
        PREFIX fda: <http://example.org/fda/quality/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT ?p ?o ?label ?type WHERE {{
          <{event_uri}> ?p ?o .
          OPTIONAL {{ ?o rdfs:label ?label }}
          OPTIONAL {{ ?o skos:prefLabel ?label }}
          OPTIONAL {{ ?o fda:entityType ?type }}
        }}
        """
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
        
        try:
            results = sparql.query().convert()
            
            # Build Agraph
            nodes = []
            edges = []
            
            # Add central node
            nodes.append(Node(id=event_uri, label=selected_id, size=25, color="#FF5733"))
            
            added_nodes = {event_uri}
            
            for r in results["results"]["bindings"]:
                p = r["p"]["value"].split("/")[-1].split("#")[-1] # Shorten property
                o_val = r["o"]["value"]
                o_label = r.get("label", {}).get("value", o_val.split("/")[-1])
                o_type = r.get("type", {}).get("value", "Literal")
                
                # Determine node color based on type relation
                color = "#999"
                if "hasFailureType" in p:
                    color = "#33FF57" # Green for Concept
                elif "mentionsEntity" in p:
                    color = "#3357FF" # Blue for Entity
                    
                if o_val not in added_nodes:
                    nodes.append(Node(id=o_val, label=o_label, size=15, color=color))
                    added_nodes.add(o_val)
                    
                edges.append(Edge(source=event_uri, target=o_val, label=p))
            
            config = Config(width=700, height=500, directed=True, nodeHighlightBehavior=True, highlightColor="#F7A7A6")
            
            return_value = agraph(nodes=nodes, edges=edges, config=config)
            
        except Exception as e:
            st.error(f"Error querying graph: {e}")

else:
    st.info("Select an event from the sidebar to visualize.")
