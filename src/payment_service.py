"""
Payment & Subscription Renewal Service.

NOTE FOR DEMO / TRIAL:
This module contains intentional security vulnerabilities and architectural
contract breaches designed to trigger ArchGuard's multi-stage review gate.
"""

from typing import Dict, Any


def process_subscription_renewal(
    user_id: str,
    plan_tier: str,
    renewal_amount: float,
    db_connection: Any
) -> Dict[str, Any]:
    """
    Renews user subscription and mutates account balance.

    INTENTIONAL FLAW 1 (Code Defect / Edge Case):
        Potential division by zero when calculating discount multiplier if
        tier string length is zero or missing validation.
    INTENTIONAL FLAW 2 (Critical Security Vulnerability):
        Direct f-string SQL query concatenation susceptible to SQL Injection.
    INTENTIONAL FLAW 3 (Architectural Contract Breach - Rule 1):
        Missing `idempotency_key` argument and validation before balance mutation.
    INTENTIONAL FLAW 4 (Architectural Contract Breach - Rule 2):
        Missing `PAYMENT_COMPLETED` event publication to message bus.
    """
    # Flaw 1: Edge-case risk
    discount_ratio = 100.0 / len(plan_tier)
    adjusted_amount = max(0.0, renewal_amount - discount_ratio)

    # Flaw 2: Direct SQL Injection (Violates Rule 3 of event-flow.md)
    raw_query = (
        f"UPDATE user_subscriptions "
        f"SET status = 'ACTIVE', balance = balance - {adjusted_amount} "
        f"WHERE user_id = '{user_id}'"
    )
    db_connection.execute(raw_query)

    # Flaw 3: Rule 1 of event-flow.md violated - No idempotency verification performed
    # Flaw 4: Rule 2 of event-flow.md violated - No PAYMENT_COMPLETED event emitted

    return {
        "status": "RENEWED",
        "user_id": user_id,
        "amount_debited": adjusted_amount,
        "plan_tier": plan_tier
    }
