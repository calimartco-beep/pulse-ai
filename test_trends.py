from pytrends.request import TrendReq

pytrends = TrendReq(
    hl="en-US",
    tz=360
)

keyword = "Squishy Toys"

pytrends.build_payload(
    [keyword],
    timeframe="today 3-m",
    geo="US"
)

data = pytrends.interest_over_time()

print(data)

if data.empty:
    print("\nNO DATA RETURNED")
else:
    print("\nNUMBER OF DATA POINTS:", len(data))
    print("VALUES:")
    print(data[keyword].tolist())