import logging
import sys
from loguru import logger  # type: ignore

def setup_logging():
    """Configure standard library logging to route through Loguru, 
    ensuring clean, formatted logs across FastAPI, Uvicorn, and Celery.
    """
    # Remove default loguru handler
    logger.remove()

    # Add a clean, readable console handler with color support
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    # Intercept standard library logs (like uvicorn, fastapi, sqlalchemy)
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Redirect root loggers
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)

    for name in ["uvicorn", "uvicorn.access", "fastapi", "sqlalchemy.engine"]:
        std_logger = logging.getLogger(name)
        std_logger.handlers = [InterceptHandler()]
        std_logger.propagate = False