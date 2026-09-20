import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (ICE Job Alert)"
}

PAGES = {
    "🇮🇹 Concorsi e Avvisi": "https://www.ice.it/it/chi-siamo/lavora-con-noi/concorsi",
    "🎓 Tirocini": "https://www.ice.it/it/chi-siamo/lavora-con-noi/tirocini",
}

POSITIVE_KEYWORDS = [
    "analyst",
    "trade analyst",
    "junior trade",
    "market analyst",
    "business analyst",
    "commercial",
    "marketing",
    "business development",
    "market intelligence",
    "international business",
    "export",
    "sales",
    "tirocinio",
    "stage",
    "internship",
    "assistente",
    "borsa di ricerca",
]

IGNORE_KEYWORDS = [
    "albo fornitori",
    "fornitori",
    "gara",
    "tender",
    "procurement",
    "pulizia",
    "cleaning",
    "assicurazione",
    "medical insurance",
    "graduatoria finale",
    "graduatoria definitiva",
    "nomina commissione",
    "commissione esaminatrice",
    "elenco candidati",
    "candidati ammessi",
    "verbale",
    "conflitto di interessi",
]

def get_page(url):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"ERRORE: {url}")
        print(e)
        return None


def analyse_page(name, url):
    print("\n" + "=" * 70)
    print(name)
    print(url)
    print("=" * 70)

    html = get_page(url)

    if not html:
        return

    soup = BeautifulSoup(html, "html.parser")

    results = []

    for link in soup.find_all("a", href=True):

        title = link.get_text(" ", strip=True)
        href = urljoin(url, link["href"])

        if not title:
            continue

        text = title.lower()

        if any(word in text for word in IGNORE_KEYWORDS):
            continue

        if any(word in text for word in POSITIVE_KEYWORDS):

            results.append({
                "title": title,
                "url": href
            })

    # elimina duplicati
    unique = []
    seen = set()

    for item in results:
        key = item["url"]

        if key not in seen:
            seen.add(key)
            unique.append(item)

    if not unique:
        print("Nessuna opportunità rilevante trovata.")

    else:
        print(f"\nTrovate {len(unique)} opportunità potenzialmente rilevanti:\n")

        for item in unique:
            print("➡️", item["title"])
            print("   ", item["url"])
            print()


def main():

    print("=" * 70)
    print("ICE JOB ALERT")
    print(datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("=" * 70)

    for name, url in PAGES.items():
        analyse_page(name, url)

    print("\nControllo completato.")


if __name__ == "__main__":
    main()
