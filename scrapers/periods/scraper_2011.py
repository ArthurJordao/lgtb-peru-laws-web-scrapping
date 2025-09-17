from os import link
import requests
import time
from datetime import datetime
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
import re
from ..base import BaseLGBTScraper


class Peru2011LGBTScraper(BaseLGBTScraper):
    def __init__(self):
        super().__init__("2011")

        # 2011 search URL
        self.search_base_2011 = "https://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2011.nsf/debusqueda2"

    def search_laws_2011(self, search_term, max_results=50):
        """Search for laws in 2011 using the historical interface"""
        print(f"Searching 2011 period for: {search_term}")

        # Construct the search URL
        encoded_term = quote(search_term)
        search_url = f"{self.search_base_2011}?SearchView&Query={encoded_term}&SearchOrder=4&SearchMax={max_results}"

        try:
            response = self.session.get(search_url, timeout=15)

            if response.status_code == 200:
                return self.parse_search_results_2011(response, search_term, search_url)
            else:
                print(f"  HTTP error {response.status_code}")
                return 0

        except Exception as e:
            print(f"  Search failed: {e}")
            return 0

    def parse_search_results_2011(self, response, search_term, search_url):
        """Parse the search results page for 2011"""
        soup = BeautifulSoup(response.content, "html.parser")

        # Look for links with the 2011 pattern
        law_links = []

        # Find all links that match the law detail pattern for 2011
        all_links = soup.find_all("a", href=True)

        for link in all_links:
            href = link.get("href")
            if href and "opendocument" in href.lower() and "CLProLey2011.nsf" in href:
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
        for link_info in law_links:
            if self.process_law_page_2011(link_info, search_term):
                processed += 1
            time.sleep(1.0)  # Be respectful with older servers

        return processed

    def extract_project_number(self, text, link_element=None):
        """Extract project number from link text or surrounding context"""
        # Look for patterns like "05405/2015-PE" or "03336/2011-CR"
        project_patterns = [
            r"(\d{4,5}/\d{4}-(?:PE|CR))",  # Main pattern like "05405/2015-PE"
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
        if link_element and link_element.parent:
            parent_text = link_element.parent.get_text()
            for pattern in project_patterns:
                match = re.search(pattern, parent_text, re.IGNORECASE)
                if match:
                    return match.group(1) if len(match.groups()) > 0 else match.group(0)

        return "N/A"

    def process_law_page_2011(self, link_info, search_term):
        """Process individual law page from 2011"""
        try:
            response = self.session.get(link_info["url"], timeout=15)

            if response.status_code != 200:
                return False

            soup = BeautifulSoup(response.content, "html.parser")
            page_text = soup.get_text().lower()

            # Check if any of our search terms appear in the page (for metadata)
            found_terms = []
            for term in self.search_terms:
                if term.lower() in page_text:
                    found_terms.append(term)

            # Process the law - search already filtered relevant results
            # Extract law information
            law_info = self.extract_law_info_2011(soup, link_info["url"])

            result = {
                "search_term_used": search_term,
                "found_terms": found_terms,
                "url": link_info["url"],
                "title": law_info.get("title", link_info["title"]),
                "law_number": law_info.get(
                    "law_number", link_info.get("project_number", "N/A")
                ),
                "date": law_info.get("date", "N/A"),
                "status": law_info.get("status", "N/A"),
                "summary": law_info.get("summary", ""),
                "authors": law_info.get("authors", ""),
                "proponent": law_info.get("proponent", ""),
                "committees": law_info.get("committees", []),
                "period": law_info.get("period", ""),
                "legislature": law_info.get("legislature", ""),
                "content_snippet": self.extract_snippet(
                    page_text, found_terms + [search_term]
                ),
                "year": "2011-2016",
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

    def extract_law_info_2011(self, soup, url):
        """Extract structured information from a 2011 law page"""
        info = {}
        text = soup.get_text()

        # Extract title - look for "Título:" field in 2011 format
        title_patterns = [
            r"Título:\s*([^\n]+)",
            r"LEY\s+[^\n]+",
            r"PROPONE\s+[^\n]+",
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1) if len(match.groups()) > 0 else match.group(0)
                if len(title) > 10:
                    info["title"] = title.strip()
                    break

        # Extract project number - 2011 uses slightly different format
        law_patterns = [
            r"Número:\s*([^\s\n]+)",
            r"(\d{4,5}/\d{4}-(?:PE|CR))",  # Main pattern like "05405/2015-PE"
            r"PROYECTO\s+N[°º]?\s*(\d+)",
        ]

        for pattern in law_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["law_number"] = (
                    match.group(1) if len(match.groups()) > 0 else match.group(0)
                )
                break

        # Extract presentation date - 2011 has "Fecha Presentación:" field
        date_patterns = [
            r"Fecha Presentación:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Fecha:\s*(\d{1,2}/\d{1,2}/\d{4})",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                info["date"] = match.group(1)
                break

        # Extract proponent - 2011 has "Proponente:" field
        proponent_match = re.search(r"Proponente:\s*([^\n]+)", text, re.IGNORECASE)
        if proponent_match:
            info["proponent"] = proponent_match.group(1).strip()

        # Extract period - 2011 has "Período:" field
        period_match = re.search(r"Período:\s*([^\n]+)", text, re.IGNORECASE)
        if period_match:
            info["period"] = period_match.group(1).strip()

        # Extract legislature - 2011 has "Legislatura:" field
        legislature_match = re.search(r"Legislatura:\s*([^\n]+)", text, re.IGNORECASE)
        if legislature_match:
            info["legislature"] = legislature_match.group(1).strip()

        # Extract summary - 2011 has "Sumilla:" field
        summary_match = re.search(r"Sumilla:\s*([^\n]+)", text, re.IGNORECASE)
        if summary_match:
            summary = summary_match.group(1).strip()
            info["summary"] = summary[:300] + "..." if len(summary) > 300 else summary

        # Extract authors - look for "Autores" section
        authors_match = re.search(r"Autores[^:]*:\s*([^\n]+)", text, re.IGNORECASE)
        if authors_match:
            info["authors"] = authors_match.group(1).strip()

        # Extract status from hidden fields or following text patterns
        status_patterns = [
            r'CodUltEsta[^>]*value="([^"]+)"',  # From hidden input
            r"Publicado El Peruano",
            r"En comisión",
            r"Dictamen",
            r"Observado",
            r"Al Archivo",
        ]

        for pattern in status_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["status"] = (
                    match.group(1) if len(match.groups()) > 0 else match.group(0)
                )
                break

        # Extract committees from hidden fields or text
        committees = []

        # First try hidden field pattern
        committee_match = re.search(r'DesComi[^>]*value="([^"]+)"', text)
        if committee_match:
            committee_text = committee_match.group(1)
            if committee_text and committee_text.strip():
                committees = [c.strip() for c in committee_text.split(",") if c.strip()]

        # If not found, try extracting from "Seguimiento" section
        if not committees:
            seguimiento_match = re.search(
                r"Seguimiento:\s*.*?Decretado a\.\.\.\s*([^\n<]+)",
                text,
                re.IGNORECASE | re.DOTALL,
            )
            if seguimiento_match:
                committee_text = seguimiento_match.group(1).strip()
                if committee_text:
                    committees = [committee_text]

        # Alternative pattern for committee assignments in text
        if not committees:
            committee_patterns = [
                r"En comisión\s+([^\n<]+)",
                r"comisión\s+de\s+([^\n<]+)",
                r"Decretado a\.\.\.\s*([^\n<]+)",
            ]

            for pattern in committee_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    committee_text = match.group(1).strip()
                    if committee_text:
                        committees = [committee_text]
                        break

        if committees:
            info["committees"] = committees

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

    def search_all_terms_2011(self):
        """Search all LGBT terms for 2011"""
        print("Starting LGBT rights law search for Peru Congress 2011-2016...")
        print(f"Search terms: {len(self.search_terms)} terms")
        print()

        total_found = 0

        for i, term in enumerate(self.search_terms):
            try:
                found = self.search_laws_2011(term)
                total_found += found
                time.sleep(2)  # Be respectful between searches

                # Progress indicator
                if (i + 1) % 5 == 0:
                    print(f"  Processed {i + 1}/{len(self.search_terms)} terms")

            except KeyboardInterrupt:
                print("\nSearch interrupted by user")
                break

        print(
            f"\nSearch completed. Found {len(self.results)} LGBT-related laws from 2011-2016 period"
        )
        return total_found

    def run(self):
        """Main execution method"""
        try:
            self.search_all_terms_2011()
        except Exception as e:
            print(f"Search error: {e}")
        finally:
            self.save_results()


if __name__ == "__main__":
    scraper = Peru2011LGBTScraper()
    scraper.run()
