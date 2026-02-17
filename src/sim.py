from dataclasses import dataclass
from typing import List, Dict
import numpy as np
import pandas as pd
from .policies import Policy, should_reorder

@dataclass
class Costs:
    holding_per_unit_per_day: float
    stockout_per_unit: float
    expedite_fixed: float = 0.0  # optional fixed expedite fee

@dataclass
class LeadTime:
    mean_days: float
    std_days: float
    min_days: int = 1

def sample_lead_time(rng: np.random.Generator, lt: LeadTime) -> int:
    x = int(round(rng.normal(lt.mean_days, lt.std_days)))
    return max(lt.min_days, x)

def sample_demand(rng: np.random.Generator, mean: float, std: float) -> int:
    d = int(round(rng.normal(mean, std)))
    return max(0, d)

def run_sim(
    days: int,
    demand_mean: float,
    demand_std: float,
    lead_time: LeadTime,
    start_inventory: int,
    policy: Policy,
    costs: Costs,
    seed: int = 7,
    allow_expedite: bool = False,
    expedite_threshold_days: int = 2,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    on_hand = start_inventory
    pipeline: List[Dict] = []  # [{"arrival_day": int, "qty": int}]
    rows = []

    for day in range(1, days + 1):
        # Receive inbound
        arriving = [p for p in pipeline if p["arrival_day"] == day]
        if arriving:
            on_hand += sum(p["qty"] for p in arriving)
        pipeline = [p for p in pipeline if p["arrival_day"] != day]

        # Demand
        demand = sample_demand(rng, demand_mean, demand_std)
        shipped = min(on_hand, demand)
        lost = demand - shipped
        on_hand -= shipped

        # Expedite (optional): if empty and next arrival is far away
        expedited = 0
        expedite_cost = 0.0
        if allow_expedite and on_hand == 0:
            next_arrival = min([p["arrival_day"] for p in pipeline], default=10**9)
            if next_arrival - day >= expedite_threshold_days:
                expedited = policy.order_qty
                pipeline.append({"arrival_day": day + 1, "qty": expedited})
                expedite_cost = costs.expedite_fixed

        # Reorder decision
        on_order = sum(p["qty"] for p in pipeline)
        if should_reorder(on_hand, on_order, policy):
            lt_days = sample_lead_time(rng, lead_time)
            pipeline.append({"arrival_day": day + lt_days, "qty": policy.order_qty})

        holding_cost = on_hand * costs.holding_per_unit_per_day
        stockout_cost = lost * costs.stockout_per_unit

        rows.append({
            "day": day,
            "demand": demand,
            "shipped": shipped,
            "lost_sales": lost,
            "on_hand_end": on_hand,
            "on_order_end": sum(p["qty"] for p in pipeline),
            "holding_cost": holding_cost,
            "stockout_cost": stockout_cost,
            "expedite_qty": expedited,
            "expedite_cost": expedite_cost,
        })

    return pd.DataFrame(rows)
