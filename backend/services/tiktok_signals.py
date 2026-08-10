import json
import os
from datetime import datetime, timezone


TIKTOK_DATA_FILE = "backend/data/tiktok_snapshots.json"

MAX_SNAPSHOTS_PER_PRODUCT = 90


def ensure_data_folder():
    folder = os.path.dirname(TIKTOK_DATA_FILE)

    if folder:
        os.makedirs(folder, exist_ok=True)


def load_tiktok_snapshots():
    ensure_data_folder()

    if not os.path.exists(TIKTOK_DATA_FILE):
        return {}

    try:
        with open(TIKTOK_DATA_FILE, "r") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except Exception as error:
        print(f"Unable to load TikTok snapshots: {error}")
        return {}


def save_tiktok_snapshots(data):
    ensure_data_folder()

    temporary_file = f"{TIKTOK_DATA_FILE}.tmp"

    try:
        with open(temporary_file, "w") as file:
            json.dump(data, file, indent=4)

        os.replace(temporary_file, TIKTOK_DATA_FILE)

    except Exception as error:
        print(f"Unable to save TikTok snapshots: {error}")

        if os.path.exists(temporary_file):
            os.remove(temporary_file)

        raise


def normalize_product_name(product_name):
    return product_name.strip().lower()


def validate_number(value, field_name):
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number.")

    try:
        number = int(value)

    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a whole number.")

    if number < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    return number


def calculate_percentage_growth(previous_value, current_value):
    if previous_value <= 0:
        if current_value > 0:
            return 100.0

        return 0.0

    growth = (
        (current_value - previous_value)
        / previous_value
    ) * 100

    return round(growth, 2)


def calculate_engagement_rate(snapshot):
    views = snapshot.get("views", 0)

    if views <= 0:
        return 0.0

    engagements = (
        snapshot.get("likes", 0)
        + snapshot.get("comments", 0)
        + snapshot.get("shares", 0)
    )

    return round(
        (engagements / views) * 100,
        2
    )


def limit_score(value):
    return round(
        max(0, min(100, value))
    )


def determine_tiktok_signal(score):
    if score is None:
        return "Collecting Data"

    if score >= 80:
        return "Strong Growth"

    if score >= 60:
        return "Growing"

    if score >= 40:
        return "Emerging"

    return "Weak"


def add_tiktok_snapshot(
    product_name,
    views,
    videos,
    likes=0,
    comments=0,
    shares=0,
    source="TikTok Creative Center"
):
    clean_name = product_name.strip()

    if not clean_name:
        raise ValueError("Product name is required.")

    snapshot = {
        "observed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "views": validate_number(
            views,
            "Views"
        ),
        "videos": validate_number(
            videos,
            "Videos"
        ),
        "likes": validate_number(
            likes,
            "Likes"
        ),
        "comments": validate_number(
            comments,
            "Comments"
        ),
        "shares": validate_number(
            shares,
            "Shares"
        ),
        "source": source.strip()
        if source
        else "Manual authorized entry"
    }

    data = load_tiktok_snapshots()
    product_key = normalize_product_name(clean_name)

    product_entry = data.get(
        product_key,
        {
            "product_name": clean_name,
            "snapshots": []
        }
    )

    snapshots = product_entry.get(
        "snapshots",
        []
    )

    snapshots.append(snapshot)

    product_entry["product_name"] = clean_name
    product_entry["snapshots"] = snapshots[
        -MAX_SNAPSHOTS_PER_PRODUCT:
    ]

    data[product_key] = product_entry

    save_tiktok_snapshots(data)

    return {
        "product": clean_name,
        "snapshot": snapshot,
        "snapshot_count": len(
            product_entry["snapshots"]
        ),
        "data_status": "User-authorized data"
    }


def get_tiktok_signal(product_name):
    data = load_tiktok_snapshots()
    product_key = normalize_product_name(
        product_name
    )

    product_entry = data.get(product_key)

    if not product_entry:
        return {
            "product": product_name,
            "available": False,
            "snapshot_count": 0,
            "signal": "No Data",
            "tiktok_score": None,
            "message": (
                "No TikTok observations have been "
                "saved for this product yet."
            ),
            "data_status": "Unavailable"
        }

    snapshots = product_entry.get(
        "snapshots",
        []
    )

    if not snapshots:
        return {
            "product": product_name,
            "available": False,
            "snapshot_count": 0,
            "signal": "No Data",
            "tiktok_score": None,
            "message": (
                "No TikTok observations have been "
                "saved for this product yet."
            ),
            "data_status": "Unavailable"
        }

    latest = snapshots[-1]
    engagement_rate = calculate_engagement_rate(
        latest
    )

    if len(snapshots) < 2:
        return {
            "product": product_entry["product_name"],
            "available": True,
            "snapshot_count": 1,
            "latest_snapshot": latest,
            "engagement_rate": engagement_rate,
            "view_growth": None,
            "video_growth": None,
            "acceleration": None,
            "tiktok_score": None,
            "signal": "Collecting Data",
            "message": (
                "One snapshot is saved. Add another "
                "observation later to calculate growth."
            ),
            "data_status": "User-authorized data"
        }

    previous = snapshots[-2]

    view_growth = calculate_percentage_growth(
        previous.get("views", 0),
        latest.get("views", 0)
    )

    video_growth = calculate_percentage_growth(
        previous.get("videos", 0),
        latest.get("videos", 0)
    )

    acceleration = None

    if len(snapshots) >= 3:
        older = snapshots[-3]

        earlier_view_growth = (
            calculate_percentage_growth(
                older.get("views", 0),
                previous.get("views", 0)
            )
        )

        acceleration = round(
            view_growth - earlier_view_growth,
            2
        )

    view_growth_score = limit_score(
        view_growth * 2
    )

    video_growth_score = limit_score(
        video_growth * 2
    )

    engagement_score = limit_score(
        engagement_rate * 10
    )

    if acceleration is None:
        acceleration_score = 0

    else:
        acceleration_score = limit_score(
            acceleration * 2
        )

    tiktok_score = round(
        view_growth_score * 0.45
        + video_growth_score * 0.25
        + engagement_score * 0.20
        + acceleration_score * 0.10
    )

    return {
        "product": product_entry["product_name"],
        "available": True,
        "snapshot_count": len(snapshots),
        "latest_snapshot": latest,
        "previous_snapshot": previous,
        "engagement_rate": engagement_rate,
        "view_growth": view_growth,
        "video_growth": video_growth,
        "acceleration": acceleration,
        "tiktok_score": tiktok_score,
        "signal": determine_tiktok_signal(
            tiktok_score
        ),
        "data_status": "User-authorized data"
    }


def list_tiktok_products():
    data = load_tiktok_snapshots()

    results = []

    for product_entry in data.values():
        product_name = product_entry.get(
            "product_name",
            ""
        )

        if product_name:
            results.append(
                get_tiktok_signal(product_name)
            )

    results.sort(
        key=lambda item: (
            item.get("tiktok_score") is not None,
            item.get("tiktok_score") or 0
        ),
        reverse=True
    )

    return results