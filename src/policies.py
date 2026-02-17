from dataclasses import dataclass

@dataclass
class Policy:
    reorder_point: int   # ROP
    order_qty: int       # Q

def should_reorder(on_hand: int, on_order: int, policy: Policy) -> bool:
    inv_position = on_hand + on_order
    return inv_position <= policy.reorder_point
