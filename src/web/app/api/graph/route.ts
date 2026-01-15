import { NextResponse } from 'next/server';

const FUSEKI_HOST = process.env.FUSEKI_HOST || 'http://fuseki:3030';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
        return NextResponse.json({ error: 'Missing ID' }, { status: 400 });
    }

    const eventUri = `http://example.org/resource/event/${id}`;

    const query = `
    PREFIX fda: <http://example.org/fda/quality/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT ?p ?o ?label ?type WHERE {
      <${eventUri}> ?p ?o .
      OPTIONAL { ?o rdfs:label ?label }
      OPTIONAL { ?o skos:prefLabel ?label }
      OPTIONAL { ?o fda:entityType ?type }
    }
  `;

    try {
        const params = new URLSearchParams();
        params.append('query', query);

        const res = await fetch(`${FUSEKI_HOST}/fda/sparql`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/sparql-results+json'
            },
            body: params
        });

        if (!res.ok) {
            // Fallback for GET if POST fails (though Fuseki standards support POST)
            console.error("Fuseki POST failed", res.status);
            throw new Error("Fuseki query failed");
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error('Graph API Error:', error);
        return NextResponse.json({ error: 'Graph query failed' }, { status: 500 });
    }
}
