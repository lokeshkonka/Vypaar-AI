"""Initialize sample discussions."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.database.connection import get_async_session, init_async_db
from app.database.repositories import DiscussionRepository
from datetime import datetime, timezone


async def main():
    """Initialize sample discussions."""
    print("Initializing discussions...")
    
    # Initialize database
    await init_async_db()
    
    # Get session
    async for session in get_async_session():
        repo = DiscussionRepository(session)
        
        # Check if discussions exist
        existing = await repo.get_recent(limit=1)
        if existing:
            print("Discussions already exist, skipping...")
            return
        
        # Create sample discussions
        sample_discussions = [
            {
                "title": "Best time to sell Tomatoes in Delhi?",
                "content": "I have a good harvest of tomatoes this season. When is the best time to sell them for maximum profit? Any insights on Delhi market trends?",
                "commodity": "Tomato",
                "author": "Ramesh Kumar",
                "tags": ["selling", "timing", "delhi"],
            },
            {
                "title": "Potato prices trending up - good news for farmers!",
                "content": "Noticed potato prices have been steadily increasing over the past 2 weeks. Great time for farmers who stored their harvest.",
                "commodity": "Potato",
                "author": "Sunita Devi",
                "tags": ["prices", "trending", "potato"],
            },
            {
                "title": "Weather impact on Wheat yield this season",
                "content": "The recent rains might affect wheat quality. What precautions are you all taking?",
                "commodity": "Wheat",
                "author": "Vijay Singh",
                "tags": ["weather", "wheat", "farming"],
            },
            {
                "title": "Onion export ban - how will it affect local prices?",
                "content": "With the recent export restrictions, what do you think will happen to onion prices in local markets?",
                "commodity": "Onion",
                "author": "Priya Sharma",
                "tags": ["policy", "onion", "exports"],
            },
        ]
        
        for disc_data in sample_discussions:
            discussion = await repo.create(
                title=disc_data["title"],
                content=disc_data["content"],
                commodity=disc_data["commodity"],
                author=disc_data["author"],
                avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={disc_data['author']}",
                tags=disc_data["tags"],
                status="PUBLISHED",
                likes_count=0,
                replies_count=0,
                views_count=0,
                is_pinned=False,
            )
            print(f"Created discussion: {discussion.title}")
        
        print(f"✅ Created {len(sample_discussions)} sample discussions")


if __name__ == "__main__":
    asyncio.run(main())
