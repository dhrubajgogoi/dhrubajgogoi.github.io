import json
import os
import requests
from scholarly import scholarly

# --- YOUR ACTUAL IDs ---
SCHOLAR_ID = 'BP85kjoAAAAJ'
SCOPUS_ID = '57226032682' 
INSPIRE_ID = '1780627' 

# Grabs the API key securely from GitHub Actions
SCOPUS_API_KEY = os.environ.get('SCOPUS_API_KEY')

def fetch_all_stats():
    # Set up our baseline empty data
    stats = {
        'scholar': {'citations': 0, 'h_index': 0, 'i10_index': 0},
        'scopus': {'citations': 0, 'h_index': 0, 'documents': 0},
        'inspire': {'citations': 0, 'papers': 0}
    }

    # 1. Fetch Google Scholar
    try:
        author = scholarly.search_author_id(SCHOLAR_ID)
        author = scholarly.fill(author, sections=['indices'])
        stats['scholar']['citations'] = author.get('citedby', 0)
        stats['scholar']['h_index'] = author.get('hindex', 0)
        stats['scholar']['i10_index'] = author.get('i10index', 0)
        print("Scholar fetched successfully.")
    except Exception as e:
        print(f"Scholar Error: {e}")

    # 2. Fetch Scopus
    if SCOPUS_ID and SCOPUS_API_KEY:
        try:
            url = f"https://api.elsevier.com/content/author?author_id={SCOPUS_ID}"
            headers = {'X-ELS-APIKey': SCOPUS_API_KEY, 'Accept': 'application/json'}
            res = requests.get(url, headers=headers).json()
            data = res.get('author-retrieval-response', [{}])[0]
            core = data.get('coredata', {})
            stats['scopus']['citations'] = int(core.get('citation-count', 0))
            stats['scopus']['documents'] = int(core.get('document-count', 0))
            stats['scopus']['h_index'] = int(data.get('h-index', 0))
            print("Scopus fetched successfully.")
        except Exception as e:
            print(f"Scopus Error: {e}")

    # 3. Fetch INSPIRE-HEP
    if INSPIRE_ID:
        try:
            # Fetches up to 250 papers to sum citations
            url = f"https://inspirehep.net/api/literature?q=a+{INSPIRE_ID}&size=250"
            res = requests.get(url).json()
            hits = res.get('hits', {}).get('hits', [])
            stats['inspire']['papers'] = res.get('hits', {}).get('total', 0)
            stats['inspire']['citations'] = sum(h.get('metadata', {}).get('citation_count', 0) for h in hits)
            print("INSPIRE fetched successfully.")
        except Exception as e:
            print(f"INSPIRE Error: {e}")

    # Save everything to one JSON file
    with open('academic_stats.json', 'w') as f:
        json.dump(stats, f, indent=4)

if __name__ == "__main__":
    fetch_all_stats()
