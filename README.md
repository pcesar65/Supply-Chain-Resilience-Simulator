# Supply Chain Resilience Simulator (Digital Twin)

A single-SKU inventory simulation that models **demand volatility + lead-time variability** and evaluates the tradeoff between:
- **Service level (fill rate)**
- **Holding cost (working capital + storage)**
- **Stockout cost (lost sales / SLA penalties)**
- Optional **expedite strategy**

## Why it matters
Ops teams don’t debate inventory policies in theory—decisions impact **OTIF, SLA misses, and cost**.  
This simulator makes the tradeoffs measurable under volatility and disruptions.

## What it does
- Simulates daily demand and replenishment over N days
- Implements (ROP, Q) reorder policy
- Models stochastic lead time
- Produces metrics: service level, stockout days, cost breakdown
- Generates a recommendation relative to a target service level

## Run
```bash
pip install -r requirements.txt
python -m src.run
