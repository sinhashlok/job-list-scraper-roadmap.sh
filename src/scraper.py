"""Scrape job listings from the Fake Python Jobs practice site."""

import csv
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://realpython.github.io/fake-jobs/"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "output" / "jobs.csv"
FIELDNAMES = ("job_title", "job_company_name", "job_company_location", "job_detail_url")


def create_session() -> requests.Session:
    """Create a session that retries temporary server and rate-limit errors."""
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=frozenset({"GET"}))
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
    
    return session


def fetch_data() -> str | None:
    """Fetch and return source HTML, or None when the request fails."""
    print("Fetching data from website...")
    try:
        with create_session() as session:
            response = session.get(BASE_URL, timeout=10)
            response.raise_for_status()
    except requests.Timeout:
        print("Error: Fake Python Jobs took too long to respond. Please try again.")
        return None
    except requests.ConnectionError:
        print("Error: Could not connect to Fake Python Jobs. Please try again.")
        return None
    except requests.HTTPError as error:
        print(f"Error: Fake Python Jobs returned HTTP {error.response.status_code}.")
        return None
    except requests.RequestException as error:
        print(f"Unexpected request error: {error}")
        return None
    
    print("Successfully fetched data!\n")
    return response.text


def get_text_or_empty(element) -> str:
    """Return cleaned element text, or an empty string for a missing element."""
    return element.get_text(" ", strip=True) if element else ""


def parse_jobs(html: str) -> list[dict[str, str]]:
    """Extract the required fields from each job card in the supplied HTML."""
    print("Parsing the HTML with Beautiful Soup...")
    
    soup = BeautifulSoup(html, "html.parser")
    job_cards = soup.select("div.column.is-half")
    
    if not job_cards:
        raise ValueError("No job cards were found. The page structure may have changed.")
    jobs: list[dict[str, str]] = []
    
    for card in job_cards:
        apply_link = card.find("a", class_="card-footer-item", string="Apply")
        href = apply_link.get("href", "") if apply_link else ""
        jobs.append({
            "job_title": get_text_or_empty(card.select_one("h2.title.is-5")),
            "job_company_name": get_text_or_empty(card.select_one("h3.subtitle.is-6.company")),
            "job_company_location": get_text_or_empty(card.select_one("p.location")),
            "job_detail_url": urljoin(BASE_URL, href) if href else "",
        })
    
    print(f"Parsing completed: found {len(jobs)} job listings.\n")
    return jobs


def save_data_as_csv(jobs: list[dict[str, str]]) -> None:
    """Save job records to a UTF-8 CSV file."""
    if not jobs:
        raise ValueError("No job listings are available to save.")
    print("Saving data to CSV file...")
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(jobs)
    print(f"Data successfully saved to {OUTPUT_PATH}.")


def jobs_scraper() -> None:
    """Run the complete fetch, parse, and export workflow."""
    html = fetch_data()
    if html is None:
        return
    try:
        jobs = parse_jobs(html)
        save_data_as_csv(jobs)
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
