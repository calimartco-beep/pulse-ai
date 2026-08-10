from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError

import json
import os
import time


CACHE_FILE = "backend/data/trends_cache.json"

# Reuse successful Google Trends results for six hours.
CACHE_DURATION_SECONDS = 6 * 60 * 60

# Stop contacting Google for one hour after a 429 response.
RATE_LIMIT_COOLDOWN_SECONDS = 60 * 60

RATE_LIMIT_CACHE_KEY = "__google_rate_limit__"


def ensure_cache_folder():
    folder = os.path.dirname(CACHE_FILE)

    if folder:
        os.makedirs(folder, exist_ok=True)


def load_cache():
    ensure_cache_folder()

    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r") as file:
            return json.load(file)

    except Exception:
        return {}


def save_cache(cache):
    ensure_cache_folder()

    try:
        with open(CACHE_FILE, "w") as file:
            json.dump(cache, file, indent=4)

    except Exception as error:
        print(f"Unable to save trend cache: {error}")


def cached_result(cached_entry):
    if cached_entry and isinstance(cached_entry, dict):
        cached_history = cached_entry.get("history", [])

        if cached_history:
            return {
                "history": cached_history,
                "status": "Cached"
            }

    return {
        "history": [],
        "status": "Unavailable"
    }


def google_is_in_cooldown(cache):
    rate_limit_entry = cache.get(RATE_LIMIT_CACHE_KEY, {})

    if not isinstance(rate_limit_entry, dict):
        return False

    blocked_timestamp = rate_limit_entry.get("timestamp", 0)
    blocked_age = time.time() - blocked_timestamp

    return blocked_age < RATE_LIMIT_COOLDOWN_SECONDS


def start_google_cooldown(cache):
    cache[RATE_LIMIT_CACHE_KEY] = {
        "timestamp": time.time()
    }

    save_cache(cache)


def clear_google_cooldown(cache):
    if RATE_LIMIT_CACHE_KEY in cache:
        del cache[RATE_LIMIT_CACHE_KEY]


def get_google_trend_history(product_name):
    """
    Return Google Trends history.

    Status values:
        Live        = freshly retrieved from Google
        Cached      = previously retrieved data
        Unavailable = no data available
    """

    cache = load_cache()
    cached_entry = cache.get(product_name)

    # Use recent saved product data first.
    if cached_entry and isinstance(cached_entry, dict):
        cached_history = cached_entry.get("history", [])
        cached_timestamp = cached_entry.get("timestamp", 0)
        cache_age = time.time() - cached_timestamp

        if cached_history and cache_age < CACHE_DURATION_SECONDS:
            print(
                f"Using recent cached Google Trends data "
                f"for {product_name}."
            )

            return {
                "history": cached_history,
                "status": "Cached"
            }

    # Skip Google while the one-hour cooldown is active.
    if google_is_in_cooldown(cache):
        print(
            f"Skipping Google Trends request for {product_name} "
            f"because Google is temporarily rate limiting Pulse AI."
        )

        return cached_result(cached_entry)

    try:
        print(f"Requesting Google Trends data for: {product_name}")

        pytrends = TrendReq(
            hl="en-US",
            tz=360,
            timeout=(5, 10)
        )

        pytrends.build_payload(
            [product_name],
            cat=0,
            timeframe="today 3-m",
            geo="US",
            gprop=""
        )

        data = pytrends.interest_over_time()

        if data.empty:
            print(f"No Google Trends data found for {product_name}.")
            return cached_result(cached_entry)

        history = []

        for index, row in data.iterrows():
            history.append(
                {
                    "date": index.strftime("%Y-%m-%d"),
                    "interest": int(row[product_name])
                }
            )

        clear_google_cooldown(cache)

        cache[product_name] = {
            "timestamp": time.time(),
            "history": history
        }

        save_cache(cache)

        print(f"Fresh Google Trends data saved for {product_name}.")

        return {
            "history": history,
            "status": "Live"
        }

    except TooManyRequestsError:
        print(
            f"Google Trends rate limit reached for {product_name}. "
            f"Starting a one-hour cooldown."
        )

        start_google_cooldown(cache)

        return cached_result(cached_entry)

    except Exception as error:
        print(f"Google Trends error for {product_name}: {error}")

        return cached_result(cached_entry)