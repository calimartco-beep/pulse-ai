
def calculate_momentum(history):
    """
    Measures how much recent Google Trends interest
    has changed compared with the previous period.
    """

    if len(history) < 28:
        return 0

    values = [
        item["interest"]
        for item in history
    ]

    recent = values[-14:]
    previous = values[-28:-14]

    recent_average = sum(recent) / len(recent)
    previous_average = sum(previous) / len(previous)

    if previous_average == 0:
        return 0

    momentum = (
        (recent_average - previous_average)
        / previous_average
    ) * 100

    return round(momentum, 2)


def calculate_acceleration(history):
    """
    Measures whether the trend is speeding up
    or slowing down.
    """

    if len(history) < 42:
        return 0

    values = [
        item["interest"]
        for item in history
    ]

    older = values[-42:-28]
    previous = values[-28:-14]
    recent = values[-14:]

    older_average = sum(older) / len(older)
    previous_average = sum(previous) / len(previous)
    recent_average = sum(recent) / len(recent)

    if older_average == 0 or previous_average == 0:
        return 0

    first_growth = (
        (previous_average - older_average)
        / older_average
    ) * 100

    recent_growth = (
        (recent_average - previous_average)
        / previous_average
    ) * 100

    acceleration = recent_growth - first_growth

    return round(acceleration, 2)


def calculate_spike_strength(history):
    """
    Detects unusually large recent spikes compared
    with the historical baseline.
    """

    if len(history) < 14:
        return 0

    values = [
        item["interest"]
        for item in history
    ]

    recent = values[-14:]

    baseline = sum(values) / len(values)
    recent_peak = max(recent)

    if baseline == 0:
        return 0

    spike = (
        (recent_peak - baseline)
        / baseline
    ) * 100

    return round(max(0, spike), 2)


def calculate_trend_direction(history):
    """
    Measures the overall direction of the trend
    using the slope of recent observations.

    Positive = rising
    Negative = falling
    Near zero = flat
    """

    if len(history) < 14:
        return 0

    values = [
        item["interest"]
        for item in history[-14:]
    ]

    n = len(values)

    x_values = list(range(n))

    x_mean = sum(x_values) / n
    y_mean = sum(values) / n

    numerator = sum(
        (x - x_mean) * (y - y_mean)
        for x, y in zip(x_values, values)
    )

    denominator = sum(
        (x - x_mean) ** 2
        for x in x_values
    )

    if denominator == 0:
        return 0

    slope = numerator / denominator

    return round(slope, 2)


def calculate_consistency(history):
    """
    Measures how strongly recent data follows
    a consistent direction.
    """

    if len(history) < 14:
        return 0

    values = [
        item["interest"]
        for item in history[-14:]
    ]

    direction = calculate_trend_direction(history)

    average = sum(values) / len(values)

    if average == 0:
        return 0

    normalized_direction = (
        abs(direction) / average
    ) * 100

    consistency = min(
        100,
        normalized_direction * 10
    )

    return round(consistency, 2)


def calculate_acceleration_score(history):
    """
    Combines momentum, acceleration, spike strength,
    trend direction, and consistency into a 0-100
    acceleration score.
    """

    momentum = calculate_momentum(history)

    acceleration = calculate_acceleration(history)

    spike = calculate_spike_strength(history)

    direction = calculate_trend_direction(history)

    consistency = calculate_consistency(history)


    # Momentum component

    momentum_score = max(
        0,
        min(
            100,
            50 + momentum
        )
    )


    # Acceleration component

    acceleration_component = max(
        0,
        min(
            100,
            50 + acceleration * 2
        )
    )


    # Spike component

    spike_score = max(
        0,
        min(
            100,
            spike
        )
    )


    # Direction component

    if direction > 0:

        direction_score = min(
            100,
            50 + abs(direction) * 5
        )

    elif direction < 0:

        direction_score = max(
            0,
            50 - abs(direction) * 5
        )

    else:

        direction_score = 50


    # Final score

    final_score = (
        momentum_score * 0.30
        + acceleration_component * 0.25
        + spike_score * 0.15
        + direction_score * 0.20
        + consistency * 0.10
    )


    return {
        "momentum": momentum,
        "acceleration": acceleration,
        "spike_strength": spike,
        "trend_direction": direction,
        "consistency": consistency,
        "acceleration_score": round(
            max(
                0,
                min(
                    100,
                    final_score
                )
            )
        )
    }


def determine_trend_signal(history):
    """
    Converts numerical analysis into a
    human-readable Pulse AI signal.
    """

    analysis = calculate_acceleration_score(
        history
    )

    score = analysis["acceleration_score"]

    momentum = analysis["momentum"]

    acceleration = analysis["acceleration"]

    direction = analysis["trend_direction"]


    if (
        score >= 75
        and momentum > 0
        and acceleration > 0
        and direction > 0
    ):

        return "Breakout"


    if (
        score >= 60
        and momentum > 0
        and direction > 0
    ):

        return "Accelerating"


    if (
        score >= 45
        and direction > 0
    ):

        return "Emerging"


    if (
        analysis["spike_strength"] >= 50
        and momentum <= 0
    ):

        return "Spike / Volatile"


    if (
        momentum < 0
        and direction < 0
    ):

        return "Declining"


    return "Stable"


def generate_product_explanation(
    product,
    trend_analysis
):
    """
    Generates a human-readable explanation
    for why Pulse AI considers a product interesting.
    """

    tiktok = product["tiktok_growth"]

    google = product["google_growth"]

    competition = product["competition"]

    momentum = trend_analysis["momentum"]

    acceleration = trend_analysis["acceleration"]

    spike = trend_analysis["spike_strength"]

    direction = trend_analysis["trend_direction"]

    score = trend_analysis["acceleration_score"]


    reasons = []

    warnings = []


    # TikTok strength

    if tiktok >= 85:

        reasons.append(
            "TikTok growth is extremely strong"
        )

    elif tiktok >= 70:

        reasons.append(
            "TikTok growth is strong"
        )


    # Google strength

    if google >= 80:

        reasons.append(
            "Google search interest is very strong"
        )

    elif google >= 65:

        reasons.append(
            "Google search interest is healthy"
        )


    # Competition

    if competition <= 25:

        reasons.append(
            "competition is relatively low"
        )

    elif competition >= 60:

        warnings.append(
            "competition is relatively high"
        )


    # Momentum

    if momentum > 20:

        reasons.append(
            "recent search momentum is increasing"
        )

    elif momentum < -10:

        warnings.append(
            "recent search momentum is declining"
        )


    # Acceleration

    if acceleration > 20:

        reasons.append(
            "the trend is gaining momentum"
        )

    elif acceleration < -20:

        warnings.append(
            "trend acceleration is weakening"
        )


    # Direction

    if direction > 0.5:

        reasons.append(
            "recent trend direction is upward"
        )

    elif direction < -0.5:

        warnings.append(
            "recent trend direction is downward"
        )


    # Spike

    if spike >= 50:

        warnings.append(
            "recent activity shows significant volatility"
        )


    # Acceleration score

    if score >= 75:

        reasons.append(
            "the trend analysis shows strong opportunity potential"
        )

    elif score < 40:

        warnings.append(
            "the underlying trend signal is currently weak"
        )


    # Explanation

    if reasons:

        explanation = (
            "Pulse AI likes this product because "
            + ", ".join(reasons)
            + "."
        )

    else:

        explanation = (
            "Pulse AI currently sees limited positive "
            "signals for this product."
        )


    if warnings:

        explanation += (
            " However, "
            + ", ".join(warnings)
            + "."
        )


    return explanation
