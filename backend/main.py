from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models.schemas import ProductResponse

from backend.services.trend_hunter import (
    calculate_trend_score,
    determine_stage
)

from backend.services.trend_analyzer import (
    calculate_acceleration_score,
    determine_trend_signal
)

from backend.services.trend_sources import (
    get_google_trend_history
)

from backend.services.tiktok_signals import (
    add_tiktok_snapshot,
    get_tiktok_signal,
    list_tiktok_products
)

from backend.services.product_analyzer import (
    analyze_product
)

from backend.database.products import products


app = FastAPI()


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():
    return {
        "app": "Pulse AI",
        "status": "Running",
        "message": "Welcome to Pulse AI 🚀"
    }


# ==================================================
# TRENDS
# ==================================================

@app.get("/trends")
def get_trends():
    results = []

    for product in products:
        score = calculate_trend_score(
            tiktok_growth=product["tiktok_growth"],
            whatnot_growth=product["whatnot_growth"],
            google_growth=product["google_growth"],
            competition=product["competition"]
        )

        results.append(
            ProductResponse(
                name=product["name"],
                category=product["category"],
                trend_score=score,
                stage=determine_stage(score),
                tiktok_growth=product["tiktok_growth"],
                whatnot_growth=product["whatnot_growth"],
                google_growth=product["google_growth"],
                competition=product["competition"]
            )
        )

    results.sort(
        key=lambda item: item.trend_score,
        reverse=True
    )

    return results


# ==================================================
# PRODUCT ANALYZER
# ==================================================

@app.get("/analyze/{product_name}")
def analyze_product_route(
    product_name: str
):
    try:
        return analyze_product(
            product_name
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print(
            f"Unable to analyze product "
            f"{product_name}: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to analyze this product."
        )


# ==================================================
# TREND ANALYSIS
# ==================================================

@app.get("/trends/{product_name}/analysis")
def get_trend_analysis(product_name: str):
    try:
        trend_data = get_google_trend_history(
            product_name
        )

        history = trend_data["history"]
        data_status = trend_data["status"]

        if not history:
            return {
                "product": product_name,
                "error": "No Google Trends data available.",
                "google_trends_available": False,
                "data_status": data_status
            }

        analysis = calculate_acceleration_score(
            history
        )

        signal = determine_trend_signal(
            history
        )

        return {
            "product": product_name,
            "data_points": len(history),
            "signal": signal,
            "momentum": analysis["momentum"],
            "acceleration": analysis["acceleration"],
            "spike_strength": analysis["spike_strength"],
            "consistency": analysis["consistency"],
            "trend_direction": analysis["trend_direction"],
            "acceleration_score": analysis["acceleration_score"],
            "google_trends_available": True,
            "data_status": data_status
        }

    except Exception as error:
        print(
            f"Google Trends unavailable for "
            f"{product_name}: {error}"
        )

        return {
            "product": product_name,
            "error": "Google Trends data is temporarily unavailable.",
            "google_trends_available": False,
            "data_status": "Unavailable"
        }


# ==================================================
# TREND OPPORTUNITY
# ==================================================

@app.get("/trends/{product_name}/opportunity")
def get_trend_opportunity(product_name: str):
    product = next(
        (
            item
            for item in products
            if item["name"].lower() == product_name.lower()
        ),
        None
    )

    if not product:
        return {
            "product": product_name,
            "error": "Product not found."
        }

    score = calculate_trend_score(
        tiktok_growth=product["tiktok_growth"],
        whatnot_growth=product["whatnot_growth"],
        google_growth=product["google_growth"],
        competition=product["competition"]
    )

    reasons = []

    if product["tiktok_growth"] >= 80:
        reasons.append(
            "TikTok growth is very strong."
        )

    elif product["tiktok_growth"] >= 60:
        reasons.append(
            "TikTok growth is showing potential."
        )

    else:
        reasons.append(
            "TikTok growth is currently moderate."
        )

    if product["whatnot_growth"] >= 80:
        reasons.append(
            "Whatnot growth is very strong."
        )

    elif product["whatnot_growth"] >= 60:
        reasons.append(
            "Whatnot growth is showing potential."
        )

    else:
        reasons.append(
            "Whatnot growth is currently moderate."
        )

    if product["google_growth"] >= 80:
        reasons.append(
            "Google interest is very strong."
        )

    elif product["google_growth"] >= 60:
        reasons.append(
            "Google interest is showing potential."
        )

    else:
        reasons.append(
            "Google interest is currently moderate."
        )

    if product["competition"] <= 30:
        reasons.append(
            "Competition is relatively low."
        )

    elif product["competition"] <= 50:
        reasons.append(
            "Competition is moderate."
        )

    else:
        reasons.append(
            "Competition is relatively high."
        )

    if score >= 85:
        summary = (
            f"{product_name} has a Pulse Score of {score}/100 "
            "and is classified as Viral Opportunity. "
            "This product has very strong opportunity signals."
        )

    elif score >= 70:
        summary = (
            f"{product_name} has a Pulse Score of {score}/100 "
            "and is classified as Early Growth. "
            "This looks like a promising opportunity."
        )

    elif score >= 50:
        summary = (
            f"{product_name} has a Pulse Score of {score}/100 "
            "and is classified as Discovery. "
            "This product is showing early opportunity signals."
        )

    else:
        summary = (
            f"{product_name} has a Pulse Score of {score}/100 "
            "and is classified as Low Momentum. "
            "This product currently has weaker opportunity signals."
        )

    return {
        "product": product_name,
        "summary": summary,
        "reasons": reasons,
        "trend_signal": "Pending Google Trends analysis",
        "acceleration_score": None,
        "google_trends_available": False,
        "data_status": "Prototype"
    }


# ==================================================
# WHATNOT TREND DATA
# ==================================================

@app.get("/trends/{product_name}/whatnot")
def get_whatnot_trend(product_name: str):
    product = next(
        (
            item
            for item in products
            if item["name"].lower() == product_name.lower()
        ),
        None
    )

    if not product:
        return {
            "product": product_name,
            "error": "Product not found."
        }

    whatnot_growth = product["whatnot_growth"]

    whatnot_demand = round(
        whatnot_growth * 0.93
    )

    whatnot_competition = product["competition"]

    whatnot_score = round(
        (
            whatnot_growth * 0.45
            + whatnot_demand * 0.35
            + (100 - whatnot_competition) * 0.20
        )
    )

    if whatnot_growth >= 80:
        signal = "Strong Growth"

    elif whatnot_growth >= 60:
        signal = "Growing"

    elif whatnot_growth >= 40:
        signal = "Emerging"

    else:
        signal = "Weak"

    reasons = []

    if whatnot_growth >= 80:
        reasons.append(
            "Whatnot growth is very strong."
        )

    elif whatnot_growth >= 60:
        reasons.append(
            "Whatnot growth is strong."
        )

    else:
        reasons.append(
            "Whatnot growth is still developing."
        )

    if whatnot_demand >= 80:
        reasons.append(
            "Whatnot demand is very strong."
        )

    elif whatnot_demand >= 60:
        reasons.append(
            "Whatnot demand is showing potential."
        )

    else:
        reasons.append(
            "Whatnot demand is currently moderate."
        )

    if whatnot_competition <= 30:
        reasons.append(
            "Whatnot competition is relatively low."
        )

    elif whatnot_competition <= 50:
        reasons.append(
            "Whatnot competition is moderate."
        )

    else:
        reasons.append(
            "Whatnot competition is relatively high."
        )

    return {
        "product": product_name,
        "whatnot_growth": whatnot_growth,
        "whatnot_demand": whatnot_demand,
        "whatnot_competition": whatnot_competition,
        "whatnot_score": whatnot_score,
        "signal": signal,
        "reasons": reasons,
        "data_status": "Prototype data"
    }


# ==================================================
# AUTHORIZED TIKTOK SIGNALS
# ==================================================

@app.post("/tiktok/snapshots")
def create_tiktok_snapshot(
    product_name: str,
    views: int,
    videos: int,
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    source: str = "TikTok Creative Center"
):
    try:
        return add_tiktok_snapshot(
            product_name=product_name,
            views=views,
            videos=videos,
            likes=likes,
            comments=comments,
            shares=shares,
            source=source
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print(
            f"Unable to save TikTok snapshot: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to save TikTok snapshot."
        )


@app.get("/tiktok/signals")
def get_all_tiktok_signals():
    return list_tiktok_products()


@app.get("/tiktok/signals/{product_name}")
def get_product_tiktok_signal(
    product_name: str
):
    return get_tiktok_signal(product_name)