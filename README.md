# Job Listing Scraper

A Python command-line scraper that collects job title, company, location, and
detail-page URL data from the [Fake Python Jobs](https://realpython.github.io/fake-jobs/)
practice website and saves it as CSV.

This is a learning project following the [Job Listings Scraper](https://roadmap.sh/projects/job-listings-scraper) from [roadmap.sh](https://roadmap.sh).

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/) (recommended), or another Python environment manager

## Run

Install the locked dependencies and run the scraper:

```bash
uv run python main.py
```

The generated file is `output/jobs.csv` and has these columns:

```text
job_title,job_company_name,job_company_location,job_detail_url
```

The scraper reports network, HTTP, parsing, and file-writing errors without
creating a misleading success message.
