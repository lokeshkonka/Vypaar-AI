#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from app.config import settings
from app.core.logging_config import setup_logging
from app.scraper.agmarknet_scraper import AgmarknetScraper

def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape agricultural market data from Agmarknet"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to scrape backwards (default: 7)"
    )
    
    parser.add_argument(
        "--commodity",
        type=str,
        help="Specific commodity to scrape (optional)"
    )
    
    parser.add_argument(
        "--market",
        type=str,
        help="Specific market to scrape (optional)"
    )
    
    parser.add_argument(
        "--commodities-only",
        action="store_true",
        help="Scrape only commodities list"
    )
    
    parser.add_argument(
        "--markets-only",
        action="store_true",
        help="Scrape only markets list"
    )
    
    parser.add_argument(
        "--prices-only",
        action="store_true",
        help="Scrape only price data"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def main():

    args = parse_args()
    
    if args.verbose:
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")
    
    logger.info("=" * 60)
    logger.info("Agmarknet Data Scraper")
    logger.info("=" * 60)
    
    try:
        scraper = AgmarknetScraper()
        
        if args.commodities_only:
            logger.info("Scraping commodities only...")
            commodities = scraper.scrape_commodities()
            logger.success(f" Scraped {len(commodities)} commodities")
            
        elif args.markets_only:
            logger.info("Scraping markets only...")
            markets = scraper.scrape_markets()
            logger.success(f" Scraped {len(markets)} markets")
            
        elif args.prices_only:
            logger.info(f"Scraping prices only (last {args.days} days)...")
            prices = scraper.scrape_market_prices(
                commodity=args.commodity,
                market=args.market,
                days_back=args.days
            )
            logger.success(f" Scraped {len(prices)} price records")
            
        else:
            logger.info(f"Scraping all data (last {args.days} days)...")
            result = scraper.scrape_all(days_back=args.days)
            
            logger.success(" Scraping completed successfully!")
            logger.info(f"Duration: {result['duration_seconds']:.2f} seconds")
            logger.info(f"Commodities: {result['counts']['commodities']}")
            logger.info(f"Markets: {result['counts']['markets']}")
            logger.info(f"Price records: {result['counts']['prices']}")
        
        logger.info(f"Data saved to: {settings.data_raw_dir}")
        logger.info("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n  Scraping interrupted by user")
        return 130
        
    except Exception as e:
        logger.exception(f" Scraping failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
