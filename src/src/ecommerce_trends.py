import pandas as pd

def load_data(file_or_path):
	df = pd.read_csv(file_or_path)
	df["date"] = pd.to_datetime(df["date"])
	df["week"] = df["date"].dt.to_period("W").astype(str)
	return df

def compute_weekly(df):
	weekly = (df.groupby(["product","week"], as_index=False)
		.agg(sales=("sales","sum"),
			 views=("views","sum"),
			 price=("price","median"),
			 category=("category","first")))
	weekly = weekly.sort_values(["product","week"])
	weekly["view_to_purchase"] = weekly.apply(
		lambda r: (r["views"]/r["sales"]) if r["sales"] > 0 else None, axis=1
	)
	weekly["sales_pct_change"] = weekly.groupby("product")["sales"].pct_change().fillna(0.0)
	weekly["trend_score"] = weekly["sales_pct_change"]
	return weekly

def find_trending(weekly):
	latest = weekly.sort_values("week").groupby("product").tail(1)
	top_rising = latest.sort_values("trend_score", ascending=False).head(10)
	top_falling = latest.sort_values("trend_score", ascending=True).head(10)
	return top_rising, top_falling