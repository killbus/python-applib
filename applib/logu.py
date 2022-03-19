"""Create custom logger."""
from sys import stdout
from loguru import logger as loguru_logger


def create_logger():
    """Create custom logger."""
    loguru_logger.remove()
    loguru_logger.add(
        stdout,
        colorize=True,
        level="INFO",
        catch=True,
        format="<green>{time:MM-DD-YYYY HH:mm:ss}</green>"
               + "<light-red> | </light-red>"
               + "<level>{level: <8}</level> | "
               + "<cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    return loguru_logger


logger = create_logger()
info, debug, warn, error = logger.info , logger.debug, logger.warning, logger.error