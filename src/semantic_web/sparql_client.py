from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST
import os

class SPARQLClient:
    """
    Client for interacting with a SPARQL endpoint using SPARQLWrapper.
    """
    def __init__(self, update_endpoint, query_endpoint):
        self.update_endpoint = update_endpoint
        self.query_endpoint = query_endpoint
        self._update = SPARQLWrapper(update_endpoint)
        self._query = SPARQLWrapper(query_endpoint)

    def upload_ttl(self, file_path, graph_uri='default'):
        """
        Uploads a TTL file to the SPARQL store using SPARQL UPDATE (LOAD command).
        Note: This assumes the file is accessible to the server or we read and INSERT.
        For simplicity, we will read the file and do an INSERT DATA.
        """
        print(f"Reading {file_path} for upload...")
        with open(file_path, 'r') as f:
            ttl_data = f.read()

        # Simple INSERT DATA (Warning: Not efficient for huge files)
        # For huge files, use Graph Store Protocol (PUT/POST) implementation instead
        print(f"Uploading data to {self.update_endpoint} (Stubbed for safety)...")
        # self._update.setMethod(POST)
        # self._update.setQuery(f"INSERT DATA {{ {ttl_data} }}")
        # self._update.query()
        pass

    def query(self, sparql_query):
        """
        Executes a SPARQL query and returns JSON results.
        """
        print(f"Executing Query: {sparql_query}")
        self._query.setQuery(sparql_query)
        self._query.setReturnFormat(JSON)
        try:
            results = self._query.query().convert()
            return results
        except Exception as e:
            print(f"Query failed: {e}")
            return {"results": {"bindings": []}} # Return empty result on failure


if __name__ == "__main__":
    # Example usage stub
    client = SPARQLClient("http://localhost:3030/ds/update", "http://localhost:3030/ds/query")
    print("SPARQL Client Initialized")
