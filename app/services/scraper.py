import requests
import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BrightDataScraper:
    """BrightData scraper for job data from LinkedIn and Glassdoor"""

    def __init__(self):
        self.api_key = settings.BRIGHTDATA_API_KEY
        self.trigger_url = settings.BRIGHTDATA_TRIGGER_URL
        self.progress_url = settings.BRIGHTDATA_PROGRESS_URL
        self.download_url = settings.BRIGHTDATA_DOWNLOAD_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _trigger_snapshot(
        self,
        dataset_id: str,
        data: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Trigger a BrightData snapshot and return snapshot_id

        Args:
            dataset_id: BrightData dataset identifier
            data: Request data payload

        Returns:
            snapshot_id if successful, None otherwise
        """
        params = {
            "dataset_id": dataset_id,
            "include_errors": "true",
            "type": "discover_new",
            "discover_by": "keyword",
            "limit_per_input": "5",
        }

        try:
            logger.info(f"🚀 Triggering snapshot for dataset: {dataset_id}")
            response = requests.post(
                self.trigger_url,
                params=params,
                json=data,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            snapshot_id = result.get("snapshot_id")

            if snapshot_id:
                logger.info(f"✅ Snapshot triggered: {snapshot_id}")
                return snapshot_id
            else:
                logger.error("❌ No snapshot_id in response")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error triggering snapshot: {str(e)}")
            return None

    def _poll_snapshot_status(
        self,
        snapshot_id: str,
        max_attempts: int = 60,
        delay: int = 5
    ) -> bool:
        """
        Poll snapshot status until ready or failed

        Args:
            snapshot_id: Snapshot identifier
            max_attempts: Maximum polling attempts
            delay: Delay between attempts in seconds

        Returns:
            True if ready, False otherwise
        """
        progress_url = f"{self.progress_url}/{snapshot_id}"

        for attempt in range(max_attempts):
            try:
                logger.info(
                    f"⏳ Checking snapshot progress... (attempt {attempt + 1}/{max_attempts})")

                response = requests.get(
                    progress_url, headers=self.headers, timeout=10)
                response.raise_for_status()

                progress_data = response.json()
                status = progress_data.get("status")

                if status == "ready":
                    logger.info("✅ Snapshot completed!")
                    return True
                elif status == "failed":
                    logger.error("❌ Snapshot failed")
                    return False
                elif status == "running":
                    logger.info("🔄 Still processing...")
                    time.sleep(delay)
                else:
                    logger.warning(f"❓ Unknown status: {status}")
                    time.sleep(delay)

            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Error checking progress: {str(e)}")
                time.sleep(delay)

        logger.error("⏰ Timeout waiting for snapshot completion")
        return False

    def _download_snapshot(
        self,
        snapshot_id: str,
        format: str = "json"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Download completed snapshot data

        Args:
            snapshot_id: Snapshot identifier
            format: Download format (json, csv, etc.)

        Returns:
            List of job data dictionaries
        """
        download_url = f"{self.download_url}/{snapshot_id}?format={format}"

        try:
            logger.info("📥 Downloading snapshot data...")

            response = requests.get(
                download_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            count = len(data) if isinstance(data, list) else 1
            logger.info(f"🎉 Successfully downloaded {count} items")

            return data if isinstance(data, list) else [data]

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error downloading snapshot: {str(e)}")
            return None

    def _trigger_and_download(
        self,
        dataset_id: str,
        data: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Complete workflow: trigger → poll → download

        Args:
            dataset_id: BrightData dataset ID
            data: Request payload

        Returns:
            Downloaded data or None
        """
        # Step 1: Trigger snapshot
        snapshot_id = self._trigger_snapshot(dataset_id, data)
        if not snapshot_id:
            return None

        # Step 2: Poll until ready
        if not self._poll_snapshot_status(snapshot_id):
            return None

        # Step 3: Download data
        return self._download_snapshot(snapshot_id)

    def scrape_linkedin_jobs(
        self,
        keywords: str,
        location: str = "Remote",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape job listings from LinkedIn via BrightData

        Args:
            keywords: Search keywords
            location: Job location
            limit: Maximum number of results

        Returns:
            List of job dictionaries
        """
        logger.info(f"🔍 Scraping LinkedIn for: {keywords} in {location}")

        dataset_id = settings.BRIGHTDATA_DATASET_ID_LINKEDIN or "gd_lpfll7v5hcqtkxl6l"

        data = [
            {
                "keyword": keywords,
                "location": location,
                "limit": limit
            }
        ]

        try:
            raw_data = self._trigger_and_download(dataset_id, data)

            if not raw_data:
                logger.warning("No data returned from LinkedIn")
                return []

            jobs = self._parse_linkedin_response(raw_data)
            logger.info(f"✅ Successfully scraped {len(jobs)} LinkedIn jobs")
            return jobs

        except Exception as e:
            logger.error(f"❌ LinkedIn scraping failed: {str(e)}")
            return []

    def scrape_glassdoor_jobs(
        self,
        keywords: str,
        location: str = "Remote",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape job listings from Glassdoor via BrightData

        Args:
            keywords: Search keywords
            location: Job location
            limit: Maximum number of results

        Returns:
            List of job dictionaries
        """
        logger.info(f"🔍 Scraping Glassdoor for: {keywords} in {location}")

        dataset_id = settings.BRIGHTDATA_DATASET_ID_GLASSDOOR or "gd_lpfbbndm1xnopbrcr0"

        data = [
            {
                "keyword": keywords,
                "location": location,
                "limit": limit
            }
        ]

        try:
            raw_data = self._trigger_and_download(dataset_id, data)

            if not raw_data:
                logger.warning("No data returned from Glassdoor")
                return []

            jobs = self._parse_glassdoor_response(raw_data)
            logger.info(f"✅ Successfully scraped {len(jobs)} Glassdoor jobs")
            return jobs

        except Exception as e:
            logger.error(f"❌ Glassdoor scraping failed: {str(e)}")
            return []

    async def scrape_all_sources(
        self,
        keywords: str,
        location: str = "Remote",
        limit_per_source: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape jobs from all sources concurrently

        Args:
            keywords: Search keywords
            location: Job location
            limit_per_source: Max results per source

        Returns:
            Combined list of jobs from all sources
        """
        logger.info(f"🚀 Starting concurrent scraping for: {keywords}")

        # Use ThreadPoolExecutor to run synchronous scraping concurrently
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=2) as executor:
            linkedin_future = loop.run_in_executor(
                executor,
                self.scrape_linkedin_jobs,
                keywords,
                location,
                limit_per_source
            )
            glassdoor_future = loop.run_in_executor(
                executor,
                self.scrape_glassdoor_jobs,
                keywords,
                location,
                limit_per_source
            )

            # Wait for both to complete
            linkedin_jobs, glassdoor_jobs = await asyncio.gather(
                linkedin_future,
                glassdoor_future,
                return_exceptions=True
            )

        # Combine results
        all_jobs = []

        if isinstance(linkedin_jobs, list):
            all_jobs.extend(linkedin_jobs)
        elif isinstance(linkedin_jobs, Exception):
            logger.error(f"LinkedIn scraping error: {str(linkedin_jobs)}")

        if isinstance(glassdoor_jobs, list):
            all_jobs.extend(glassdoor_jobs)
        elif isinstance(glassdoor_jobs, Exception):
            logger.error(f"Glassdoor scraping error: {str(glassdoor_jobs)}")

        logger.info(f"✅ Total jobs scraped: {len(all_jobs)}")
        return all_jobs

    def _parse_linkedin_response(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse BrightData LinkedIn response into standardized format"""
        jobs = []

        for item in raw_data:
            try:
                job = {
                    "job_id": f"linkedin_{item.get('job_posting_id', item.get('job_id', ''))}",
                    "title": item.get("job_title", ""),
                    "company": item.get("company_name", ""),
                    "location": item.get("job_location", ""),
                    "country": item.get("country", item.get("discovery_input", {}).get("country", "")),
                    "job_type": item.get("discovery_input", {}).get("job_type", ""),
                    "experience_level": item.get("discovery_input", {}).get("experience_level", ""),
                    "remote": item.get("discovery_input", {}).get("remote", ""),
                    "job_employment_type": item.get("job_employment_type", ""),
                    "job_summary": item.get("job_summary", item.get("job_overview", "")),
                    "job_industries": item.get("job_industries", item.get("company_industry", item.get("company_sector", ""))),
                    "job_function": item.get("job_function", ""),
                    "job_seniority_level": item.get("job_seniority_level", ""),
                    "job_base_pay_range": item.get("job_base_pay_range", ""),
                    "posted_date": item.get("job_posted_date", ""),
                    "apply_url": item.get("url", item.get("job_url", "")),
                    "employee_benefit_reviews": item.get("employee_benefit_reviews", []),
                    "source": "LinkedIn",
                    "raw_data": item
                }
                jobs.append(job)
            except Exception as e:
                logger.warning(f"Failed to parse LinkedIn job: {str(e)}")
                continue

        return jobs

    def _parse_glassdoor_response(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse BrightData Glassdoor response into standardized format"""
        jobs = []

        for item in raw_data:
            try:
                job = {
                    "job_id": f"glassdoor_{item.get('job_id', '')}",
                    "title": item.get("job_title", ""),
                    "company": item.get("company_name", ""),
                    "location": item.get("job_location", ""),
                    "country": item.get("country", item.get("discovery_input", {}).get("country", "")),
                    "job_type": item.get("discovery_input", {}).get("job_type", ""),
                    "experience_level": item.get("discovery_input", {}).get("experience_level", ""),
                    "remote": item.get("discovery_input", {}).get("remote", ""),
                    "job_employment_type": item.get("job_employment_type", ""),
                    "job_summary": item.get("job_description", item.get("job_overview", "")),
                    "job_industries": item.get("job_industries", item.get("company_industry", item.get("company_sector", ""))),
                    "job_function": item.get("job_function", ""),
                    "job_seniority_level": item.get("job_seniority_level", ""),
                    "job_base_pay_range": item.get("salary_estimate", ""),
                    "posted_date": item.get("job_posted_date", ""),
                    "apply_url": item.get("url", item.get("job_url", "")),
                    "employee_benefit_reviews": item.get("employee_benefit_reviews", []),
                    "source": "Glassdoor",
                    "raw_data": item
                }
                jobs.append(job)
            except Exception as e:
                logger.warning(f"Failed to parse Glassdoor job: {str(e)}")
                continue

        return jobs
