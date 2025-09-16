"""
Base scraper class with shared functionality for Peru LGBT law scrapers
"""

import requests
import time
import re
from datetime import datetime
from fake_useragent import UserAgent
from .utils.search_terms import LGBT_SEARCH_TERMS
from .utils.export import DataExporter


class BaseLGBTScraper:
    """Base class for Peru LGBT law scrapers with shared functionality"""

    def __init__(self, period_name):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.period_name = period_name
        self.search_terms = LGBT_SEARCH_TERMS
        self.results = []
        self.exporter = DataExporter()
        self.setup_session()

    def setup_session(self):
        """Setup HTTP session with appropriate headers"""
        headers = {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.session.headers.update(headers)

    def extract_project_number(self, text, link_element=None):
        """Extract project number from text or link context"""
        project_patterns = [
            r"(\\d{4,5}/\\d{4}-(?:PE|CR))",  # Main pattern like "05405/2015-PE"
            r"(\\d{4,5}/\\d{4})",
            r"PL\\s*(\\d+)",
            r"PROYECTO\\s+(\\d+)",
        ]

        # Try the text first
        for pattern in project_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)

        # If not found and we have link element, try parent context
        if link_element and hasattr(link_element, "parent") and link_element.parent:
            parent_text = link_element.parent.get_text()
            for pattern in project_patterns:
                match = re.search(pattern, parent_text, re.IGNORECASE)
                if match:
                    return match.group(1) if len(match.groups()) > 0 else match.group(0)

        return "N/A"

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

    def save_results(self):
        """Save results using the shared exporter"""
        self.exporter.save_results(self.results, self.period_name)

    def run(self):
        """Main execution method - should be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement the run() method")
