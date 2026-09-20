import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

BASE_URL = "https://www.ice.it"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (ICE Job Alert)"
}

KEYWORDS = [
    "lavora con noi",
    "work with us",
    "concorso",
    "concorso pubblico",
    "avviso",
    "selezione",
    "tirocinio",
    "stage",
    "internship",
    "junior trade analyst",
    "trade analyst",
    "market analyst",
    "business analyst",
    "commercial",
    "marketing",
    "business development",
    "market intelligence",
]

def get_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Errore nel caricamento di {url}: {e}")
        return None


def extract_links(url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = urljoin(url, a["href"])

        if not text:
            continue

        combined = f"{text} {href}".lower()

        if any(keyword in combined for keyword in KEYWORDS):
            links.append({
                "title": text,
                "url": href
            })

    return links


def main():
    print("=" * 60)
    print("ICE JOB ALERT")
    print(datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("=" * 60)

    url = f"{BASE_URL}/it/lavora-con-noi"

    html = get_page(url)

    if not html:
        print("Impossibile leggere la pagina ICE.")
        return

    links = extract_links(url, html)

    print(f"\nTrovati {len(links)} link potenzialmente rilevanti:\n")

    for item in links:
        print(f"- {item['title']}")
        print(f"  {item['url']}")
        print()

    print("Controllo completato.")


if __name__ == "__main__":
    main()
