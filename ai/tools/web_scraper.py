"""
Web scraping tools for job postings and company research.
Uses requests + BeautifulSoup for scraping, and DuckDuckGo for search.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urlparse, quote_plus


class WebScraper:
    """Tool for scraping job postings and company information"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_job_posting(self, url: str) -> Dict[str, str]:
        """Scrape job posting from URL."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            job_data = {"title": "", "company": "", "description": "", "url": url}
            
            # Extract title
            for sel in ['h1.job-title', 'h1', '.job-title', '.posting-headline']:
                elem = soup.select_one(sel)
                if elem and elem.get_text(strip=True):
                    job_data["title"] = elem.get_text(strip=True)
                    break
            
            # Extract company
            for sel in ['.company-name', '.topcard__org-name-link', '[data-testid="companyName"]']:
                elem = soup.select_one(sel)
                if elem:
                    job_data["company"] = elem.get_text(strip=True)
                    break
            
            if not job_data["company"]:
                job_data["company"] = self._extract_company_from_url(url)
            
            # Extract description
            for sel in ['.job-description', '.description__text', '#job-details', 'article']:
                elem = soup.select_one(sel)
                if elem:
                    job_data["description"] = elem.get_text(separator='\n', strip=True)
                    break
            
            if not job_data["description"]:
                main = soup.find('main') or soup.find('body')
                if main:
                    job_data["description"] = main.get_text(separator='\n', strip=True)[:5000]
            
            return job_data
        except Exception as e:
            return {"title": "", "company": "", "description": "", "error": str(e), "url": url}
    
    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from job board URL patterns"""
        parsed = urlparse(url)
        if 'greenhouse.io' in parsed.netloc or 'lever.co' in parsed.netloc:
            parts = parsed.path.strip('/').split('/')
            if parts:
                return parts[0].replace('-', ' ').title()
        return ""

    
    def search_company_info(self, company_name: str) -> Dict[str, list]:
        """Search for company engineering blog, tech stack using DuckDuckGo."""
        intel = {
            "company_name": company_name,
            "engineering_blog": [],
            "tech_stack": [],
            "recent_news": []
        }
        
        if not company_name:
            return intel
        
        searches = [
            (f"{company_name} engineering blog", "engineering_blog"),
            (f"{company_name} tech stack technology 2024", "tech_stack"),
        ]
        
        for query, key in searches:
            intel[key] = self._duckduckgo_search(query, num_results=3)
        
        return intel
    
    def _duckduckgo_search(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """Perform DuckDuckGo search."""
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('.result')[:num_results]:
                title = result.select_one('.result__title')
                snippet = result.select_one('.result__snippet')
                link = result.select_one('.result__url')
                
                if title:
                    results.append({
                        "title": title.get_text(strip=True),
                        "snippet": snippet.get_text(strip=True) if snippet else "",
                        "url": link.get_text(strip=True) if link else ""
                    })
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def extract_tech_from_url(self, url: str, job_keywords: List[str] = None) -> List[str]:
        """Scrape URL and extract mentioned technologies/keywords relevant to the job."""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True).lower()
            
            # If job keywords provided, look for those specifically
            if job_keywords:
                return [kw for kw in job_keywords if kw.lower() in text][:10]
            
            # Fallback: return empty (let LLM analyze instead)
            return []
        except Exception:
            return []


web_scraper = WebScraper()
