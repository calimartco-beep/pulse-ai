
from backend.services.trend_sources import get_google_trend_history
from backend.services.trend_analyzer import calculate_acceleration_score


history = get_google_trend_history("Squishy Toys")


print("\nGOOGLE TRENDS HISTORY")
print("---------------------")
print(f"Data points: {len(history)}")


result = calculate_acceleration_score(history)


print("\nTREND ANALYSIS")
print("--------------")
print(f"Momentum: {result['momentum']}%")
print(f"Acceleration: {result['acceleration']}%")
print(f"Spike strength: {result['spike_strength']}%")
print(f"Consistency: {result['consistency']}%")
print(f"Trend direction: {result['trend_direction']}")
print(f"Acceleration Score: {result['acceleration_score']}/100")
