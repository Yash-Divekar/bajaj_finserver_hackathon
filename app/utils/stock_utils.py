import pandas as pd
import os
import pickle

CACHE_FILE = "app/cache/stock_cache.pkl"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "rb") as f:
        stock_cache = pickle.load(f)
else:
    stock_cache = {}

def save_cache():
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(stock_cache, f)

def load_stock_data(path):
    df = pd.read_csv(path)
    # Correct format: day-abbr_month-2digit_year
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y")
    df["Month-Year"] = df["Date"].dt.strftime("%b-%y")
    return df

def get_stat(df, month_year, mode="avg"):
    cache_key = f"{mode}-{month_year}"
    if cache_key in stock_cache:
        return stock_cache[cache_key]

    df_filtered = df[df["Month-Year"] == month_year]
    if df_filtered.empty:
        return "No data"

    if mode == "avg":
        val = round(df_filtered["Close Price"].mean(), 2)
    elif mode == "high":
        val = round(df_filtered["Close Price"].max(), 2)
    elif mode == "low":
        val = round(df_filtered["Close Price"].min(), 2)
    else:
        return "Invalid mode"

    stock_cache[cache_key] = val
    save_cache()
    return val

def compare_months(df, m1, m2):
    # Filter and label the data
    df1 = df[df["Month-Year"] == m1][["Date", "Close Price"]].copy()
    df2 = df[df["Month-Year"] == m2][["Date", "Close Price"]].copy()

    df1["Day"] = df1["Date"].dt.day
    df2["Day"] = df2["Date"].dt.day

    df1.rename(columns={"Close Price": m1}, inplace=True)
    df2.rename(columns={"Close Price": m2}, inplace=True)

    # Merge on day of the month
    merged = pd.merge(df1[["Day", m1]], df2[["Day", m2]], on="Day", how="outer").sort_values("Day")
    
    # Calculate difference and better
    merged["Difference"] = (merged[m1] - merged[m2]).round(2)
    merged["Better"] = merged["Difference"].apply(
        lambda x: m1 if x > 0 else (m2 if x < 0 else "Equal")
    )

    # Calculate and append averages
    avg_row = {
        "Day": "Average",
        m1: round(merged[m1].mean(), 2),
        m2: round(merged[m2].mean(), 2),
        "Difference": round((merged[m1].mean() - merged[m2].mean()), 2),
        "Better": m1 if merged[m1].mean() > merged[m2].mean() else (m2 if merged[m1].mean() < merged[m2].mean() else "Equal"),
    }

    merged = pd.concat([merged, pd.DataFrame([avg_row])], ignore_index=True)
    return merged