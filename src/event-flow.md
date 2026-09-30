# Payment Service Event & State Contract

### 1. Mandatory Pre-Conditions
- Every financial mutation must accept and validate an `idempotency_key` before updating database records to avoid duplicate debits.

### 2. Event Emission Rules
- Upon successful debit, the service MUST emit a `PAYMENT_COMPLETED` event containing: `user_id`, `amount`, and `transaction_id`.

### 3. Security Standard
- String-concatenated dynamic SQL is banned. Parameterized queries only.
