# Craigslist Scraper for Cincinnati/Northern Kentucky
# Scrapes junk removal and related service posts

import requests
from bs4 import BeautifulSoup
import random
import time
import re
from datetime import datetime
from config import Config

class CincinnatiCraigslistScraper:
    """Scraper for Cincinnati and Northern Kentucky Craigslist"""

    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.last_check_time = None

    def _get_headers(self):
        """Get randomized headers to avoid blocking"""
        return {
            'User-Agent': random.choice(self.config.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def _make_request(self, url, max_retries=3):
        """Make HTTP request with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, headers=self._get_headers(), timeout=15)
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    # Rate limited, wait longer
                    time.sleep(30)
                elif response.status_code == 404:
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Request error (attempt {attempt + 1}): {e}")
                time.sleep(5)

        return None

    def fetch_leads(self):
        """Fetch leads from all Craigslist sources"""
        leads = []

        # Fetch from Cincinnati main site
        cincinnati_leads = self._scrape_section(
            f"{self.config.CINCINNATI_CRAIGSLIST_URL}/search/hsh",
            'cincinnati'
        )
        leads.extend(cincinnati_leads)

        # Fetch from NKY section
        nky_leads = self._scrape_section(
            f"{self.config.CINCINNATI_CRAIGSLIST_URL}/search/nky/hsh",
            'cincinnati_nky'
        )
        leads.extend(nky_leads)

        # Fetch from Services section
        services_leads = self._scrape_section(
            f"{self.config.CINCINNATI_CRAIGSLIST_URL}/search/sss",
            'cincinnati'
        )
        leads.extend(services_leads)

        return leads

    def _scrape_section(self, url, source_name):
        """Scrape a specific Craigslist section"""
        leads = []

        try:
            # Add query parameters for junk removal
            query_url = f"{url}?query=junk+removal&sort=date"

            response = self._make_request(query_url)
            if not response:
                return leads

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('li', class_='result-row')

            for result in results[:self.config.MAX_LEADS_PER_CHECK]:
                try:
                    lead = self._parse_result(result, source_name)
                    if lead:
                        leads.append(lead)
                except Exception as e:
                    print(f"Error parsing result: {e}")
                    continue

            # Also check recent posts without query
            recent_url = f"{url}?sort=date"
            response = self._make_request(recent_url)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.find_all('li', class_='result-row')

                for result in results[:10]:
                    try:
                        lead = self._parse_result(result, source_name)
                        if lead:
                            # Avoid duplicates
                            if not any(l['source_url'] == lead['source_url'] for l in leads):
                                leads.append(lead)
                    except Exception as e:
                        continue

        except Exception as e:
            print(f"Error scraping section {url}: {e}")

        return leads

    def _parse_result(self, result, source_name):
        """Parse a single Craigslist result"""
        # Get title and link
        title_elem = result.find('a', class_='result-title')
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)
        url = title_elem.get('href', '')

        # Get price
        price_elem = result.find('span', class_='result-price')
        price = price_elem.get_text(strip=True) if price_elem else ''

        # Get location
        location_elem = result.find('span', class_='result-hood')
        location = location_elem.get_text(strip=True) if location_elem else ''

        # Get posted time
        time_elem = result.find('time', class_='result-date')
        posted_time = time_elem.get('datetime') if time_elem else datetime.now().isoformat()

        # Fetch full description
        description = self._get_description(url)

        # Create lead object
        lead = {
            'source': 'craigslist',
            'source_url': url,
            'title': title,
            'description': description,
            'location': location,
            'price': price,
            'posted_time': posted_time,
            'discovered_time': datetime.now().isoformat(),
            'source_name': source_name
        }

        return lead

    def _get_description(self, url):
        """Fetch full post description"""
        try:
            response = self._make_request(url)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                section = soup.find('section', id='postingbody')
                if section:
                    # Remove unwanted elements
                    for unwanted in section.find_all(['script', 'style', 'aside']):
                        unwanted.decompose()
                    return section.get_text(strip=True)
        except Exception as e:
            print(f"Error fetching description: {e}")

        return ''

    def fetch_matching_posts(self, keywords):
        """Fetch posts matching specific keywords"""
        all_leads = self.fetch_leads()
        matching = []

        for lead in all_leads:
            text = f"{lead['title']} {lead['description']}".lower()
            if any(kw.lower() in text for kw in keywords):
                matching.append(lead)

        return matching


class LeadSourceScraper:
    """Base class for other lead sources"""

    def __init__(self):
        self.config = Config()

    def fetch_leads(self):
        """Override in subclass"""
        return []
