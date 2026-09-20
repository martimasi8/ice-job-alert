import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (ICE Job Alert)"
}

SOURCE_PAGES = {
    "🇮🇹 Italia - Concorsi":
        "https://www.ice.it/it/chi-siamo/lavora-con-noi/concorsi",

    "🇮🇹 Italia - Tirocini":
        "https://www.ice.it/it/chi-siamo/lavora-con-noi/tirocini",

    "🌍 ICE - Mercati esteri":
        "https://www.ice.it/it/mercati",
}

# Parole che identificano possibili opportunità
JOB_KEYWORDS = [
    "analista",
    "analyst",
    "assistente",
    "assistant",
    "trade analyst",
    "market analyst",
    "business analyst",
    "commercial",
    "commerce",
    "marketing",
    "sales",
    "export",
    "international",
    "junior",
    "trainee",
    "internship",
    "intern",
    "stage",
    "tirocinio",
    "research",
    "ricerca",
    "personale",
    "assunzione",
    "selezione",
    "concorso",
    "concorso pubblico",
]

# Pagine/contenuti che NON sono recruiting
IGNORE_KEYWORDS = [
    "albo fornitori",
    "fornitori",
    "market surveys",
    "tender notices",
    "tender",
    "procurement",
    "gara",
    "gare",
    "sponsorizzazioni",
    "graduatoria",
    "graduatorie",
    "commissione",
    "candidati ammessi",
    "elenco candidati",
    "verbale",
    "esito",
    "esiti",
    "risultato della selezione",
    "nomina",
]


def get_page(url):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()
        return response.text

    except Exception as e:
        print(f"⚠️ Errore: {url}")
        print(e)
        return None


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def is_job_link(title, url):

    text = f"{title} {url}".lower()

    # Prima escludiamo ciò che NON ci interessa
    if any(word in text for word in IGNORE_KEYWORDS):
        return False

    # Poi cerchiamo indicatori di recruiting
    return any(word in text for word in JOB_KEYWORDS)


def analyse_page(source_name, url):

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

        if href in seen:
            continue

        if is_job_link(title, href):

            seen.add(href)

            results.append({
                "title": title,
                "url": href,
                "source": source_name
            })

    return results


def find_recruiting_pages():

    print("\n🌍 Ricerca delle pagine recruiting estere...")

    url = SOURCE_PAGES["🌍 ICE - Mercati esteri"]

    html = get_page(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    recruiting_pages = []
    seen = set()

    RECRUITING_WORDS = [
        "bandi di concorso",
        "offerte di lavoro",
        "lavora con noi",
        "work with us",
        "we're hiring",
        "were hiring",
        "job opportunities",
        "job opportunity",
        "recruitment",
        "personale locale",
        "ricerca personale",
        "annunci ricerca personale",
    ]

    for link in soup.find_all("a", href=True):

        title = clean_text(link.get_text(" ", strip=True))
        href = urljoin(url, link["href"])

        if not title:
            continue

        text = title.lower()

        if any(word in text for word in RECRUITING_WORDS):

            if href not in seen:

                seen.add(href)

                recruiting_pages.append({
                    "title": title,
                    "url": href
                })

    print(
        f"🔎 Pagine recruiting estere individuate: "
        f"{len(recruiting_pages)}"
    )

    return recruiting_pages


def main():

    print("=" * 70)
    print("ICE JOB ALERT")
    print(datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("=" * 70)

    all_results = []

    # --------------------------------------------------
    # ITALIA
    # --------------------------------------------------

    print("\n🇮🇹 ITALIA")

    for name, url in SOURCE_PAGES.items():

        if name.startswith("🌍"):
            continue

        print(f"\nControllo: {name}")

        results = analyse_page(name, url)

        print(f"   Trovati: {len(results)}")

        all_results.extend(results)

    # --------------------------------------------------
    # ESTERO
    # --------------------------------------------------

    print("\n🌍 ESTERO")

    recruiting_pages = find_recruiting_pages()

    # Limite di sicurezza
    if len(recruiting_pages) > 100:

        print(
            "⚠️ Trovate più di 100 pagine recruiting. "
            "Per sicurezza interrompo il controllo estero."
        )

        return

    for page in recruiting_pages:

        results = analyse_page(
            page["title"],
            page["url"]
        )

        all_results.extend(results)

    # --------------------------------------------------
    # RIMOZIONE DUPLICATI
    # --------------------------------------------------

    unique = {}

    for item in all_results:

        unique[item["url"]] = item

    print("\n" + "=" * 70)
    print(
        f"🚨 OPPORTUNITÀ POTENZIALI: "
        f"{len(unique)}"
    )
    print("=" * 70)

    for item in unique.values():

        print("\n➡️", item["title"])
        print("📍", item["source"])
        print("🔗", item["url"])

    print("\n✅ Controllo completato.")


if __name__ == "__main__":
    main()
