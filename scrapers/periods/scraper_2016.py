import time
from datetime import datetime
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
import re
from ..base import BaseLGBTScraper


class Peru2016LGBTScraper(BaseLGBTScraper):
    def __init__(self):
        super().__init__("2016")

        # Historical search URLs (2016 as example)
        self.search_base_2016 = "https://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2016.nsf/debusqueda2"

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
        for link_info in law_links:
            if self.process_law_page_2016(link_info, search_term):
                processed += 1
            time.sleep(0.8)  # Be respectful with older servers


        return processed

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
                    "authors": law_info.get("authors", ""),
                    "proponent": law_info.get("proponent", ""),
                    "committees": law_info.get("committees", []),
                    "period": law_info.get("period", ""),
                    "legislature": law_info.get("legislature", ""),
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

        # Extract authors - in 2016, authors are listed after "Grupo Parlamentario:" line
        author_match = re.search(
            r"Grupo Parlamentario:[^\n]*\n([^\n]+(?:,[^\n]+)*)", text, re.IGNORECASE
        )
        if author_match:
            info["authors"] = author_match.group(1).strip()

        # Extract proponent - 2016 has "Proponente:" field
        proponent_match = re.search(r"Proponente:\s*([^\n]+)", text, re.IGNORECASE)
        if proponent_match:
            info["proponent"] = proponent_match.group(1).strip()

        # Extract period - 2016 has "Período Parlamentario:" field
        period_match = re.search(
            r"Período\s*Parlamentario:\s*([^\n]+)", text, re.IGNORECASE
        )
        if period_match:
            info["period"] = period_match.group(1).strip()

        # Extract legislature - 2016 has "Legislatura:" field
        legislature_match = re.search(r"Legislatura:\s*([^\n]+)", text, re.IGNORECASE)
        if legislature_match:
            info["legislature"] = legislature_match.group(1).strip()

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

        # Extract summary - use a simple text extraction approach
        # Look for the "Objeto del Proyecto de Ley:" section in the text
        if "Objeto del Proyecto de Ley:" in text:
            # Find the position and extract text after it
            obj_pos = text.find("Objeto del Proyecto de Ley:")
            if obj_pos != -1:
                # Get text starting from this position
                remaining_text = text[obj_pos + len("Objeto del Proyecto de Ley:"):]
                
                # Extract the first meaningful sentence/paragraph
                lines = remaining_text.split('\n')
                summary_lines = []
                
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 10 and not line.startswith(('http', 'www')):
                        # Skip navigation/header lines
                        if any(word in line.lower() for word in ['menu', 'navigation', 'congreso', 'inicio', 'buscar']):
                            continue
                        summary_lines.append(line)
                        # Stop after getting enough content (around 300 chars)
                        if len(' '.join(summary_lines)) > 200:
                            break
                
                if summary_lines:
                    summary = ' '.join(summary_lines).strip()
                    # Clean up extra whitespace
                    summary = re.sub(r'\s+', ' ', summary)
                    if len(summary) > 20:
                        info["summary"] = summary[:300] + "..." if len(summary) > 300 else summary

        return info

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


            except KeyboardInterrupt:
                print("\nSearch interrupted by user")
                break

        print(
            f"\nSearch completed. Found {len(self.results)} LGBT-related laws from 2016"
        )
        return total_found

    def run(self):
        """Main execution method"""
        try:
            self.search_all_terms_2016()
        except Exception as e:
            print(f"Search error: {e}")
        finally:
            self.save_results()


if __name__ == "__main__":
    scraper = Peru2016LGBTScraper()
    scraper.run()
