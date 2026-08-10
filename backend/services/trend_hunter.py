def calculate_trend_score(
    tiktok_growth,
    whatnot_growth,
    google_growth,
    competition
):
    """
    Calculates the Pulse AI score.

    TikTok Live = 35%
    Whatnot = 30%
    Google = 20%
    Competition = 15%

    Higher growth/demand = better.
    Lower competition = better.
    """

    score = (
        tiktok_growth * 0.35
        +
        whatnot_growth * 0.30
        +
        google_growth * 0.20
        +
        (100 - competition) * 0.15
    )

    return round(score)


def determine_stage(score):

    if score >= 85:
        return "Viral Opportunity"

    elif score >= 70:
        return "Early Growth"

    elif score >= 50:
        return "Discovery"

    else:
        return "Low Momentum"