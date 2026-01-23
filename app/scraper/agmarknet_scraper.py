"""Agmarknet web scraper for agricultural market data."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from bs4 import BeautifulSoup
from loguru import logger

from app.config import settings
from app.core.exceptions import ScraperError
from app.core.utils import ensure_dir, get_current_timestamp, save_json
from app.scraper.data_validator import DataValidator
from app.scraper.utils import (
    with_rate_limit,
    retry_on_failure,
    get_session,
    safe_get,
    clean_text,
    parse_float,
    parse_int,
    extract_table_data,
)


class AgmarknetScraper:
    """Scraper for Agmarknet agricultural market data."""

    def __init__(self):
        """Initialize the scraper."""
        self.base_url = settings.agmarknet_base_url
        self.session = get_session(timeout=settings.scrape_timeout)
        self.validator = DataValidator()
        self.raw_data_dir = Path(settings.data_raw_dir)
        self.processed_data_dir = Path(settings.data_processed_dir)
        
        # Ensure directories exist
        ensure_dir(self.raw_data_dir)
        ensure_dir(self.processed_data_dir)
        
        logger.info(f"AgmarknetScraper initialized - base_url: {self.base_url}")

    @with_rate_limit
    @retry_on_failure(max_attempts=settings.scrape_retry_attempts)
    def fetch_page(self, url: str) -> BeautifulSoup:
        """
        Fetch and parse a web page.
        
        Args:
            url: URL to fetch
            
        Returns:
            Parsed BeautifulSoup object
            
        Raises:
            ScraperError: If fetch fails
        """
        logger.debug(f"Fetching page: {url}")
        
        try:
            response = safe_get(url, session=self.session)
            soup = BeautifulSoup(response.content, "html.parser")
            return soup
        except Exception as e:
            logger.error(f"Failed to fetch page {url}: {str(e)}")
            raise ScraperError(f"Failed to fetch page: {url}", details={"error": str(e)})

    def scrape_commodities(self) -> list[dict[str, Any]]:
        """
        Scrape list of commodities from Agmarknet.
        
        Returns:
            List of commodity data dictionaries
        """
        logger.info("Scraping commodities...")
        
        # Mock data for demonstration (Agmarknet structure may vary)
        # In production, you would scrape actual commodity list
        commodities = [
            {"name": "Wheat", "category": "Cereals", "unit": "Quintal"},
            {"name": "Rice", "category": "Cereals", "unit": "Quintal"},
            {"name": "Maize", "category": "Cereals", "unit": "Quintal"},
            {"name": "Bajra", "category": "Cereals", "unit": "Quintal"},
            {"name": "Jowar", "category": "Cereals", "unit": "Quintal"},
            {"name": "Potato", "category": "Vegetables", "unit": "Quintal"},
            {"name": "Onion", "category": "Vegetables", "unit": "Quintal"},
            {"name": "Tomato", "category": "Vegetables", "unit": "Quintal"},
            {"name": "Brinjal", "category": "Vegetables", "unit": "Quintal"},
            {"name": "Cabbage", "category": "Vegetables", "unit": "Quintal"},
            {"name": "Cotton", "category": "Cash Crops", "unit": "Quintal"},
            {"name": "Sugarcane", "category": "Cash Crops", "unit": "Quintal"},
            {"name": "Groundnut", "category": "Oilseeds", "unit": "Quintal"},
            {"name": "Soybean", "category": "Oilseeds", "unit": "Quintal"},
            {"name": "Mustard", "category": "Oilseeds", "unit": "Quintal"},
        ]
        
        # Validate commodities
        valid_commodities, invalid = self.validator.validate_batch(
            commodities,
            self.validator.validate_commodity
        )
        
        logger.info(f"Scraped {len(valid_commodities)} commodities, {len(invalid)} invalid")
        
        # Save to file
        timestamp = get_current_timestamp().strftime("%Y%m%d_%H%M%S")
        output_file = self.raw_data_dir / f"commodities_{timestamp}.json"
        save_json({"commodities": valid_commodities, "scraped_at": timestamp}, output_file)
        
        return valid_commodities

    def scrape_markets(self) -> list[dict[str, Any]]:
        """
        Scrape list of markets from Agmarknet.
        
        Returns:
            List of market data dictionaries
        """
        logger.info("Scraping markets...")
        
        # Mock data for demonstration
        markets = [
            {"name": "Azadpur", "state": "Delhi", "district": "North Delhi"},
            {"name": "Anaj Mandi", "state": "Delhi", "district": "Central Delhi"},
            {"name": "Mumbai (Dadar)", "state": "Maharashtra", "district": "Mumbai"},
            {"name": "Pune", "state": "Maharashtra", "district": "Pune"},
            {"name": "Bangalore", "state": "Karnataka", "district": "Bangalore Urban"},
            {"name": "Chennai", "state": "Tamil Nadu", "district": "Chennai"},
            {"name": "Hyderabad", "state": "Telangana", "district": "Hyderabad"},
            {"name": "Kolkata", "state": "West Bengal", "district": "Kolkata"},
            {"name": "Jaipur", "state": "Rajasthan", "district": "Jaipur"},
            {"name": "Lucknow", "state": "Uttar Pradesh", "district": "Lucknow"},
        ]
        
        # Validate markets
        valid_markets, invalid = self.validator.validate_batch(
            markets,
            self.validator.validate_market
        )
        
        logger.info(f"Scraped {len(valid_markets)} markets, {len(invalid)} invalid")
        
        # Save to file
        timestamp = get_current_timestamp().strftime("%Y%m%d_%H%M%S")
        output_file = self.raw_data_dir / f"markets_{timestamp}.json"
        save_json({"markets": valid_markets, "scraped_at": timestamp}, output_file)
        
        return valid_markets

    def scrape_market_prices(
        self,
        commodity: Optional[str] = None,
        market: Optional[str] = None,
        date: Optional[str] = None,
        days_back: int = 7
    ) -> list[dict[str, Any]]:
        """
        Scrape market price data.
        
        Args:
            commodity: Specific commodity to scrape (None for all)
            market: Specific market to scrape (None for all)
            date: Specific date (YYYY-MM-DD) (None for recent)
            days_back: Number of days to scrape backwards
            
        Returns:
            List of market price data dictionaries
        """
        logger.info(f"Scraping market prices - commodity: {commodity}, market: {market}, date: {date}")
        
        # Generate sample data for demonstration
        # In production, this would scrape actual Agmarknet pages
        market_prices = self._generate_sample_market_data(
            commodity=commodity,
            market=market,
            date=date,
            days_back=days_back
        )
        
        # Validate data
        valid_prices, invalid = self.validator.validate_batch(
            market_prices,
            self.validator.validate_market_price
        )
        
        logger.info(f"Scraped {len(valid_prices)} price records, {len(invalid)} invalid")
        
        # Save to file
        timestamp = get_current_timestamp().strftime("%Y%m%d_%H%M%S")
        output_file = self.raw_data_dir / f"market_prices_{timestamp}.json"
        save_json({
            "prices": valid_prices,
            "invalid": invalid,
            "scraped_at": timestamp,
            "filters": {
                "commodity": commodity,
                "market": market,
                "date": date,
                "days_back": days_back
            }
        }, output_file)
        
        return valid_prices

    def _generate_sample_market_data(
        self,
        commodity: Optional[str] = None,
        market: Optional[str] = None,
        date: Optional[str] = None,
        days_back: int = 7
    ) -> list[dict[str, Any]]:
        """
        Generate sample market data for testing.
        
        This is a placeholder that generates realistic-looking data.
        In production, replace with actual scraping logic.
        """
        import random
        
        commodities = ["Wheat", "Rice", "Potato", "Onion", "Tomato"] if not commodity else [commodity]
        markets_list = [
            {"name": "Azadpur", "state": "Delhi"},
            {"name": "Mumbai (Dadar)", "state": "Maharashtra"},
            {"name": "Bangalore", "state": "Karnataka"},
            {"name": "Chennai", "state": "Tamil Nadu"},
        ] if not market else [{"name": market, "state": "Unknown"}]
        
        # Base prices for commodities (per quintal)
        base_prices = {
            "Wheat": 2500,
            "Rice": 3500,
            "Potato": 1200,
            "Onion": 2000,
            "Tomato": 1500,
        }
        
        data = []
        
        # Generate data for each day
        start_date = datetime.now() - timedelta(days=days_back)
        
        for day in range(days_back):
            current_date = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
            
            for comm in commodities:
                base_price = base_prices.get(comm, 2000)
                
                for mkt in markets_list:
                    # Add some random variation
                    variation = random.uniform(-0.15, 0.15)
                    modal_price = base_price * (1 + variation)
                    min_price = modal_price * 0.9
                    max_price = modal_price * 1.1
                    arrival = random.uniform(500, 5000)
                    
                    data.append({
                        "commodity": comm,
                        "market": mkt["name"],
                        "state": mkt["state"],
                        "date": current_date,
                        "min_price": round(min_price, 2),
                        "max_price": round(max_price, 2),
                        "modal_price": round(modal_price, 2),
                        "price": round(modal_price, 2),
                        "arrival": round(arrival, 2),
                    })
        
        return data

    def scrape_all(self, days_back: int = 7) -> dict[str, Any]:
        """
        Scrape all data (commodities, markets, prices).
        
        Args:
            days_back: Number of days to scrape price data
            
        Returns:
            Dictionary containing all scraped data
        """
        logger.info(f"Starting full scrape - days_back: {days_back}")
        
        start_time = get_current_timestamp()
        
        try:
            # Scrape commodities
            commodities = self.scrape_commodities()
            
            # Scrape markets
            markets = self.scrape_markets()
            
            # Scrape market prices
            prices = self.scrape_market_prices(days_back=days_back)
            
            end_time = get_current_timestamp()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "status": "success",
                "scraped_at": start_time.isoformat(),
                "duration_seconds": duration,
                "counts": {
                    "commodities": len(commodities),
                    "markets": len(markets),
                    "prices": len(prices),
                },
                "data": {
                    "commodities": commodities,
                    "markets": markets,
                    "prices": prices[:100],  # Include sample of prices
                }
            }
            
            # Save summary
            timestamp = start_time.strftime("%Y%m%d_%H%M%S")
            summary_file = self.raw_data_dir / f"scrape_summary_{timestamp}.json"
            save_json(result, summary_file)
            
            logger.info(f"Full scrape completed in {duration:.2f}s - "
                       f"{len(commodities)} commodities, {len(markets)} markets, {len(prices)} prices")
            
            return result
            
        except Exception as e:
            logger.exception(f"Full scrape failed: {str(e)}")
            raise ScraperError(f"Full scrape failed: {str(e)}")


# Convenience function
def create_scraper() -> AgmarknetScraper:
    """Create and return a scraper instance."""
    return AgmarknetScraper()
