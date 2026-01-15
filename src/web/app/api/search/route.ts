import { NextResponse } from 'next/server';

const ES_HOST = process.env.ES_HOST || 'http://elasticsearch:9200';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { query, filters } = body;

        const esQuery: any = {
            size: 50,
            query: {
                bool: {
                    must: query ? { query_string: { query: query + '*' } } : { match_all: {} },
                    filter: []
                }
            },
            aggs: {
                "System": { terms: { field: "failure_type.keyword", size: 20 } },
                "Site": { terms: { field: "state.keyword", size: 50 } }, // Using state as proxy for site location
                "Risk": { terms: { field: "classification.keyword", size: 5 } },
                "Status": { terms: { field: "status.keyword", size: 5 } }
                // Year would ideally need a date histogram or script, simplified here to just query if needed or we aggregate by date string
            }
        };

        // Apply Filters
        if (filters) {
            if (filters.System && filters.System.length > 0) {
                esQuery.query.bool.filter.push({ terms: { "failure_type.keyword": filters.System } });
            }
            if (filters.Site && filters.Site.length > 0) {
                esQuery.query.bool.filter.push({ terms: { "state.keyword": filters.Site } });
            }
            if (filters.Risk && filters.Risk.length > 0) {
                esQuery.query.bool.filter.push({ terms: { "classification.keyword": filters.Risk } });
            }
        }

        const res = await fetch(`${ES_HOST}/fda_events/_search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(esQuery),
        });

        if (!res.ok) {
            const txt = await res.text();
            throw new Error(`ES Error: ${res.status} ${txt}`);
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error('Search API Error:', error);
        return NextResponse.json({ error: 'Search failed' }, { status: 500 });
    }
}

export async function GET(request: Request) {
    // Fallback for simple GET tests
    const { searchParams } = new URL(request.url);
    const q = searchParams.get('q');
    return POST(new Request(request.url, {
        method: 'POST',
        body: JSON.stringify({ query: q })
    }));
}
