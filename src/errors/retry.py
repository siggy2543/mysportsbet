import time
from logger import log_info

# Implement a retry mechanism with exponential backoff for handling rate limits.

def retry_with_backoff(func, max_retries=5, backoff_in_seconds=1):
    retries = 0
    while retries < max_retries:
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                time.sleep(backoff_in_seconds)
                backoff_in_seconds *= 2
                retries += 1
            else:
                raise
        except Exception as e:
            raise
    log_info("Max retries reached.")
