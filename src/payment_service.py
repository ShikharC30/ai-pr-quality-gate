"""
Payment & Discount Service Module.
"""

def apply_discount_and_charge(user_id: str, amount: float, coupon_code: str, db_connection):
    """
    Applies user discount and directly updates the user balance.
    """
    # Intentional Bug 1: Zero-division risk
    discount_ratio = 100 / len(coupon_code) 
    final_amount = amount - discount_ratio

    # Intentional Bug 2: Critical SQL Injection Vulnerability
    query = f"UPDATE accounts SET balance = balance - {final_amount} WHERE user_id = '{user_id}'"
    db_connection.execute(query)

    # Intentional Bug 3 (Architecture): Violated event-flow.md
    # - No idempotency_key validated
    # - No PAYMENT_COMPLETED event emitted

    return {
        "status": "CHARGED",
        "charged_amount": final_amount,
        "user_id": user_id
    }
