import requests
import time
from datetime import datetime
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import pandas as pd
import re


class PeruHistoricalLGBTScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_session()

        # Historical search URLs (2016 as example)
        self.search_base_2016 = "https://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2016.nsf/debusqueda2"

        # LGBT-related search terms (starting with a few for testing)
        self.search_terms = [
            "no binarie",
            "no binario",
            "no binaria",
            "no-binario",
            "no-binaria",
            "bisex",
            "bisexual",
            "bisexualidad",
            "pareja del mismo sexo",
            "parejas del mismo sexo",
            "matrimonio igualitario",
            "matrimonio entre personas del mismo sexo",
            "gay",
            "gays",
            "comunidad gay",
            "LGBT",
            "LGTB",
            "LGBTI",
            "LGTBI",
            "LGBTIQ",
            "LGBTIQ+",
            "heteronorma",
            "heteronormativo",
            "heteronormatividad",
            "homoafectivo",
            "vínculos homoafectivos",
            "homofobia",
            "homofóbico",
            "homofóbica",
            "homosexual",
            "homosexualidad",
            "identidad de género",
            "reconocimiento de identidad de género",
            "ley de identidad de género",
            "intersex",
            "intersexual",
            "intersexualidad",
            "lesbiana",
            "lesbianas",
            "lesbianidad",
            "lésbico",
            "mismo sexo",
            "del mismo sexo",
            "nombre social",
            "uso de nombre social",
            "orientación sexual",
            "diversidad sexual",
            "no discriminación por orientación sexual",
            "psicosexual",
            "psicosexualidad",
            "queer",
            "transexual",
            "transexualidad",
            "transfobia",
            "transfóbico",
            "transfóbica",
            "transgénero",
            "transgenero",
            # "trans",
            "reasignación de sexo",
            "adecuación de sexo",
            "cirugía de reasignación de sexo",
            "travesti",
            "travestis",
            "unión homoafectiva",
            "unión entre personas del mismo sexo",
            "unión civil",
            "unión civil no matrimonial",
            "crímenes de odio",
            "delitos de odio",
            # "igualdad",
            "no discriminación",
            "cambio de nombre",
            "rectificación de nombre",
            "rectificación de sexo",
        ]

        self.results = []

    def setup_session(self):
        headers = {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.session.headers.update(headers)

    def search_historical_laws_2016(self, search_term, max_results=50):
        """Search for laws in 2016 using the historical interface"""
        print(f"Searching 2016 period for: {search_term}")

        # Construct the search URL
        encoded_term = quote(search_term)
        search_url = f"{self.search_base_2016}?SearchView&Query={encoded_term}&SearchOrder=4&SearchMax={max_results}"

        try:
            response = self.session.get(search_url, timeout=15)

            if response.status_code == 200:
                return self.parse_search_results_2016(response, search_term, search_url)
            else:
                print(f"  HTTP error {response.status_code}")
                return 0

        except Exception as e:
            print(f"  Search failed: {e}")
            return 0

    def parse_search_results_2016(self, response, search_term, search_url):
        """Parse the search results page for 2016"""
        soup = BeautifulSoup(response.content, "html.parser")

        # Based on analysis, look for links with the specific pattern
        # Links are in format: /Sicr/TraDocEstProc/CLProLey2016.nsf/.../...?opendocument
        law_links = []

        # Find all links that match the law detail pattern
        all_links = soup.find_all("a", href=True)

        for link in all_links:
            href = link.get("href")
            if href and "opendocument" in href.lower() and "CLProLey2016.nsf" in href:
                # This is likely a law detail link
                full_url = urljoin("https://www2.congreso.gob.pe", href)
                text = link.get_text().strip()

                # Try to extract project number from the text or surrounding context
                project_num = self.extract_project_number(text, link)

                law_links.append(
                    {
                        "url": full_url,
                        "title": text,
                        "project_number": project_num,
                        "raw_link": href,
                    }
                )

        print(f"  Found {len(law_links)} law detail links")

        # Process each law link
        processed = 0
        for link_info in law_links[:10]:  # Limit for testing
            if self.process_law_page_2016(link_info, search_term):
                processed += 1
            time.sleep(0.8)  # Be respectful with older servers

            if len(self.results) >= 20:  # Overall limit
                print("  Reached result limit, stopping...")
                break

        return processed

    def extract_project_number(self, text, link_element):
        """Extract project number from link text or surrounding context"""
        # Look for pattern like "05493/2020-CR" in text
        project_patterns = [
            r"(\d{4,5}/\d{4}-CR)",
            r"(\d{4,5}/\d{4})",
            r"PL\s*(\d+)",
            r"PROYECTO\s+(\d+)",
        ]

        # First try the link text itself
        for pattern in project_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)

        # If not found in text, look at parent elements
        if link_element.parent:
            parent_text = link_element.parent.get_text()
            for pattern in project_patterns:
                match = re.search(pattern, parent_text, re.IGNORECASE)
                if match:
                    return match.group(1) if len(match.groups()) > 0 else match.group(0)

        return "N/A"

    def process_law_page_2016(self, link_info, search_term):
        """Process individual law page from 2016"""
        try:
            response = self.session.get(link_info["url"], timeout=15)

            if response.status_code != 200:
                return False

            soup = BeautifulSoup(response.content, "html.parser")
            page_text = soup.get_text().lower()

            # Check if any of our search terms appear in the page
            found_terms = []
            for term in self.search_terms:
                if term.lower() in page_text:
                    found_terms.append(term)

            if found_terms or search_term.lower() in page_text:
                # Extract law information
                law_info = self.extract_law_info_2016(soup, link_info["url"])

                result = {
                    "search_term_used": search_term,
                    "found_terms": found_terms,
                    "url": link_info["url"],
                    "title": law_info.get("title", link_info["title"]),
                    "law_number": law_info.get("law_number", "N/A"),
                    "date": law_info.get("date", "N/A"),
                    "status": law_info.get("status", "N/A"),
                    "summary": law_info.get("summary", ""),
                    "content_snippet": self.extract_snippet(
                        page_text, found_terms + [search_term]
                    ),
                    "year": "2016",
                    "scraped_at": datetime.now().isoformat(),
                }

                self.results.append(result)

                print(
                    f"    ✓ {law_info.get('law_number', 'N/A')}: {law_info.get('title', link_info['title'])[:60]}..."
                )
                return True

        except Exception as e:
            print(f"    Error processing {link_info['url']}: {e}")

        return False

    def extract_law_info_2016(self, soup, url):
        """Extract structured information from a 2016 law page"""
        info = {}
        text = soup.get_text()

        # Extract title - look for "LEY" or "PROPONE" patterns
        title_patterns = [
            r"LEY\s+[^.\n]+",
            r"PROPONE\s+[^.\n]+",
            r"OBJETO:\s*([^.\n]+)",
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1) if len(match.groups()) > 0 else match.group(0)
                if len(title) > 10:
                    info["title"] = title.strip()
                    break

        # Extract project number - more specific patterns for 2016 format
        law_patterns = [
            r"(\d{4,5}/\d{4}-CR)",  # Main pattern like "05493/2020-CR"
            r"PROYECTO\s+N[°º]?\s*(\d+)",
            r"PL\s*(\d+)",
        ]

        for pattern in law_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["law_number"] = (
                    match.group(1) if len(match.groups()) > 0 else match.group(0)
                )
                break

        # Extract presentation date - look for "Presentado:" or similar
        date_patterns = [
            r"Presentado:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Fecha:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{1,2}/\d{1,2}/\d{4})",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                info["date"] = match.group(1)
                break

        # Extract status - look for specific status indicators
        status_patterns = [
            r"Al\s+Archivo",
            r"Presentado",
            r"En\s+Comisión",
            r"Aprobado",
            r"Rechazado",
        ]

        for pattern in status_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["status"] = match.group(0)
                break

        # Extract authors/proponents - look for "Proponente:" section
        author_match = re.search(r"Proponente[s]?:\s*([^.\n]+)", text, re.IGNORECASE)
        if author_match:
            info["authors"] = author_match.group(1).strip()

        # Extract committees
        committee_patterns = [
            r"Comisión[es]*:\s*([^.\n]+)",
            r"Comisión\s+de\s+([^.\n]+)",
        ]

        for pattern in committee_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                info["committees"] = matches
                break

        # Extract object/summary - look for "OBJETO:" section
        object_match = re.search(
            r"OBJETO:\s*([^.]+\.)", text, re.IGNORECASE | re.DOTALL
        )
        if object_match:
            summary = object_match.group(1).strip()
            info["summary"] = summary[:300] + "..." if len(summary) > 300 else summary

        return info

    def extract_snippet(self, text, terms, max_length=200):
        """Extract relevant text snippet around found terms"""
        for term in terms:
            if term.lower() in text:
                idx = text.find(term.lower())
                start = max(0, idx - 100)
                end = min(len(text), idx + 100)
                snippet = text[start:end].strip()
                return snippet[:max_length] if len(snippet) > max_length else snippet
        return text[:max_length]

    def search_all_terms_2016(self):
        """Search all LGBT terms for 2016"""
        print("Starting LGBT rights law search for Peru Congress 2016...")
        print(f"Search terms: {', '.join(self.search_terms)}...")  # Show first few
        print()

        total_found = 0

        for term in self.search_terms:
            try:
                found = self.search_historical_laws_2016(term)
                total_found += found
                time.sleep(2)  # Be respectful between searches

                if len(self.results) >= 20:  # Reasonable limit for testing
                    print("Reached limit of 20 results, stopping search...")
                    break

            except KeyboardInterrupt:
                print("\nSearch interrupted by user")
                break

        print(
            f"\nSearch completed. Found {len(self.results)} LGBT-related laws from 2016"
        )
        return total_found

    def save_results(self):
        """Save results in multiple formats"""
        if not self.results:
            print("No LGBT-related laws found for 2016.")
            return

        # Save detailed JSON
        with open("lgbt_laws_2016_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Save as CSV
        df = pd.DataFrame(self.results)
        df.to_csv("lgbt_laws_2016.csv", index=False, encoding="utf-8")

        # Create human-readable summary
        with open("lgbt_laws_2016_summary.txt", "w", encoding="utf-8") as f:
            f.write("LEYES SOBRE DERECHOS LGBT EN PERÚ - 2016\n")
            f.write("=" * 50 + "\n")
            f.write(
                f"Búsqueda realizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Total de proyectos encontrados: {len(self.results)}\n\n")

            for i, law in enumerate(self.results, 1):
                f.write(f"{i}. {law['law_number']} - {law['title'][:80]}...\n")
                f.write(f"   Fecha: {law['date']}\n")
                f.write(f"   Estado: {law['status']}\n")
                f.write(f"   Término de búsqueda: {law['search_term_used']}\n")
                f.write(f"   Términos encontrados: {', '.join(law['found_terms'])}\n")
                f.write(f"   URL: {law['url']}\n")
                f.write(f"   Resumen: {law['summary'][:150]}...\n\n")

        print(f"Results saved:")
        print(f"  - lgbt_laws_2016_results.json (detailed)")
        print(f"  - lgbt_laws_2016.csv (spreadsheet)")
        print(f"  - lgbt_laws_2016_summary.txt (human readable)")

    def run(self):
        """Main execution method"""
        try:
            self.search_all_terms_2016()
        except Exception as e:
            print(f"Search error: {e}")
        finally:
            self.save_results()


if __name__ == "__main__":
    scraper = PeruHistoricalLGBTScraper()
    scraper.run()
