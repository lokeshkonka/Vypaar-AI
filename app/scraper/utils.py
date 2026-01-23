"""Utility functions for web scraping."""

import time
from functools import wraps
from typing import Any, Callable, Optional

from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import requests

from app.config import settings
from app.core.exceptions import ScraperError


class RateLimiter:
    """Rate limiter for API/web requests."""

    def __init__(self, requests_per_minute: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0

    def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=settings.scrape_rate_limit)


def with_rate_limit(func: Callable) -> Callable:
    """Decorator to apply rate limiting to a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        rate_limiter.wait()
        return func(*args, **kwargs)
    return wrapper


def retry_on_failure(
    max_attempts: int = 3,
    min_wait: int = 2,
    max_wait: int = 10
) -> Callable:
    """
    Decorator to retry function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((requests.RequestException, ScraperError)),
        reraise=True,
    )


def get_session(
    timeout: int = 30,
    headers: Optional[dict[str, str]] = None
) -> requests.Session:
    """
    Create a requests session with default settings.
    
    Args:
        timeout: Request timeout in seconds
        headers: Custom headers
        
    Returns:
        Configured requests session
    """
    session = requests.Session()
    
    default_headers = {
        "User-Agent": settings.scrape_user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    if headers:
        default_headers.update(headers)
    
    session.headers.update(default_headers)
    
    return session


def safe_get(
    url: str,
    session: Optional[requests.Session] = None,
    timeout: int = 30,
    **kwargs
) -> requests.Response:
    """
    Safely fetch a URL with error handling.
    
    Args:
        url: URL to fetch
        session: Requests session to use
        timeout: Request timeout
        **kwargs: Additional arguments for requests.get
        
    Returns:
        Response object
        
    Raises:
        ScraperError: If request fails
    """
    if session is None:
        session = get_session(timeout=timeout)
    
    try:
        response = session.get(url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.Timeout as e:
        raise ScraperError(f"Request timeout for {url}", details={"error": str(e)})
    except requests.RequestException as e:
        raise ScraperError(
            f"Request failed for {url}",
            details={"error": str(e), "status_code": getattr(e.response, "status_code", None)}
        )


def clean_text(text: Optional[str]) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = " ".join(text.split())
    
    # Remove special characters but keep basic punctuation
    cleaned = cleaned.strip()
    
    return cleaned


def parse_float(value: Any, default: float = 0.0) -> float:
    """
    Safely parse value to float.
    
    Args:
        value: Value to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed float value
    """
    if value is None:
        return default
    
    try:
        # Handle string values with commas (e.g., "1,234.56")
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Failed to parse float from: {value}")
        return default


def parse_int(value: Any, default: int = 0) -> int:
    """
    Safely parse value to integer.
    
    Args:
        value: Value to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed integer value
    """
    if value is None:
        return default
    
    try:
        # Handle string values with commas
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return int(float(value))
    except (ValueError, TypeError):
        logger.warning(f"Failed to parse int from: {value}")
        return default


def extract_table_data(table, headers: Optional[list[str]] = None) -> list[dict[str, Any]]:
    """
    Extract data from an HTML table.
    
    Args:
        table: BeautifulSoup table element
        headers: Optional list of header names
        
    Returns:
        List of dictionaries containing table data
    """
    data = []
    
    # Get headers from table if not provided
    if headers is None:
        header_row = table.find("thead")
        if header_row:
            headers = [clean_text(th.get_text()) for th in header_row.find_all("th")]
        else:
            # Try to get headers from first row
            first_row = table.find("tr")
            if first_row:
                headers = [clean_text(th.get_text()) for th in first_row.find_all(["th", "td"])]
    
    if not headers:
        logger.warning("No headers found in table")
        return data
    
    # Extract data rows
    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]  # Skip header row
    
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) == len(headers):
            row_data = {
                headers[i]: clean_text(cells[i].get_text())
                for i in range(len(headers))
            }
            data.append(row_data)
    
    return data
