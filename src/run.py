# src/run.py
import os
import matplotlib.pyplot as plt

from .sim import run_sim, LeadTime, Costs
from .policies import Policy
from .metrics import summarize, recommendation
from .tune import run_tuning_and_save


def main():
    os.makedirs("outputs", exist_ok=True)

    # ---- Baseline scenario inputs ----
    DAYS = 180
    DEMAND_MEAN = 40
    DEMAND_STD = 12
    START_INV = 200
    TARGET_SL = 0.97

    lt = LeadTime(mean_days=7, std_days=2, min_days=2)
    costs = Costs(holding_per_unit_per_day=0.02, stockout_per_unit=3.00, expedite_fixed=250.0)

    # ---- Auto-tune search space ----
    rop_values = list(range(80, 281, 20))    # 80..280 step 20
    q_values = list(range(100, 401, 50))     # 100..400 step 50

    print("Running auto-tune (grid search)...")
    results_df, best_df = run_tuning_and_save(
        days=DAYS,
        demand_mean=DEMAND_MEAN,
        demand_std=DEMAND_STD,
        lead_time=lt,
        start_inventory=START_INV,
        costs=costs,
        target_service_level=TARGET_SL,
        rop_values=rop_values,
        q_values=q_values,
        seed=7,
        allow_expedite=True,
        expedite_threshold_days=2,
    )

    best = best_df.iloc[0].to_dict()
    best_policy = Policy(reorder_point=int(best["rop"]), order_qty=int(best["q"]))

    print("\n=== BEST POLICY FOUND ===")
    print(f"ROP={best_policy.reorder_point}, Q={best_policy.order_qty}")
    print(f"Service Level={best['service_level']:.3f} (target {TARGET_SL:.2f})")
    print(f"Total Cost={best['total_cost']:.2f}")
    print("(Saved outputs/tuning_results.csv and outputs/best_policy.csv)")

    # ---- Re-run sim with best policy to generate plot + ledger ----
    df = run_sim(
        days=DAYS,
        demand_mean=DEMAND_MEAN,
        demand_std=DEMAND_STD,
        lead_time=lt,
        start_inventory=START_INV,
        policy=best_policy,
        costs=costs,
        seed=7,
        allow_expedite=True,
        expedite_threshold_days=2,
    )

    df.to_csv("outputs/results_best_policy.csv", index=False)

    plt.figure()
    plt.plot(df["day"], df["on_hand_end"])
    plt.title("On-hand Inventory Over Time (Best Policy)")
    plt.xlabel("Day")
    plt.ylabel("Units")
    plt.tight_layout()
    plt.savefig("outputs/inventory_best_policy.png", dpi=200)

    s = summarize(df)
    rec = recommendation(s, target_service_level=TARGET_SL)

    print("\n=== SUMMARY (Best Policy Simulation) ===")
    for k, v in s.items():
        print(f"{k}: {v}")
    print("\n=== RECOMMENDATION ===")
    print(rec)

    print("\nSaved:")
    print("- outputs/tuning_results.csv")
    print("- outputs/best_policy.csv")
    print("- outputs/results_best_policy.csv")
    print("- outputs/inventory_best_policy.png")


if __name__ == "__main__":
    main()
