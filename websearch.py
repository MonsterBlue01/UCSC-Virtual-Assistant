import requests
from decouple import config

def search_google(query):
    api_key = config('GOOGLE_API_KEY')
    cse_id = config('GOOGLE_CSE_ID')

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    search_results = response.json()

    if 'items' in search_results:
        links = [result['link'] for result in search_results['items']]
        return links
    else:
        return []