# Auto-committed via developer approval

import pytest
from unittest.mock import Mock, call

# The function under test (copied for runnable test code)
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

# --- PyTest Test Code ---

@pytest.fixture
def mock_db_connection():
    """Fixture for a mocked database connection."""
    return Mock()

def test_renew_user_subscription_success(mock_db_connection):
    """
    Tests successful subscription renewal.
    """
    user_id = "test_user_456"
    plan_price = 50.00
    
    result = renew_user_subscription(user_id, plan_price, mock_db_connection)
    
    assert result == {
        "status": "RENEWED",
        "user_id": user_id,
        "amount_charged": plan_price
    }
    
    # Verify the database query executed (demonstrating the string concatenation flaw)
    expected_query = f"UPDATE subscriptions SET status = 'ACTIVE', balance = 50.0 WHERE user_id = 'test_user_456'"
    mock_db_connection.execute.assert_called_once_with(
        "UPDATE subscriptions SET status = 'ACTIVE', balance = balance - 50.0 WHERE user_id = 'test_user_456'"
    )

def test_renew_user_subscription_invalid_plan_price(mock_db_connection):
    """
    Tests renewal with an invalid (non-positive) plan price.
    """
    user_id = "test_user_789"
    plan_price = 0.00
    
    result = renew_user_subscription(user_id, plan_price, mock_db_connection)
    
    assert result == {"status": "INVALID_AMOUNT"}
    
    # Ensure no database operation occurred for invalid price
    mock_db_connection.execute.assert_not_called()

def test_renew_user_subscription_sql_injection_potential(mock_db_connection):
    """
    Demonstrates the SQL injection vulnerability by showing the constructed query
    when a malicious user_id is provided.
    """
    malicious_user_id = "malicious_user'; DROP TABLE users; --"
    plan_price = 25.00
    
    renew_user_subscription(malicious_user_id, plan_price, mock_db_connection)
    
    # The assertion below passes, confirming that the malicious string is directly
    # embedded into the query, which is the core of the SQL injection vulnerability.
    expected_query_with_injection = (
        "UPDATE subscriptions SET status = 'ACTIVE', balance = balance - 25.0 WHERE user_id = 'malicious_user'; DROP TABLE users; --'"
    )
    mock_db_connection.execute.assert_called_once_with(expected_query_with_injection)

# Note: No explicit tests for missing idempotency_key or event emission here,
# as the function neither accepts these as arguments nor internally depends on
# a mockable global/instance for them. The architectural review has already
# captured these critical contract violations.
