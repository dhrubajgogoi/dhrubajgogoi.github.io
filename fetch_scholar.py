import json
from scholarly import scholarly

# REPLACE THIS WITH YOUR ACTUAL GOOGLE SCHOLAR ID
SCHOLAR_ID = 'BP85kjoAAAAJ'

def fetch_scholar_stats():
    try:
        # Fetch the author and their metrics
        author = scholarly.search_author_id(SCHOLAR_ID)
        author = scholarly.fill(author, sections=['indices'])
        
        # Extract just the data we want
        stats = {
            'name': author['name'],
            'citations': author['citedby'],
            'h_index': author['hindex'],
            'i10_index': author['i10index']
        }
        
        # Save it to a JSON file
        with open('scholar_stats.json', 'w') as f:
            json.dump(stats, f, indent=4)
            
        print("Successfully updated scholar_stats.json")
        
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_scholar_stats()
