# modules/utils.py

import logging
import time

def retry_with_exponential_backoff(func, max_retries=5, base_delay=1):
    """
    Retries a function with exponential backoff.

    Args:
        func (callable): Function to retry.
        max_retries (int, optional): Maximum number of retries. Defaults to 5.
        base_delay (int, optional): Base delay in seconds. Defaults to 1.

    Returns:
        any: Result of the function, or None if retries fail.
    """
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                delay = base_delay * (2 ** (retries - 1))  # Exponential backoff
                logging.warning(f"Retry {retries} for {func.__name__} in {delay} seconds. Error: {e}")
                #time.sleep(delay)
        logging.error(f"Max retries reached for {func.__name__}. Failed.")
        return None  # Or raise an exception, depending on your needs
    return wrapper

