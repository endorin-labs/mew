import logging
import time
from functools import wraps
from colorama import Fore, Style, init

# initialize colorama
init()


class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored logs"""

    COLORS = {
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
        "DEBUG": Fore.BLUE,
    }

    def format(self, record):
        # add colors based on log level
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


def setup_logging(name: str) -> logging.Logger:
    """Set up a logger with colored output"""
    log = logging.getLogger(name)

    if log.hasHandlers():
        return log

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = ColoredFormatter(
        fmt="%(levelname)s %(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    log.addHandler(console_handler)
    log.setLevel(logging.INFO)

    return log


def log_grpc_call(logger: logging.Logger):
    """Decorator to log gRPC method calls with timing"""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, stream, *args, **kwargs):
            method_name = func.__name__
            start_time = time.time()

            logger.info(f"gRPC call started: {method_name}")

            try:
                result = await func(self, stream, *args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"gRPC call completed: {method_name} - Duration: {duration:.2f}s"
                )
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"gRPC call failed: {method_name} - Error: {str(e)} - "
                    f"Duration: {duration:.2f}s"
                )
                raise

        return wrapper

    return decorator


# create a global logger
logger = setup_logging(__name__)
