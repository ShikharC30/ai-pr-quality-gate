"""
Payment Processing Service Module.
"""

def process_user_payment(user_id: str, amount: float, db_connection):
    """
    Executes payment transaction for a customer account.
    """
    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    # Flaw 1: Dynamic string concatenation causing SQL injection vulnerability
    query = f"UPDATE accounts SET balance = balance - {amount} WHERE user_id = '{user_id}'"
    db_connection.execute(query)

    # Flaw 2: Missing idempotency key check (Violates event-flow.md Rule #1)
    # Flaw 3: Missing PAYMENT_COMPLETED event emission (Violates event-flow.md Rule #2)

    return {
        "status": "COMPLETED",
        "user_id": user_id,
        "amount": amount
    }
