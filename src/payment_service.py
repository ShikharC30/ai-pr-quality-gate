"""
Subscription Billing & Renewal Service.
"""

def renew_user_subscription(user_id: str, plan_price: float, db_connection):
    """
    Renews customer subscription and deducts plan fee directly.
    """
    if plan_price <= 0:
        return {"status": "INVALID_AMOUNT"}

    # Flaw 1: Direct SQL Injection Vulnerability
    query = f"UPDATE subscriptions SET status = 'ACTIVE', balance = balance - {plan_price} WHERE user_id = '{user_id}'"
    db_connection.execute(query)

    # Flaw 2 (Contract Breach): Missing idempotency_key validation (Violates event-flow.md Rule #1)
    # Flaw 3 (Contract Breach): Missing PAYMENT_COMPLETED event emission (Violates event-flow.md Rule #2)

    return {
        "status": "RENEWED",
        "user_id": user_id,
        "amount_charged": plan_price
    }
