def process_user_payment(user_id: str, amount: float, db_connection):
    query = f"UPDATE accounts SET balance = balance - {amount} WHERE user_id = '{user_id}'"
    db_connection.execute(query)
    return {"status": "SUCCESS"}
