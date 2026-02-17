import pandas as pd

def summarize(df: pd.DataFrame) -> dict:
    total_demand = df["demand"].sum()
    total_shipped = df["shipped"].sum()
    total_lost = df["lost_sales"].sum()

    service_level = (total_shipped / total_demand) if total_demand > 0 else 1.0
    stockout_days = int((df["on_hand_end"] == 0).sum())

    holding_cost = float(df["holding_cost"].sum())
    stockout_cost = float(df["stockout_cost"].sum())
    expedite_cost = float(df["expedite_cost"].sum())

    return {
        "days": int(df["day"].max()),
        "total_demand": int(total_demand),
        "total_shipped": int(total_shipped),
        "total_lost": int(total_lost),
        "service_level": float(service_level),
        "stockout_days": stockout_days,
        "avg_on_hand": float(df["on_hand_end"].mean()),
        "max_on_hand": int(df["on_hand_end"].max()),
        "holding_cost": holding_cost,
        "stockout_cost": stockout_cost,
        "expedite_cost": expedite_cost,
        "total_cost": holding_cost + stockout_cost + expedite_cost,
    }

def recommendation(summary: dict, target_service_level: float) -> str:
    sl = summary["service_level"]
    if sl >= target_service_level:
        return "Meets target SL. Consider lowering ROP to reduce holding cost (test carefully)."
    gap = target_service_level - sl
    if gap < 0.03:
        return "Small SL gap. Increase ROP modestly or reduce lead time variability."
    return "Material SL gap. Increase safety stock (ROP) and/or add expedite strategy."
