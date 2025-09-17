import requests
import time
from datetime import datetime
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
import re
from ..base import BaseLGBTScraper


class Peru2000LGBTScraper(BaseLGBTScraper):
    def __init__(self):
        super().__init__("2000")

        # 2000 search URL - uses different endpoint
        self.search_base_2000 = "https://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2000.nsf/debusqueda"

    def search_laws_2000(self, search_term, max_results=100):
        """Search for laws in 2000-2001 period using the legacy interface"""
        print(f"Searching 2000-2001 period for: {search_term}")

        # Construct the search URL - 2000 uses Start/Count parameters
        encoded_term = quote(search_term)
        search_url = f"{self.search_base_2000}?SearchView&Query={encoded_term}&SearchOrder=4&Start=1&Count={max_results}"

        try:
            response = self.session.get(search_url, timeout=15)

            if response.status_code == 200:
                return self.parse_search_results_2000(response, search_term, search_url)
            else:
                print(f"  HTTP error {response.status_code}")
                return 0

        except Exception as e:
            print(f"  Search failed: {e}")
            return 0

    def parse_search_results_2000(self, response, search_term, search_url):
        """Parse the search results page for 2000"""
        soup = BeautifulSoup(response.content, "html.parser")

        # Look for links with the 2000 pattern
        law_links = []

        # Find all links that match the law detail pattern for 2000
        all_links = soup.find_all("a", href=True)

        for link in all_links:
            href = link.get("href")
            if href and "opendocument" in href.lower() and "CLProLey2000.nsf" in href:
                # This is likely a law detail link
                # Handle both relative and absolute URLs
                if href.startswith("/"):
                    full_url = f"https://www2.congreso.gob.pe{href}"
                elif not href.startswith("http"):
                    full_url = f"https://www2.congreso.gob.pe/{href}"
                else:
                    full_url = href

                text = link.get_text().strip()

                # Try to extract project number from the text
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
            if self.process_law_page_2000(link_info, search_term):
                processed += 1
            time.sleep(1.2)  # Be respectful with older servers

        return processed

    def process_law_page_2000(self, link_info, search_term):
        """Process individual law page from 2000"""
        try:
            print(f"    Accessing URL: {link_info['url']}")

            # Use curl-compatible headers
            headers = {
                "User-Agent": "curl/8.7.1",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
            }

            response = self.session.get(link_info["url"], timeout=15, headers=headers)

            if response.status_code != 200:
                print(f"    HTTP error {response.status_code}")
                return False

            # Handle encoding correctly - the server returns ISO-8859-1
            if "charset=iso-8859-1" in response.headers.get("content-type", "").lower():
                response.encoding = "iso-8859-1"

            # Fix malformed HTML before parsing
            html_content = response.text
            # Fix common HTML issues in 2000 pages
            html_content = html_content.replace("</script", "</script>")
            # Fix malformed attributes with mixed quotes and commas
            html_content = re.sub(
                r"width='([^']*)',\s*align=\"([^\"]*)\"",
                r'width="\1" align="\2"',
                html_content,
            )
            html_content = re.sub(
                r"width=\"([^\"]*)\",\s*align=\"([^\"]*)\"",
                r'width="\1" align="\2"',
                html_content,
            )
            # Additional fixes for 2000-specific patterns
            html_content = re.sub(
                r"border='([^']*)',\s*cellpadding=\"([^\"]*)\"",
                r'border="\1" cellpadding="\2"',
                html_content,
            )

            soup = BeautifulSoup(html_content, "html.parser")

            page_text = soup.get_text().lower()

            # Check if any of our search terms appear in the page (for metadata)
            found_terms = []
            for term in self.search_terms:
                if term.lower() in page_text:
                    found_terms.append(term)

            # Process the law - search already filtered relevant results
            # Extract law information
            law_info = self.extract_law_info_2000(soup, link_info["url"])

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
                "year": "1995-2001",
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

    def extract_law_info_2000(self, soup, url):
        """Extract structured information from a 2000 law page"""
        info = {}

        # 2000 pages also store data in hidden form fields
        hidden_fields = {}
        for input_tag in soup.find_all("input", {"type": "hidden"}):
            name = input_tag.get("name")
            value = input_tag.get("value", "")
            if name:
                hidden_fields[name] = value

        # Extract from hidden fields (most reliable)
        if "TitIni" in hidden_fields and hidden_fields["TitIni"].strip():
            info["title"] = hidden_fields["TitIni"].strip()

        if "CodIni_web" in hidden_fields and hidden_fields["CodIni_web"].strip():
            info["law_number"] = hidden_fields["CodIni_web"].strip()
        elif "CodIni_web_1" in hidden_fields and hidden_fields["CodIni_web_1"].strip():
            info["law_number"] = hidden_fields["CodIni_web_1"].strip()

        if "FecPres" in hidden_fields and hidden_fields["FecPres"].strip():
            info["date"] = hidden_fields["FecPres"].strip()
        elif "fechapre" in hidden_fields and hidden_fields["fechapre"].strip():
            info["date"] = hidden_fields["fechapre"].strip()

        if "CodUltEsta" in hidden_fields and hidden_fields["CodUltEsta"].strip():
            info["status"] = hidden_fields["CodUltEsta"].strip()

        if "DesPropo" in hidden_fields and hidden_fields["DesPropo"].strip():
            info["proponent"] = hidden_fields["DesPropo"].strip()

        if "DesPerio" in hidden_fields and hidden_fields["DesPerio"].strip():
            info["period"] = hidden_fields["DesPerio"].strip()

        if "DesLegis" in hidden_fields and hidden_fields["DesLegis"].strip():
            info["legislature"] = hidden_fields["DesLegis"].strip()

        if "SumIni" in hidden_fields and hidden_fields["SumIni"].strip():
            summary = hidden_fields["SumIni"].strip()
            info["summary"] = summary[:300] + "..." if len(summary) > 300 else summary

        if "NomCongre" in hidden_fields and hidden_fields["NomCongre"].strip():
            info["authors"] = hidden_fields["NomCongre"].strip()

        if "DesComi" in hidden_fields and hidden_fields["DesComi"].strip():
            committees = hidden_fields["DesComi"].strip()
            info["committees"] = [c.strip() for c in committees.split(",") if c.strip()]

        # Always run table parsing to extract fields not found in hidden fields
        self._parse_table_data_2000(soup, info)

        # Fallback to visible text parsing if both hidden fields and table parsing fail
        text = soup.get_text()

        # Only use text parsing for fields not found in other methods
        if not info.get("title"):
            title_patterns = [
                r"Título:\s*([^\n]+)",
                r"LEY\s+[^.\n]+",
                r"PROPONE\s+[^.\n]+",
            ]
            for pattern in title_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    title = (
                        match.group(1) if len(match.groups()) > 0 else match.group(0)
                    )
                    if len(title.strip()) > 10:
                        info["title"] = title.strip()
                        break

        if not info.get("law_number"):
            law_match = re.search(r"(\d{4,5}/\d{4}-[A-Z]+)", text, re.IGNORECASE)
            if law_match:
                info["law_number"] = law_match.group(1)

        if not info.get("status"):
            status_patterns = ["Al Archivo", "En comisión", "Presentado", "Aprobado"]
            for pattern in status_patterns:
                if pattern.lower() in text.lower():
                    info["status"] = pattern
                    break

        return info

    def _parse_table_data_2000(self, soup, info):
        """Parse data from the visible table structure in 2000 pages"""
        try:
            # Look for tables containing the law data
            tables = soup.find_all("table")

            for table in tables:
                rows = table.find_all("tr")

                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        # Get the label (first cell) and value (remaining cells)
                        label = cells[0].get_text(strip=True).lower()
                        value = " ".join(
                            [cell.get_text(strip=True) for cell in cells[1:]]
                        )

                        if not value:
                            continue

                        # Map labels to our info fields
                        if "período" in label or "periodo" in label:
                            info["period"] = value
                        elif "legislatura" in label:
                            info["legislature"] = value
                        elif "número" in label:
                            info["law_number"] = value
                        elif "fecha presentación" in label:
                            info["date"] = value
                        elif "proponente" in label:
                            info["proponent"] = value
                        elif "título" in label:
                            info["title"] = value
                        elif "sumilla" in label:
                            summary = value
                            info["summary"] = (
                                summary[:300] + "..." if len(summary) > 300 else summary
                            )
                        elif "autores" in label:
                            info["authors"] = value
                        elif "seguimiento" in label:
                            # Extract committee info from seguimiento text
                            if "comisión" in value.lower():
                                # Try to extract committee names
                                committee_match = re.search(
                                    r"comisión[^\n]*?([A-Za-z][^\n]*?)(?:\n|\r|$)",
                                    value,
                                    re.IGNORECASE,
                                )
                                if committee_match:
                                    committee = committee_match.group(1).strip()
                                    info["committees"] = (
                                        [committee] if committee else []
                                    )

                            # Extract status from seguimiento
                            if not info.get("status"):
                                status_patterns = [
                                    "Al Archivo",
                                    "En comisión",
                                    "Presentado",
                                    "Aprobado",
                                    "Decretado",
                                ]
                                for pattern in status_patterns:
                                    if pattern.lower() in value.lower():
                                        info["status"] = pattern
                                        break

        except Exception as e:
            print(f"    Table parsing failed: {e}")

    def search_all_terms_2000(self):
        """Search all LGBT terms for 1995-2001 period"""
        print("Starting LGBT rights law search for Peru Congress 1995-2001...")
        print(f"Search terms: {len(self.search_terms)} terms")
        print()

        total_found = 0

        for i, term in enumerate(self.search_terms):
            try:
                print(f"  Searching term {i + 1}/{len(self.search_terms)}: {term}")
                found = self.search_laws_2000(term)
                total_found += found
                time.sleep(2)  # Be respectful between searches

                # Continue processing all results

            except KeyboardInterrupt:
                print("\nSearch interrupted by user")
                break

        print(
            f"\nSearch completed. Found {len(self.results)} LGBT-related laws from 2000-2001"
        )
        return total_found

    def run(self):
        """Main execution method"""
        try:
            self.search_all_terms_2000()
        except Exception as e:
            print(f"Search error: {e}")
        finally:
            self.save_results()


if __name__ == "__main__":
    scraper = Peru2000LGBTScraper()
    scraper.run()
