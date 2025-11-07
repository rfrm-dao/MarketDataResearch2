import requests
import pandas as pd
import matplotlib.pyplot as plt

# Config
COIN = "bitcoin"
DAYS = 30
VS_CURRENCY = "usd"

# Helper Functions
def fetch_market_chart(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": VS_CURRENCY, "days": DAYS, "interval": "daily"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

def fetch_summary_data(coin_id):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": VS_CURRENCY,
        "ids": coin_id,
        "price_change_percentage": "24h,7d,30d"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()[0]

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Main
plt.style.use("dark_background")
df = fetch_market_chart(COIN)
info = fetch_summary_data(COIN)

df["MA_50"] = df["price"].rolling(50).mean()
df["MA_200"] = df["price"].rolling(30).mean()
df["RSI_14"] = calculate_rsi(df["price"])

# Plot
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

axs[0].plot(df.index, df["price"], label="Price", color="cyan")
axs[0].plot(df.index, df["MA_50"], label="MA 50", color="yellow", linestyle='--')
axs[0].plot(df.index, df["MA_200"], label="MA 200", color="orange", linestyle='--')
axs[0].set_title("BTC Price + MA")
axs[0].legend()
axs[0].grid(True, alpha=0.3)

axs[1].plot(df.index, df["RSI_14"], label="RSI (14)", color="lime")
axs[1].axhline(70, color='red', linestyle='--', alpha=0.7)
axs[1].axhline(30, color='blue', linestyle='--', alpha=0.7)
axs[1].set_title("BTC RSI (14)")
axs[1].legend()
axs[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print summary
print(f"\n🔹 BITCOIN Summary")
print(f"Current Price: ${info['current_price']:,}")
print(f"24h Change: {info['price_change_percentage_24h_in_currency']:.2f}%")
print(f"7d Change: {info['price_change_percentage_7d_in_currency']:.2f}%")
print(f"30d Change: {info['price_change_percentage_30d_in_currency']:.2f}%")
print(f"24h Volume: ${info['total_volume']:,}")
print(f"Market Cap: ${info['market_cap']:,}")

# Save
df.reset_index().to_csv("BTC_priceindicators.csv", index=False)
print("✅ Saved BTC_priceindicators.csv")
