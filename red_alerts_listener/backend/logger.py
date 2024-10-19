import logging
import sys
import os
import codecs

from DEFINITIONS import ROOT_DIR

def setup_logger(name: str, log_filename: str = 'message.log') -> logging.Logger:
    # Create logger with the given name
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a file handler for logging to a file
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')  # Ensure UTF-8 encoding

    # Create a stream handler for logging to stdout with UTF-8 encoding
    # Wrap sys.stdout with a UTF-8 writer if needed (for Windows compatibility)
    stream_handler = logging.StreamHandler(codecs.getwriter('utf-8')(sys.stdout.buffer))

    # Create a logging format including the filename
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set the same formatter for both handlers
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

# Initialize the logger
logger = setup_logger('main_logger', os.path.join(ROOT_DIR, 'messages.log'))
