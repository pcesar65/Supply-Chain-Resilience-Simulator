# src/tune.py
import os
from dataclasses import asdict
from typing import List, Tuple, Dict, Any

import pandas as pd

from .sim import run_sim, LeadTime, Costs
from .policies import Policy
from .metrics import summarize


def tune_policy(
    days: int,
    demand_mean: float,
    demand_std: float,
    lead_time: LeadTime,
    start_inventory: int,
    costs: Costs,
    target_service_level: float,
    rop_values: List[int],
    q_values: List[int],
    seed: int = 7,
    allow_expedite: bool = False,
    expedite_threshold_days: int = 2,
) -> pd.DataFrame:
    """
    Grid search across ROP and Q.
    Returns a DataFrame of results for each policy combo.
    """
    results: List[Dict[str, Any]] = []

    for rop in rop_values:
        for q in q_values:
            policy = Policy(reorder_point=int(rop), order_qty=int(q))

            df = run_sim(
                days=days,
                demand_mean=demand_mean,
                demand_std=demand_std,
                lead_time=lead_time,
                start_inventory=start_inventory,
                policy=policy,
                costs=costs,
                seed=seed,
                allow_expedite=allow_expedite,
                expedite_threshold_days=expedite_threshold_days,
            )

            s = summarize(df)

            results.append({
                "rop": rop,
                "q": q,
                "service_level": s["service_level"],
                "stockout_days": s["stockout_days"],
                "avg_on_hand": s["avg_on_hand"],
                "max_on_hand": s["max_on_hand"],
                "holding_cost": s["holding_cost"],
                "stockout_cost": s["stockout_cost"],
                "expedite_cost": s["expedite_cost"],
                "total_cost": s["total_cost"],
                "meets_target": s["service_level"] >= target_service_level,
            })

    return pd.DataFrame(results)


def pick_best(df_results: pd.DataFrame) -> pd.DataFrame:
    """
    Choose best policy:
      1) Prefer those meeting target SL, lowest total_cost
      2) If none meet target, pick highest service_level, then lowest total_cost
    Returns a 1-row DataFrame of the chosen policy.
    """
    meets = df_results[df_results["meets_target"] == True].copy()
    if len(meets) > 0:
        best = meets.sort_values(["total_cost", "holding_cost"]).head(1)
        return best

    # fallback: maximize SL, then minimize cost
    best = df_results.sort_values(["service_level", "total_cost"], ascending=[False, True]).head(1)
    return best


def run_tuning_and_save(
    out_csv: str = "outputs/tuning_results.csv",
    best_csv: str = "outputs/best_policy.csv",
    **kwargs
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    df_results = tune_policy(**kwargs)
    df_results.to_csv(out_csv, index=False)

    best = pick_best(df_results)
    best.to_csv(best_csv, index=False)

    return df_results, best
