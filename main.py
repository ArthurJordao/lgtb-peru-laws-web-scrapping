import requests
import time
import json
import re
from datetime import datetime
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd


class PeruLGBTLawScraper:
    def __init__(self):
        self.base_urls = [
            "https://www.congreso.gob.pe",
            "https://www.congreso.gob.pe/pley-2016-2021/",
            "https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search"
        ]

        self.search_terms = [
            "LGTBI",
            "LGBTI", 
            "LGBTIQ",
            "igualdad",
            "discriminación",
            "orientación sexual",
            "identidad de género",
            "matrimonio igualitario",
            "unión civil",
            "trans",
            "travesti",
            "intersexual"
        ]

        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_session()
        self.results = []

    def setup_session(self):
        headers = {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }
        self.session.headers.update(headers)

    def safe_request(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    print(
                        f"Access forbidden to {url}, trying with different user agent..."
                    )
                    self.session.headers["User-Agent"] = self.ua.random
                else:
                    print(f"HTTP {response.status_code} for {url}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
        return None

    def search_congress_main(self):
        print("Searching main Congress website...")

        # Try different search endpoints
        search_endpoints = ["/search", "/buscar", "/consultas", "/proyectos-ley"]

        for endpoint in search_endpoints:
            url = urljoin(self.base_urls[0], endpoint)
            response = self.safe_request(url)
            if response:
                self.parse_search_results(response, url)
                break

        # Try searching for specific pages that might contain LGBT-related content
        specific_pages = ["/comisiones", "/proyectos-ley", "/leyes", "/dictamenes"]

        for page in specific_pages:
            if len(self.results) >= 10:  # Stop if we have enough results
                break
            url = urljoin(self.base_urls[0], page)
            response = self.safe_request(url)
            if response:
                self.search_page_content(response, url)

    def search_pley_portal(self):
        print("Searching PLEY portal...")
        if len(self.results) >= 10:  # Stop if we have enough results
            return
            
        response = self.safe_request(self.base_urls[1])
        if response:
            soup = BeautifulSoup(response.content, "html.parser")

            # Look for search forms or project listings
            search_forms = soup.find_all("form")
            for form in search_forms[:2]:  # Limit forms to check
                if len(self.results) >= 10:
                    break
                if any(
                    term in str(form).lower()
                    for term in ["search", "buscar", "consulta"]
                ):
                    self.handle_search_form(form, self.base_urls[1])

            # Look for direct project links
            project_links = soup.find_all("a", href=True)
            for link in project_links[:5]:  # Limit links to check
                if len(self.results) >= 10:
                    break
                if any(
                    term in link.get("href", "").lower()
                    for term in ["proyecto", "ley", "dictamen"]
                ):
                    full_url = urljoin(self.base_urls[1], link["href"])
                    self.check_project_page(full_url)

    def handle_search_form(self, form, base_url):
        action = form.get("action", "")
        method = form.get("method", "get").lower()

        # Try searching for each LGBT-related term (already limited to 3 terms)
        for term in self.search_terms:
            if len(self.results) >= 10:  # Stop if we have enough results
                break
            try:
                search_url = urljoin(base_url, action) if action else base_url

                if method == "post":
                    # Handle POST search
                    data = {"q": term, "search": term, "query": term}
                    response = self.session.post(search_url, data=data, timeout=10)
                else:
                    # Handle GET search
                    params = {"q": term, "search": term, "query": term}
                    response = self.session.get(search_url, params=params, timeout=10)

                if response and response.status_code == 200:
                    self.parse_search_results(response, search_url)
                    time.sleep(1)  # Be respectful

            except Exception as e:
                print(f"Search failed for term '{term}': {e}")

    def search_page_content(self, response, url):
        soup = BeautifulSoup(response.content, "html.parser")
        text_content = soup.get_text().lower()

        found_terms = []
        for term in self.search_terms:
            if term.lower() in text_content:
                found_terms.append(term)

        if found_terms:
            title = soup.find("title")
            title_text = title.get_text() if title else "Sin título"

            result = {
                "url": url,
                "title": title_text,
                "found_terms": found_terms,
                "content_snippet": self.extract_relevant_snippet(soup, found_terms),
                "scraped_at": datetime.now().isoformat(),
            }
            self.results.append(result)
            print(f"Found LGBT-related content at: {url}")

    def check_project_page(self, url):
        response = self.safe_request(url)
        if response:
            self.search_page_content(response, url)

    def parse_search_results(self, response, search_url):
        soup = BeautifulSoup(response.content, "html.parser")

        # Look for result links
        result_selectors = [
            'a[href*="proyecto"]',
            'a[href*="ley"]',
            'a[href*="dictamen"]',
            ".search-result a",
            ".resultado a",
        ]

        for selector in result_selectors:
            links = soup.select(selector)
            for link in links[:3]:  # Limit to 3 results per selector for testing
                if len(self.results) >= 10:  # Stop if we have enough results
                    return
                href = link.get("href")
                if href:
                    full_url = urljoin(search_url, href)
                    self.check_project_page(full_url)

    def extract_relevant_snippet(self, soup, found_terms, max_length=500):
        text = soup.get_text()

        for term in found_terms:
            pattern = re.compile(
                f".{{0,100}}{re.escape(term.lower())}.{{0,100}}", re.IGNORECASE
            )
            match = pattern.search(text)
            if match:
                snippet = match.group(0).strip()
                return snippet[:max_length] if len(snippet) > max_length else snippet

        return text[:max_length] if text else ""

    def save_results(self):
        if not self.results:
            print("No LGBT-related laws or documents found.")
            return

        # Save as JSON
        with open("lgbt_laws_peru.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Save as CSV
        df = pd.DataFrame(self.results)
        df.to_csv("lgbt_laws_peru.csv", index=False, encoding="utf-8")

        print(f"Found {len(self.results)} LGBT-related documents/pages")
        print("Results saved to 'lgbt_laws_peru.json' and 'lgbt_laws_peru.csv'")

    def run(self):
        print("Starting LGBT rights law scraper for Peru Congress...")
        print(f"Searching for terms: {', '.join(self.search_terms[:3])}")  # Limit terms for testing
        print("(Testing mode: limited to first 3 search terms and 10 total results)")

        try:
            # Only search first few terms and limit results
            self.search_terms = self.search_terms[:3]  
            self.search_congress_main()
            
            # Stop early if we have enough results
            if len(self.results) >= 10:
                print(f"Reached limit of 10 results, stopping search...")
                return
                
            time.sleep(1)
            self.search_pley_portal()

        except KeyboardInterrupt:
            print("\nScraping interrupted by user")
        except Exception as e:
            print(f"Scraping error: {e}")
        finally:
            self.save_results()


def main():
    scraper = PeruLGBTLawScraper()
    scraper.run()


if __name__ == "__main__":
    main()
