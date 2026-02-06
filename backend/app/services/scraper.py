"""
Wikipedia article scraper using BeautifulSoup.
Uses HTML scraping only - NO Wikipedia API.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse


class WikipediaScraper:
    """Scrapes Wikipedia article content from HTML."""
    
    WIKI_PATTERN = re.compile(
        r"^https?://(?:en|www)\.wikipedia\.org/wiki/[^/]+$",
        re.IGNORECASE
    )
    
    def __init__(self, user_agent: str = "WikiQuizGenerator/1.0 (Educational)"):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
    
    def is_valid_wikipedia_url(self, url: str) -> bool:
        """Validate that URL is a Wikipedia article URL."""
        try:
            parsed = urlparse(url)
            return bool(
                parsed.scheme in ("http", "https")
                and "wikipedia.org" in parsed.netloc
                and parsed.path.startswith("/wiki/")
                and "Special:" not in url
                and "File:" not in url
            )
        except Exception:
            return False
    
    def fetch_title_only(self, url: str) -> str:
        """Lightweight fetch - returns only the article title for URL preview."""
        if not self.is_valid_wikipedia_url(url):
            raise ValueError(f"Invalid Wikipedia URL: {url}")
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        title_elem = soup.find("h1", {"id": "firstHeading"}) or soup.find("h1")
        return title_elem.get_text(strip=True) if title_elem else "Unknown"
    
    def fetch_and_parse(self, url: str) -> dict:
        """
        Fetch Wikipedia page and extract structured content.
        Returns dict with: title, summary, sections, content, raw_html, key_entities
        """
        if not self.is_valid_wikipedia_url(url):
            raise ValueError(f"Invalid Wikipedia URL: {url}")
        
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = "utf-8"
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove unwanted elements
        for tag in soup.find_all(["script", "style", "nav", "footer"]):
            tag.decompose()
        for tag in soup.select(".navbox, .infobox, .metadata, .noprint"):
            tag.decompose()
        
        # Get title
        title_elem = soup.find("h1", {"id": "firstHeading"}) or soup.find("h1")
        title = title_elem.get_text(strip=True) if title_elem else "Unknown"
        
        # Get main content div
        content_div = soup.find("div", {"id": "mw-content-text"}) or soup.find("div", {"class": "mw-parser-output"})
        if not content_div:
            raise ValueError("Could not find article content")
        
        # Extract sections
        sections = []
        section_content = {}
        current_section = "Introduction"
        current_text = []
        
        for elem in content_div.find_all(["h2", "h3", "p", "ul", "li"])[:120]:
            if elem.name in ("h2", "h3"):
                if current_text:
                    section_content[current_section] = " ".join(current_text)
                span = elem.find("span", {"class": "mw-headline"})
                current_section = span.get_text(strip=True) if span else elem.get_text(strip=True)
                if current_section and current_section not in ("Contents", "See also", "References", "External links"):
                    sections.append(current_section)
                current_text = []
            elif elem.name in ("p", "li"):
                text = elem.get_text(strip=True)
                if text and len(text) > 20:
                    current_text.append(text)
        
        if current_text:
            section_content[current_section] = " ".join(current_text)
        
        # Build full content (truncate for LLM context)
        full_content = "\n\n".join(
            f"## {sec}\n{section_content.get(sec, '')}"
            for sec in ["Introduction"] + [s for s in sections if s != "Introduction"]
            if section_content.get(sec)
        )
        
        # Summary: first few paragraphs
        intro = section_content.get("Introduction", "")
        summary = intro[:800] + "..." if len(intro) > 800 else intro
        
        return {
    "title": title,
    "summary": summary,
    "sections": sections[:10],
    "content": full_content[:5000],
    "raw_html": html[:30000] if html else None,
    "key_entities": None,
}
