"""
============================================
AutoHire AI - Job Scraper Module
============================================
Automates job scraping from LinkedIn, Indeed, and Naukri using Selenium.
Uses WebDriver Manager for automatic ChromeDriver management.
Implements OOP with a base scraper class and platform-specific subclasses.
"""

import time
import re
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    StaleElementReferenceException, WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager
from database import DatabaseManager
from config import Config


class BaseScraper(ABC):
    """
    Abstract base class for all job scrapers.
    Provides common Selenium setup, teardown, and utility methods.
    Subclasses must implement the `scrape()` method.
    """

    def __init__(self, role=None, location=None):
        """
        Initialize the scraper with search parameters.

        Args:
            role (str): Job role to search for (default from config)
            location (str): Location to search in (default from config)
        """
        self.role = role or Config.SCRAPE_ROLE
        self.location = location or Config.SCRAPE_LOCATION
        self.driver = None
        self.db = DatabaseManager()
        self.jobs = []  # Collected jobs for this scraping session

    def _setup_driver(self):
        """
        Configure and initialize Chrome WebDriver.
        Uses headless mode by default for server environments.
        """
        chrome_options = Options()

        if Config.CHROME_HEADLESS:
            chrome_options.add_argument("--headless=new")

        # Essential Chrome options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")

        # User agent to avoid bot detection
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        # Suppress logging
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            print(f"[SCRAPER] Chrome WebDriver initialized successfully")
        except WebDriverException as e:
            print(f"[SCRAPER ERROR] Failed to initialize WebDriver: {e}")
            raise

    def _teardown_driver(self):
        """Safely close and quit the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                print("[SCRAPER] WebDriver closed")
            except Exception:
                pass

    def _scroll_page(self, scroll_count=3, delay=2):
        """
        Scroll the page to load dynamic content.

        Args:
            scroll_count (int): Number of times to scroll
            delay (float): Seconds to wait between scrolls
        """
        for i in range(scroll_count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)

    def _safe_get_text(self, element, selector, by=By.CSS_SELECTOR, default="N/A"):
        """
        Safely extract text from a child element.
        Returns default value if element is not found.

        Args:
            element: Parent WebElement
            selector (str): CSS selector or other locator
            by: Selenium By locator strategy
            default (str): Default value if not found

        Returns:
            str: Extracted text or default value
        """
        try:
            return element.find_element(by, selector).text.strip()
        except (NoSuchElementException, StaleElementReferenceException):
            return default

    def _safe_get_attribute(self, element, selector, attribute, by=By.CSS_SELECTOR, default=""):
        """
        Safely extract an attribute from a child element.

        Args:
            element: Parent WebElement
            selector (str): CSS selector or other locator
            attribute (str): HTML attribute to extract
            by: Selenium By locator strategy
            default (str): Default value if not found

        Returns:
            str: Extracted attribute value or default
        """
        try:
            return element.find_element(by, selector).get_attribute(attribute) or default
        except (NoSuchElementException, StaleElementReferenceException):
            return default

    def run(self):
        """
        Execute the complete scraping pipeline:
        1. Setup WebDriver
        2. Run platform-specific scraper
        3. Store results in database
        4. Log the scraping session
        5. Teardown WebDriver

        Returns:
            list: List of scraped job dictionaries
        """
        source = self.__class__.__name__.replace('Scraper', '').lower()
        print(f"\n{'='*50}")
        print(f"[SCRAPER] Starting {source.upper()} scraper")
        print(f"[SCRAPER] Role: {self.role} | Location: {self.location}")
        print(f"{'='*50}")

        try:
            self._setup_driver()
            self.jobs = self.scrape()

            # Store jobs in database
            if self.jobs:
                added = self.db.insert_jobs_bulk(self.jobs)
                self.db.log_scrape(source, len(self.jobs), added, 'success')
                print(f"[SCRAPER] {source.upper()}: Found {len(self.jobs)} jobs, added {added} new")
            else:
                self.db.log_scrape(source, 0, 0, 'success')
                print(f"[SCRAPER] {source.upper()}: No jobs found")

            return self.jobs

        except Exception as e:
            error_msg = str(e)
            print(f"[SCRAPER ERROR] {source.upper()} scraping failed: {error_msg}")
            self.db.log_scrape(source, 0, 0, 'failed', error_msg)
            return []

        finally:
            self._teardown_driver()

    @abstractmethod
    def scrape(self):
        """
        Platform-specific scraping logic.
        Must be implemented by each subclass.

        Returns:
            list: List of job dictionaries with keys:
                  job_title, company_name, location, job_link, date_posted, source
        """
        pass


class LinkedInScraper(BaseScraper):
    """
    Scrapes job listings from LinkedIn Jobs.
    Uses LinkedIn's public job search (no login required).
    """

    def scrape(self):
        """
        Scrape LinkedIn Jobs for the configured role and location.

        Returns:
            list: Scraped job listings
        """
        jobs = []
        # LinkedIn public job search URL
        search_query = self.role.replace(' ', '%20')
        location_query = self.location.replace(' ', '%20')
        url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={search_query}&location={location_query}"
        )

        print(f"[LinkedIn] Navigating to: {url}")
        self.driver.get(url)
        time.sleep(4)  # Wait for initial page load

        # Scroll to load more jobs (LinkedIn uses lazy loading)
        self._scroll_page(scroll_count=5, delay=2)

        try:
            # LinkedIn job cards container
            job_cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div.base-card, div.job-search-card, li.jobs-search-results__list-item"
            )
            print(f"[LinkedIn] Found {len(job_cards)} job cards")

            for card in job_cards[:30]:  # Limit to 30 jobs per session
                try:
                    # Extract job details from each card
                    title = self._safe_get_text(
                        card,
                        "h3.base-search-card__title, h3.job-search-card__title, "
                        "a.job-card-list__title"
                    )
                    company = self._safe_get_text(
                        card,
                        "h4.base-search-card__subtitle, h4.job-search-card__company-name, "
                        "a.job-card-container__company-name"
                    )
                    location = self._safe_get_text(
                        card,
                        "span.job-search-card__location, "
                        "li.job-card-container__metadata-item"
                    )
                    link = self._safe_get_attribute(
                        card,
                        "a.base-card__full-link, a.job-card-list__title, "
                        "a.job-card-container__link",
                        "href"
                    )
                    date_posted = self._safe_get_text(
                        card,
                        "time.job-search-card__listdate, "
                        "time.job-search-card__listdate--new"
                    )

                    # Only add if we have minimum required data
                    if title != "N/A" and link:
                        jobs.append({
                            'job_title': title,
                            'company_name': company,
                            'location': location,
                            'job_link': link.split('?')[0],  # Clean URL
                            'date_posted': date_posted,
                            'source': 'linkedin'
                        })
                except Exception as e:
                    print(f"[LinkedIn] Error parsing card: {e}")
                    continue

        except Exception as e:
            print(f"[LinkedIn] Error finding job cards: {e}")

        return jobs


class IndeedScraper(BaseScraper):
    """
    Scrapes job listings from Indeed.
    Uses Indeed's search with keyword and location parameters.
    """

    def scrape(self):
        """
        Scrape Indeed for the configured role and location.

        Returns:
            list: Scraped job listings
        """
        jobs = []
        search_query = self.role.replace(' ', '+')
        location_query = self.location.replace(' ', '+')
        url = f"https://www.indeed.com/jobs?q={search_query}&l={location_query}"

        print(f"[Indeed] Navigating to: {url}")
        self.driver.get(url)
        time.sleep(4)

        try:
            # Indeed job cards
            job_cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div.job_seen_beacon, div.jobsearch-ResultsList > div, "
                "div.cardOutline, td.resultContent"
            )
            print(f"[Indeed] Found {len(job_cards)} job cards")

            for card in job_cards[:30]:
                try:
                    title = self._safe_get_text(
                        card,
                        "h2.jobTitle span, a.jcs-JobTitle span, "
                        "h2.jobTitle a"
                    )
                    company = self._safe_get_text(
                        card,
                        "span.companyName, span[data-testid='company-name'], "
                        "span.css-63koeb"
                    )
                    location = self._safe_get_text(
                        card,
                        "div.companyLocation, div[data-testid='text-location'], "
                        "span.css-1p0sjhy"
                    )
                    link = self._safe_get_attribute(
                        card,
                        "a.jcs-JobTitle, h2.jobTitle a, a[data-jk]",
                        "href"
                    )
                    date_posted = self._safe_get_text(
                        card,
                        "span.date, span.css-qvloho"
                    )

                    # Build full URL if relative link
                    if link and not link.startswith('http'):
                        link = f"https://www.indeed.com{link}"

                    if title != "N/A" and link:
                        jobs.append({
                            'job_title': title,
                            'company_name': company,
                            'location': location,
                            'job_link': link.split('&')[0] if '&' in link else link,
                            'date_posted': date_posted,
                            'source': 'indeed'
                        })
                except Exception as e:
                    print(f"[Indeed] Error parsing card: {e}")
                    continue

        except Exception as e:
            print(f"[Indeed] Error finding job cards: {e}")

        return jobs


class NaukriScraper(BaseScraper):
    """
    Scrapes job listings from Naukri.com.
    Handles Naukri's specific page structure and dynamic loading.
    """

    def scrape(self):
        """
        Scrape Naukri.com for the configured role and location.

        Returns:
            list: Scraped job listings
        """
        jobs = []
        search_query = self.role.replace(' ', '-')
        location_query = self.location.replace(' ', '-')
        url = f"https://www.naukri.com/{search_query}-jobs-in-{location_query}"

        print(f"[Naukri] Navigating to: {url}")
        self.driver.get(url)
        time.sleep(4)

        # Scroll to load all job cards
        self._scroll_page(scroll_count=4, delay=2)

        try:
            # Naukri job cards
            job_cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                "article.jobTuple, div.srp-jobtuple-wrapper, "
                "div.cust-job-tuple, div.list > article"
            )
            print(f"[Naukri] Found {len(job_cards)} job cards")

            for card in job_cards[:30]:
                try:
                    title = self._safe_get_text(
                        card,
                        "a.title, a.job-title-href, "
                        "a[class*='title']"
                    )
                    company = self._safe_get_text(
                        card,
                        "a.subTitle, a.comp-name, "
                        "a[class*='companyName'], span.comp-name"
                    )
                    location = self._safe_get_text(
                        card,
                        "span.locWdth, span.loc-wrap, "
                        "span[class*='location'], li.location span"
                    )
                    link = self._safe_get_attribute(
                        card,
                        "a.title, a.job-title-href, "
                        "a[class*='title']",
                        "href"
                    )
                    date_posted = self._safe_get_text(
                        card,
                        "span.date, span.job-post-day, "
                        "span[class*='freshness']"
                    )

                    if title != "N/A" and link:
                        jobs.append({
                            'job_title': title,
                            'company_name': company,
                            'location': location,
                            'job_link': link,
                            'date_posted': date_posted,
                            'source': 'naukri'
                        })
                except Exception as e:
                    print(f"[Naukri] Error parsing card: {e}")
                    continue

        except Exception as e:
            print(f"[Naukri] Error finding job cards: {e}")

        return jobs


class JobScraperManager:
    """
    Orchestrates all scrapers and manages the scraping pipeline.
    Provides a single entry point to run all or specific scrapers.
    """

    def __init__(self, role=None, location=None):
        """
        Initialize the scraper manager.

        Args:
            role (str): Job role to search for
            location (str): Location to search in
        """
        self.role = role
        self.location = location
        self.scrapers = {
            'linkedin': LinkedInScraper,
            'indeed': IndeedScraper,
            'naukri': NaukriScraper
        }

    def run_all(self):
        """
        Run all registered scrapers sequentially.

        Returns:
            dict: Results keyed by platform name
        """
        results = {}
        total_jobs = 0

        print("\n" + "=" * 60)
        print("  AutoHire AI - Starting Full Scraping Pipeline")
        print("=" * 60)

        for name, scraper_class in self.scrapers.items():
            try:
                scraper = scraper_class(self.role, self.location)
                jobs = scraper.run()
                results[name] = jobs
                total_jobs += len(jobs)
            except Exception as e:
                print(f"[MANAGER] {name} scraper failed: {e}")
                results[name] = []

        print(f"\n{'='*60}")
        print(f"  Scraping Complete! Total jobs found: {total_jobs}")
        print(f"{'='*60}\n")

        return results

    def run_single(self, platform):
        """
        Run a single platform scraper.

        Args:
            platform (str): Platform name (linkedin, indeed, naukri)

        Returns:
            list: Scraped jobs from the platform
        """
        if platform not in self.scrapers:
            print(f"[MANAGER] Unknown platform: {platform}")
            return []

        scraper = self.scrapers[platform](self.role, self.location)
        return scraper.run()


# ============================================
# CLI Entry Point for standalone scraping
# ============================================
if __name__ == "__main__":
    print("AutoHire AI - Job Scraper")
    print("-" * 40)
    manager = JobScraperManager()
    results = manager.run_all()

    for platform, jobs in results.items():
        print(f"\n{platform.upper()}: {len(jobs)} jobs found")
        for job in jobs[:3]:  # Show first 3 from each
            print(f"  - {job['job_title']} at {job['company_name']} ({job['location']})")
