
def explain_opportunity(
    product,
    trend_score,
    stage,
    tiktok_growth,
    google_growth,
    competition,
    trend_analysis
):
    """
    Creates a simple explanation for why
    Pulse AI considers a product an opportunity.
    """

    reasons = []

    momentum = trend_analysis.get(
        "momentum",
        0
    )

    acceleration = trend_analysis.get(
        "acceleration",
        0
    )

    signal = trend_analysis.get(
        "signal",
        "Stable"
    )

    acceleration_score = trend_analysis.get(
        "acceleration_score",
        0
    )


    # --------------------------------------------------
    # TREND GROWTH
    # --------------------------------------------------

    if momentum > 20:

        reasons.append(
            "Google search interest is rising strongly."
        )

    elif momentum > 0:

        reasons.append(
            "Google search interest is starting to rise."
        )

    elif momentum < -20:

        reasons.append(
            "Google search interest has recently declined."
        )


    # --------------------------------------------------
    # ACCELERATION
    # --------------------------------------------------

    if acceleration > 20:

        reasons.append(
            "The trend is accelerating."
        )

    elif acceleration > 0:

        reasons.append(
            "The trend is showing positive acceleration."
        )

    elif acceleration < -20:

        reasons.append(
            "The trend is losing momentum."
        )


    # --------------------------------------------------
    # TIKTOK
    # --------------------------------------------------

    if tiktok_growth >= 80:

        reasons.append(
            "TikTok activity is very strong."
        )

    elif tiktok_growth >= 60:

        reasons.append(
            "TikTok activity is showing healthy interest."
        )


    # --------------------------------------------------
    # GOOGLE
    # --------------------------------------------------

    if google_growth >= 80:

        reasons.append(
            "Google interest is strong."
        )

    elif google_growth >= 60:

        reasons.append(
            "Google interest is showing potential."
        )


    # --------------------------------------------------
    # COMPETITION
    # --------------------------------------------------

    if competition <= 30:

        reasons.append(
            "Competition is relatively low."
        )

    elif competition <= 50:

        reasons.append(
            "Competition is still manageable."
        )

    elif competition >= 70:

        reasons.append(
            "Competition is relatively high."
        )


    # --------------------------------------------------
    # SIGNAL
    # --------------------------------------------------

    if signal == "Breakout":

        reasons.append(
            "Pulse AI is detecting a potential breakout."
        )

    elif signal == "Accelerating":

        reasons.append(
            "Pulse AI is detecting accelerating demand."
        )

    elif signal == "Emerging":

        reasons.append(
            "The product appears to be an emerging opportunity."
        )

    elif signal == "Spike / Volatile":

        reasons.append(
            "The product is experiencing unusual but volatile activity."
        )

    elif signal == "Declining":

        reasons.append(
            "The trend is currently declining."
        )


    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------

    if not reasons:

        reasons.append(
            "Pulse AI is monitoring this product for potential opportunity."
        )


    # --------------------------------------------------
    # CREATE SUMMARY
    # --------------------------------------------------

    summary = (
        f"{product} currently has a Pulse Score of "
        f"{trend_score}/100 and is classified as "
        f"{stage}. "
        + " ".join(reasons[:5])
    )


    return {
        "product": product,
        "summary": summary,
        "reasons": reasons,
        "trend_signal": signal,
        "acceleration_score": acceleration_score
    }
