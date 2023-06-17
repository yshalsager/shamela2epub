import logging

from gevent import sleep
from httpx import codes, get

logging.getLogger("httpx").setLevel(logging.WARNING)

TIME_OUT = 25
MAX_RETRIES = 5


def get_url_text(url: str) -> str:
    response = get(url, timeout=TIME_OUT)
    if response.status_code != codes.OK:
        # retry getting the page 5 times in case the server is down
        retries = 0
        while response.status_code != codes.OK and retries < MAX_RETRIES:
            sleep(5)
            response = get(url, timeout=TIME_OUT)
            retries += 1
    return response.text or ""
