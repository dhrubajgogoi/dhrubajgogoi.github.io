import json
import os
import requests
from scholarly import scholarly

# --- YOUR ACTUAL IDs ---
SCHOLAR_ID = 'BP85kjoAAAAJ'
SCOPUS_ID = '57226032682' 
INSPIRE_ID = '1780627' 

SCOPUS_API_KEY = os.environ.get('SCOPUS_API_KEY')

def fetch_all_stats():
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
        print("✅ Scholar fetched successfully.")
    except Exception as e:
        print(f"❌ Scholar Error: {e}")

    # 2. Fetch Scopus 
    if not SCOPUS_API_KEY:
        print("❌ Scopus Error: No API Key found in GitHub Secrets!")
    else:
        try:
            url = "https://api.elsevier.com/content/search/scopus"
            headers = {'X-ELS-APIKey': SCOPUS_API_KEY, 'Accept': 'application/json'}
            
            start = 0
            citation_counts = []
            
            while True:
                # FIXED: Changed count to 25. 100 exceeds the free API tier limits!
                params = {'query': f'AU-ID({SCOPUS_ID})', 'count': 25, 'start': start}
                res = requests.get(url, headers=headers, params=params)
                
                if res.status_code != 200:
                    print(f"❌ Scopus API Error: HTTP {res.status_code} - {res.text}")
                    break
                    
                entries = res.json().get('search-results', {}).get('entry', [])
                if not entries:
                    break
                    
                for entry in entries:
                    if 'citedby-count' in entry:
                        citation_counts.append(int(entry['citedby-count']))
                
                # FIXED: Increment by 25
                start += 25
                if len(entries) < 25:
                    break

            if citation_counts:
                stats['scopus']['documents'] = len(citation_counts)
                stats['scopus']['citations'] = sum(citation_counts)
                
                citation_counts.sort(reverse=True)
                h_index = 0
                for i, citations in enumerate(citation_counts):
                    if citations >= i + 1:
                        h_index = i + 1
                    else:
                        break
                stats['scopus']['h_index'] = h_index
                print("✅ Scopus fetched successfully via Search API.")
            else:
                print("❌ Scopus fetched, but 0 papers found.")
                
        except Exception as e:
            print(f"❌ Scopus Error: {e}")

    # 3. Fetch INSPIRE-HEP 
    try:
        author_res = requests.get(f"https://inspirehep.net/api/authors/{INSPIRE_ID}")
        if author_res.status_code == 200:
            author_data = author_res.json()
            
            # FIXED: Grab the exact internal papers link directly from your profile data
            lit_url = author_data.get('links', {}).get('papers')
            if not lit_url:
                lit_url = author_data.get('links', {}).get('literature')
            
            # Fallback to BAI search if the direct link isn't found
            if not lit_url:
                ids = author_data.get('metadata', {}).get('ids', [])
                bai = next((id_obj['value'] for id_obj in ids if id_obj['schema'] == 'INSPIRE BAI'), None)
                if bai:
                    lit_url = f"https://inspirehep.net/api/literature?q=a+{bai}"

            if lit_url:
                # Add size=250 to fetch all papers at once
                separator = "&" if "?" in lit_url else "?"
                lit_url = f"{lit_url}{separator}size=250"
                
                lit_res = requests.get(lit_url)
                if lit_res.status_code == 200:
                    data = lit_res.json()
                    hits = data.get('hits', {}).get('hits', [])
                    total_papers = data.get('hits', {}).get('total', 0)
                    
                    if total_papers > 0:
                        stats['inspire']['papers'] = total_papers
                        stats['inspire']['citations'] = sum(h.get('metadata', {}).get('citation_count', 0) for h in hits)
                        print(f"✅ INSPIRE fetched successfully ({total_papers} papers).")
                    else:
                        print("❌ INSPIRE: Searched via official link, but 0 papers matched.")
                else:
                    print(f"❌ INSPIRE Literature Error: HTTP {lit_res.status_code}")
            else:
                print("❌ INSPIRE: Could not find literature link or BAI in author profile.")
        else:
            print(f"❌ INSPIRE Author Error: HTTP {author_res.status_code}")
            
    except Exception as e:
        print(f"❌ INSPIRE Error: {e}")

    # Save everything to one JSON file
    with open('academic_stats.json', 'w') as f:
        json.dump(stats, f, indent=4)
        print("💾 academic_stats.json saved successfully.")

if __name__ == "__main__":
    fetch_all_stats()
