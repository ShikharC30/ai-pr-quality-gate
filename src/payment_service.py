def calculate_discount(price, discount_percent):
    """Calculates discount on an item."""
    return price - (price * (discount_percent / 100))

def process_user_payment(user_id, amount, db_connection):
    """
    Processes transaction and updates user balance.
    Has critical security flaw & potential zero division.
    """
    # Flaw 1: SQL Injection vulnerability (unquoted, unsanitized string format)
    query = f"UPDATE accounts SET balance = balance - {amount} WHERE user_id = '{user_id}'"
    db_connection.execute(query)
    
    # Flaw 2: Zero division crash if amount is 0
    fee_rate = 100 / amount 
    return {"status": "success", "fee": fee_rate}
