import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

CHANGELOG_PATTERNS = [
    "/changelog",
    "/whats-new",
    "/what's-new", 
    "/updates",
    "/releases",
    "/release-notes",
    "/blog",
    "/news",
    "/announcements",
    "/product-updates",
]

CONTENT_SELECTORS = [
    "main",
    "article", 
    '[role="main"]',
    ".content",
    ".posts",
    ".changelog",
    ".updates",
    "#content",
    "#main",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def fetch_page(url: str) -> BeautifulSoup | None:
    """ Fetch a webpage and return a BeautifulSoup object """
    try:
        response = requests.get(
            url, 
            headers=HEADERS, 
            timeout=15,
            allow_redirects=True
        )
        
        response.raise_for_status()

        return BeautifulSoup(response.text, "lxml")
    
    except requests.exceptions.Timeout:
        print(f"[Scraper] Timeout fetching {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"[Scraper] HTTP Error {e.response.status_code} for {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Scraper] Error fetching {url}: {e}")
        return None

def find_update_page_url(base_url: str) -> str | None:
    """
    Given a competitor's homepage, find their changelog/blog URL.
    
    Strategy:
    1. First, try common URL patterns by just appending them to the base URL
    2. If that fails, fetch the homepage and look for links in navigation

    """

    parsed = urlparse(base_url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"
    
    print(f"[Scraper] Looking for update pages on {base_domain}...")

    for pattern in CHANGELOG_PATTERNS:
        candidate_url = base_domain + pattern
        
        try:
            response = requests.head(
                candidate_url, 
                headers=HEADERS, 
                timeout=8,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                print(f"[Scraper] Found update page: {candidate_url}")
                return candidate_url
                
        except requests.exceptions.RequestException:
            continue
    
    print("[Scraper] Common patterns not found, searching homepage links...")
    soup = fetch_page(base_url)
    
    if soup is None:
        return None
    
    all_links = soup.find_all("a", href=True)
    
    update_keywords = [
        "changelog", "what's new", "whats new", "updates", 
        "blog", "news", "releases", "announcements", "product"
    ]
    
    for link in all_links:
        href = str(link.get("href") or "").lower()
        link_text = link.get_text(strip=True).lower()

        for keyword in update_keywords:
            if keyword in href or keyword in link_text:
                full_url = urljoin(base_domain, str(link.get("href") or "").lower())
                print(f"[Scraper] Found via link text: {full_url}")
                return full_url
    
    print("[Scraper] No update page found, will use homepage")
    return base_url


def extract_text_content(soup: BeautifulSoup) -> str:
    """ Extract meaningful text from a page, removing navigation/footer noise """
    
    for element in soup.find_all(["nav", "footer", "header", "script", "style", "aside"]):
        element.decompose()
  
    noise_classes = ["cookie", "banner", "popup", "modal", "sidebar", "advertisement", "ad"]
    for noise_class in noise_classes:
        for element in soup.find_all(class_=lambda c: c and noise_class in c.lower()):  # type: ignore
            element.decompose()
    
    for selector in CONTENT_SELECTORS:
        content_area = soup.select_one(selector)
        if content_area:
            text = content_area.get_text(separator="\n", strip=True)
 
            if len(text) > 200:
                return text
    
    body = soup.find("body")
    if body:
        return body.get_text(separator="\n", strip=True)
    
    return soup.get_text(separator="\n", strip=True)


def extract_structured_entries(soup: BeautifulSoup) -> list[dict]:
    """ Try to extract individual changelog/blog entries as structured data """
    entries = []
    
    entry_patterns = [
        ("article", ["h1", "h2", "h3"]),
        (".post", ["h1", "h2", "h3"]),
        (".changelog-entry", ["h2", "h3"]),
        (".update", ["h2", "h3"]),
        ("section", ["h2", "h3"]),
    ]
    
    for container_selector, title_tags in entry_patterns:
        containers = soup.select(container_selector)
        
        if len(containers) >= 2:  # Found multiple entries - promising!
            for container in containers[:20]:  # Limit to 20 most recent
                entry = {}
                
                for title_tag in title_tags:
                    title_elem = container.find(title_tag)
                    if title_elem:
                        entry["title"] = title_elem.get_text(strip=True)
                        break
                time_elem = container.find("time")
                if time_elem:

                    entry["date"] = time_elem.get("datetime") or time_elem.get_text(strip=True)
                
                entry["content"] = container.get_text(separator=" ", strip=True)[:500]
                
                if entry.get("title") or len(entry.get("content", "")) > 50:
                    entries.append(entry)
            
            if entries: 
                break
    
    return entries



def scrape_competitor(url: str) -> dict | None:
    """
    Main function: scrape a competitor URL and return everything we found.
    
    This orchestrates all the other functions:
    1. Find their update page
    2. Fetch it
    3. Extract content
    4. Return structured result
    """

    update_url = find_update_page_url(url)
    
    if not update_url:
        print(f"[Scraper] Could not find update page for {url}")
        return None
    
    soup = fetch_page(update_url)
    
    if soup is None:
        return None
    
    raw_text = extract_text_content(soup)
    structured_entries = extract_structured_entries(soup)
    

    title = soup.find("title")
    page_title = title.get_text(strip=True) if title else "Unknown"

    result = {
        "source_url": url,             
        "scraped_url": update_url,    
        "page_title": page_title,
        "scraped_at": datetime.now().isoformat(),
        "raw_text": raw_text[:8000], 
        "entries": structured_entries,
        "entry_count": len(structured_entries)
    }
    
    print(f"[Scraper] Successfully scraped {update_url}")
    print(f"[Scraper] Found {len(structured_entries)} structured entries")
    print(f"[Scraper] Extracted {len(raw_text)} characters of text")
    
    return result
