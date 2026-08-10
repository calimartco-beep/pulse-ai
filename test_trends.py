import sys

from backend.services.trend_sources import get_google_trend_history


def main():
    keyword = " ".join(sys.argv[1:]).strip() or "Squishy Toys"

    print(f"\nTesting Pulse AI Google Trends service for: {keyword}")

    trend_data = get_google_trend_history(keyword)
    history = trend_data.get("history", [])
    status = trend_data.get("status", "Unavailable")

    print(f"\nDATA STATUS: {status}")
    print(f"NUMBER OF DATA POINTS: {len(history)}")

    if not history:
        print(
            "\nNo Google Trends history is currently available. "
            "Pulse AI may be observing its rate-limit cooldown."
        )
        return

    print("\nMOST RECENT 10 DATA POINTS:")

    for data_point in history[-10:]:
        print(
            f"{data_point['date']}: "
            f"{data_point['interest']}"
        )


if __name__ == "__main__":
    main()