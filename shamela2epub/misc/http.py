from niquests import Session
from urllib3 import Retry

TIME_OUT = 30
MAX_RETRIES = 10

retry_strategy = Retry(
    total=MAX_RETRIES,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    backoff_factor=0.1,
)


def get_session(connections: int) -> Session:
    return Session(
        resolver="doh+cloudflare://",
        multiplexed=True,
        retries=retry_strategy,
        pool_maxsize=connections * 3,
    )
