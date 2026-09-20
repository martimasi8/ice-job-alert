import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (ICE Job Alert)"
}

SOURCE_PAGES = {
    "Concorsi e Avvisi":
        "https://www.ice.it/it/chi-siamo/lavora-con-noi/concorsi",

    "Tirocini":
        "https://www.ice.it/it/chi-siamo/lavora-con-noi/tirocini",
}

# Parole che identificano una vera opportunità
JOB_KEYWORDS = [
    "avviso di selezione",
    "avviso di assunzione",
    "selezione",
    "assunzione",
    "assistente",
    "analista",
    "analyst",
    "trade analyst",
    "market analyst",
    "business analyst",
    "junior",
    "tirocinio",
    "stage",
    "internship",
    "trainee",
    "borsa",
]

# Elementi da ignorare
IGNORE_KEYWORDS = [
    "albo fornitori",
    "fornitori",
    "servizi export",
    "formazione per l'export",
    "iniziative export",
    "piano export",
    "gara",
    "tender",
    "procurement",
    "graduatoria",
    "commissione",
    "candidati ammessi",
    "elenco candidati",
    "verbale",
    "esito",
    "esiti",
    "nomina",
    "concluso",
    "conclusa",
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
        print(f"Errore: {url}")
        print(e)
        return None


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def analyse_source(name, url):

    print("\n" + "=" * 70)
    print(name)
    print(url)
    print("=" * 70)

    html = get_page(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    results = []
    seen = set()

    for link in soup.find_all("a", href=True):

        title = clean_text(link.get_text(" ", strip=True))
        href = urljoin(url, link["href"])

        if not title:
            continue

        text = title.lower()

        # Ignora contenuti evidentemente non lavorativi
        if any(word in text for word in IGNORE_KEYWORDS):
            continue

        # Cerca opportunità
        if any(word in text for word in JOB_KEYWORDS):

            if href not in seen:

                seen.add(href)

                results.append({
                    "title": title,
                    "url": href
                })

    return results


def main():

    print("=" * 70)
    print("ICE JOB ALERT")
    print(datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("=" * 70)

    all_results = []

    for name, url in SOURCE_PAGES.items():

        results = analyse_source(name, url)

        for item in results:

            if item not in all_results:
                all_results.append(item)

    print("\n" + "=" * 70)
    print(f"TOTALE OPPORTUNITÀ POTENZIALI: {len(all_results)}")
    print("=" * 70)

    for item in all_results:

        print("\n➡️", item["title"])
        print(item["url"])

    print("\n")
    print("Controllo completato.")


if __name__ == "__main__":
    main()
