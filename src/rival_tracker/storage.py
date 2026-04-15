import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")

def get_storage_key(url: str) -> str:
    """ Convet URL to filename """

    url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
    print("The generated hash for the URL is: " + url_hash)

    return url_hash



def save_scrape_result(url: str, content: str) -> None:
    """ Save the scraped content to a json file"""
    DATA_DIR.mkdir(exist_ok=True)

    storage_key = get_storage_key(url)
    file_path = DATA_DIR / f"{storage_key}.json"

    data_to_save = {
        "url": url,
        "content": content,
        "last_checked": datetime.now().isoformat(),
    }

    with open(file_path, "w", encoding = "utf-8") as f:
        json.dump(data_to_save, f,indent = 2, ensure_ascii = False)
    
    print(f"[Storage] Saved results for {url}")

def load_prev_result(url: str) -> dict | None:
    """ Load previously stored scrape result """

    storage_key = get_storage_key(url)
    file_path = DATA_DIR / f"{storage_key}.json"

    if not os.path.exists(file_path):
        return None
 
    with open(file_path, "r", encoding = "utf-8") as f:
        return json.load(f)


def get_all_tracked_urls() -> list[dict]:
    """ Returns info about all URLs currently being tracked """

    DATA_DIR.mkdir(exist_ok=True)
    tracked = []
    for json_file in DATA_DIR.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            tracked.append({
                "url": data.get("url", "Unknown"),
                "last_checked": data.get("last_checked", "Unknown")
            })
    
    return tracked




