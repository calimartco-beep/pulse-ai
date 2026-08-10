from backend.database.products import products

from backend.services.tiktok_signals import (
    get_tiktok_signal
)

from backend.services.trend_analyzer import (
    calculate_acceleration_score,
    determine_trend_signal
)

from backend.services.trend_sources import (
    get_google_trend_history
)


def find_prototype_product(product_name):
    return next(
        (
            product
            for product in products
            if product["name"].lower()
            == product_name.strip().lower()
        ),
        None
    )


def limit_score(value):
    return round(
        max(0, min(100, value))
    )


def determine_confidence(
    verified_source_count
):
    if verified_source_count >= 3:
        return "Strong"

    if verified_source_count == 2:
        return "Developing"

    if verified_source_count == 1:
        return "Low"

    return "Insufficient Data"


def determine_opportunity_stage(score):
    if score is None:
        return "Collecting Data"

    if score >= 80:
        return "Strong Opportunity"

    if score >= 60:
        return "Early Growth"

    if score >= 40:
        return "Discovery"

    return "Low Momentum"


def build_recommendation(
    score,
    confidence
):
    if score is None:
        return (
            "Pulse AI does not have enough verified data "
            "to score this product yet. Save additional "
            "authorized observations before making an "
            "inventory decision."
        )

    if confidence == "Low":
        return (
            f"The preliminary signal score is {score}/100, "
            "but it is based on only one verified source. "
            "Treat this as a research lead, not a buying "
            "decision."
        )

    if score >= 80:
        return (
            f"The verified signal score is {score}/100. "
            "This product is showing strong early opportunity "
            "signals across the available sources. Start with "
            "a small inventory test before scaling."
        )

    if score >= 60:
        return (
            f"The verified signal score is {score}/100. "
            "This product is showing promising early growth. "
            "Continue monitoring and consider a small test."
        )

    if score >= 40:
        return (
            f"The verified signal score is {score}/100. "
            "This product is in discovery. Collect more "
            "observations before purchasing inventory."
        )

    return (
        f"The verified signal score is {score}/100. "
        "Current momentum appears limited. Continue watching "
        "for acceleration before taking action."
    )


def analyze_google_signal(
    product_name
):
    trend_data = get_google_trend_history(
        product_name
    )

    history = trend_data.get(
        "history",
        []
    )

    data_status = trend_data.get(
        "status",
        "Unavailable"
    )

    if not history:
        return {
            "available": False,
            "score": None,
            "signal": "Unavailable",
            "data_points": 0,
            "momentum": None,
            "acceleration": None,
            "trend_direction": None,
            "data_status": data_status
        }

    analysis = calculate_acceleration_score(
        history
    )

    signal = determine_trend_signal(
        history
    )

    return {
        "available": True,
        "score": limit_score(
            analysis["acceleration_score"]
        ),
        "signal": signal,
        "data_points": len(history),
        "momentum": analysis["momentum"],
        "acceleration": analysis["acceleration"],
        "trend_direction": analysis["trend_direction"],
        "data_status": data_status
    }


def analyze_tiktok_signal(
    product_name
):
    signal = get_tiktok_signal(
        product_name
    )

    score = signal.get(
        "tiktok_score"
    )

    return {
        "available": (
            signal.get("available", False)
            and score is not None
        ),
        "score": score,
        "signal": signal.get(
            "signal",
            "Unavailable"
        ),
        "snapshot_count": signal.get(
            "snapshot_count",
            0
        ),
        "view_growth": signal.get(
            "view_growth"
        ),
        "video_growth": signal.get(
            "video_growth"
        ),
        "engagement_rate": signal.get(
            "engagement_rate"
        ),
        "acceleration": signal.get(
            "acceleration"
        ),
        "data_status": signal.get(
            "data_status",
            "Unavailable"
        ),
        "message": signal.get(
            "message"
        )
    }


def get_prototype_context(
    product_name
):
    product = find_prototype_product(
        product_name
    )

    if not product:
        return {
            "available": False,
            "data_status": "Unavailable"
        }

    return {
        "available": True,
        "category": product["category"],
        "tiktok_growth": product["tiktok_growth"],
        "whatnot_growth": product["whatnot_growth"],
        "google_growth": product["google_growth"],
        "competition": product["competition"],
        "data_status": (
            "Prototype only — excluded from verified score"
        )
    }


def calculate_verified_score(
    tiktok_signal,
    google_signal
):
    weighted_scores = []
    total_weight = 0

    if tiktok_signal["available"]:
        weighted_scores.append(
            tiktok_signal["score"] * 0.60
        )

        total_weight += 0.60

    if google_signal["available"]:
        weighted_scores.append(
            google_signal["score"] * 0.40
        )

        total_weight += 0.40

    if not weighted_scores or total_weight == 0:
        return None

    return limit_score(
        sum(weighted_scores)
        / total_weight
    )


def analyze_product(product_name):
    clean_name = product_name.strip()

    if not clean_name:
        raise ValueError(
            "Product name is required."
        )

    tiktok_signal = analyze_tiktok_signal(
        clean_name
    )

    google_signal = analyze_google_signal(
        clean_name
    )

    prototype_context = get_prototype_context(
        clean_name
    )

    verified_source_count = sum(
        [
            tiktok_signal["available"],
            google_signal["available"]
        ]
    )

    verified_score = calculate_verified_score(
        tiktok_signal,
        google_signal
    )

    confidence = determine_confidence(
        verified_source_count
    )

    missing_sources = []

    if not tiktok_signal["available"]:
        missing_sources.append(
            "TikTok needs at least two authorized snapshots."
        )

    if not google_signal["available"]:
        missing_sources.append(
            "Google Trends data is currently unavailable."
        )

    missing_sources.append(
        "Whatnot will remain unavailable until an official "
        "seller report is imported."
    )

    return {
        "product": clean_name,
        "verified_score": verified_score,
        "stage": determine_opportunity_stage(
            verified_score
        ),
        "confidence": confidence,
        "verified_source_count": verified_source_count,
        "required_verified_sources": 3,
        "recommendation": build_recommendation(
            verified_score,
            confidence
        ),
        "sources": {
            "tiktok": tiktok_signal,
            "google": google_signal,
            "whatnot": {
                "available": False,
                "score": None,
                "signal": "Waiting for seller report",
                "data_status": "Unavailable"
            }
        },
        "prototype_context": prototype_context,
        "missing_data": missing_sources,
        "safety": {
            "prototype_data_used_in_score": False,
            "invented_data_used": False,
            "authorized_sources_only": True
        }
    }