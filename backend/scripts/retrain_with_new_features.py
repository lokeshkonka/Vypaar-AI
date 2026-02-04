import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from app.database.connection import init_sync_db
from app.ml.trainer import ModelTrainer
from app.core.utils import get_current_timestamp

async def main():
    logger.info("Starting model retraining with 29 features")
    
    db = init_sync_db()
    trainer = ModelTrainer(db)
    
    logger.info("Fetching historical data for training")
    success = await trainer.train_models(
        days_back=180,
        test_size=0.2,
        models_to_train=["random_forest", "gradient_boosting"]
    )
    
    if success:
        logger.success("Models retrained successfully with 29 features")
    else:
        logger.error("Model retraining failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
