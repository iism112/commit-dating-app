import httpx
from bs4 import BeautifulSoup
from typing import List, Dict

HN_URL = "https://news.ycombinator.com/"

async def scrape_hn_ai_headlines() -> List[Dict[str, str]]:
    async with httpx.AsyncClient() as client:
        response = await client.get(HN_URL)
        response.raise_for_status()
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    headlines_data = []
    
    # HN structure: <tr class="athing">...<span class="titleline"><a ...>Title</a></span>...</tr>
    items = soup.select('tr.athing')
    
    for item in items:
        title_element = item.select_one('.titleline > a')
        if not title_element:
            continue
            
        title = title_element.get_text()
        url = title_element.get('href')
        
        # Filter for "AI" (case-insensitive)
        if "ai" in title.lower():
            # Handle relative URLs (like "item?id=...")
            if not url.startswith('http'):
                url = HN_URL + url
                
            headlines_data.append({
                "title": title,
                "url": url
            })
            
        if len(headlines_data) >= 5:
            break
            
    return headlines_data
