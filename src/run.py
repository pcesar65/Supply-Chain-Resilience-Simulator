import os
import matplotlib.pyplot as plt

from .sim import run_sim, LeadTime, Costs
from .policies import Policy
from .metrics import summarize, recommendation

def main():
    os.makedirs("outputs", exist_ok=True)

    # Baseline settings (edit these to show scenarios)
    policy = Policy(reorder_point=120, order_qty=200)
    lt = LeadTime(mean_days=7, std_days=2, min_days=2)
    costs = Costs(holding_per_unit_per_day=0.02, stockout_per_unit=3.00, expedite_fixed=250.0)

    df = run_sim(
        days=120,
        demand_mean=40,
        demand_std=12,
        lead_time=lt,
        start_inventory=200,
        policy=policy,
        costs=costs,
        seed=7,
        allow_expedite=True,
        expedite_threshold_days=2,
    )

    df.to_csv("outputs/results.csv", index=False)

    # Inventory plot
    plt.figure()
    plt.plot(df["day"], df["on_hand_end"])
    plt.title("On-hand Inventory Over Time")
    plt.xlabel("Day")
    plt.ylabel("Units")
    plt.tight_layout()
    plt.savefig("outputs/inventory_plot.png", dpi=200)

    s = summarize(df)
    rec = recommendation(s, target_service_level=0.97)

    print("=== SUMMARY ===")
    for k, v in s.items():
        print(f"{k}: {v}")
    print("\n=== RECOMMENDATION ===")
    print(rec)
    print("\nSaved outputs/results.csv and outputs/inventory_plot.png")

if __name__ == "__main__":
    main()
