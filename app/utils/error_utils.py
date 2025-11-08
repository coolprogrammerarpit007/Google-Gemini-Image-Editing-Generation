
from models.error_log import ErrorLog
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from core.logger import logger

async def log_error(db: AsyncSession, source: str, error_type: str, message: str, prompt: str = None):
    """Logs error to database and local log file."""
    try:
        new_log = ErrorLog(
            source=source,
            error_type=error_type,
            message=message,
            prompt=prompt,
            created_at=datetime.utcnow()
        )
        db.add(new_log)
        await db.commit()
        logger.error(f"[{source}] {error_type}: {message}")
    except Exception as e:
        logger.error(f"Failed to log error: {e}")