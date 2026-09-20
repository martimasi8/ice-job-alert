import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (ICE Job Alert)"
}

BASE_URL = "https://www.ice.it"

ITALY_PAGES = {
    "Concorsi e Avvisi":
        "https://www.ice.it/it/chi-siamo/lavora-con-noi/concorsi",

    "Tirocini":
        "https://www.ice.it/it/chi-siamo/lavora-con-noi/tirocini",
}

JOB_WORDS = [
    "avviso di selezione",
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

IGNORE_WORDS = [
    "albo fornitori",
    "fornitori",
    "gara",
    "tender",
    "procurement",
    "graduatoria",
    "commissione",
    "candidati ammessi",
    "verbale",
    "esito",
    "nomina",
    "servizi export",
    "formazione per l'export",
    "iniziative export",
]


def get_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"Errore {url}: {e}")
        return None


def clean(text):
    return " ".join(text.split())


def find_work_pages():

    print("\n🔎 Ricerca delle sedi ICE estere...")

    url = f"{BASE_URL}/it/mercati"

    html = get_page(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    pages = []

    for a in soup.find_all("a", href=True):

        text = clean(a.get_text(" ", strip=True))
        href = urljoin(url, a["href"])

        if not text:
            continue

        # Cerchiamo pagine che sembrano appartenere
        # agli uffici ICE esteri
        if "/mercati/" in href:

            if href not in [p["url"] for p in pages]:

                pages.append({
                    "name": text,
                    "url": href
                })

    print(f"🌍 Trovate {len(pages)} pagine di mercato.")

    return pages


def find_job_pages(market_pages):

    job_pages = []

    for market in market_pages:

        html = get_page(market["url"])

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):

            title = clean(a.get_text(" ", strip=True))
            href = urljoin(market["url"], a["href"])

            if "lavora con noi" in title.lower():

                job_pages.append({
                    "office": market["name"],
                    "title": title,
                    "url": href
                })

    return job_pages


def analyse_page(name, url):

    html = get_page(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    results = []

    for a in soup.find_all("a", href=True):

        title = clean(a.get_text(" ", strip=True))
        href = urljoin(url, a["href"])

        if not title:
            continue

        text = title.lower()

        if any(word in text for word in IGNORE_WORDS):
            continue

        if any(word in text for word in JOB_WORDS):

            results.append({
                "title": title,
                "url": href,
                "source": name
            })

    return results


def main():

    print("=" * 70)
    print("ICE JOB ALERT")
    print(datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("=" * 70)

    all_results = []

    # 🇮🇹 ITALIA

    print("\n🇮🇹 ITALIA")

    for name, url in ITALY_PAGES.items():

        results = analyse_page(name, url)

        all_results.extend(results)

    # 🌍 ESTERO

    print("\n🌍 ESTERO")

    market_pages = find_work_pages()

    work_pages = find_job_pages(market_pages)

    print(f"🔎 Trovate {len(work_pages)} pagine 'Lavora con noi'.")

    for page in work_pages:

        results = analyse_page(
            page["office"],
            page["url"]
        )

        all_results.extend(results)

    # Rimuove duplicati

    unique = {}

    for item in all_results:

        unique[item["url"]] = item

    print("\n" + "=" * 70)
    print(f"🚨 OPPORTUNITÀ POTENZIALI: {len(unique)}")
    print("=" * 70)

    for item in unique.values():

        print("\n➡️", item["title"])
        print("🌍", item["source"])
        print(item["url"])

    print("\n✅ Controllo completato.")


if __name__ == "__main__":
    main()
