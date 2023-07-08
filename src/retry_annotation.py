import time
from functools import wraps

from logger import logger


def retry(exception_to_check, tries=5, initial_delay=2, backoff=2, failure_handler=None):
    """A Retry decorator with an exponential backoff.
    Heavily inspired by https://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    If all retries fail the exception will be raised.
    If failure_handler is given it will be called with the exception as argument instead
    of raising the exception.
    """

    def decorator_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            m_tries, m_delay = tries, initial_delay

            while m_tries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
                    logger.warning(f"{e}, Retrying in {m_delay} seconds... ({m_tries - 1} tries left)")
                    time.sleep(m_delay)
                    m_tries -= 1
                    m_delay *= backoff  # calculate delay for next try

            try:
                return f(*args, **kwargs)  # last try
            except exception_to_check as e:
                if failure_handler is not None:
                    failure_handler(e)
                else:
                    raise e

        return f_retry  # true decorator -> decorated function

    return decorator_retry  # decorator -> decorated function
