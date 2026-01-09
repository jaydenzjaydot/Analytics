# System Design Documentation

## Architecture Overview

The Member Savings & Loan Management System is a web-based application built with Flask (Python) that manages member savings accounts and loans according to specific business rules.

## Class Structure (Object-Oriented Design)

### 1. Member Class
**Purpose:** Represents a registered member in the savings and loan scheme.

**Attributes:**
- `id`: Primary key (Integer)
- `full_name`: Member's full name (String, 200 chars)
- `member_id`: Unique member identifier (String, 50 chars, indexed)
- `date_joined`: Date when member joined (Date)
- `savings_balance`: Current savings balance (Decimal, 10.2 precision)

**Methods:**
- `to_dict()`: Convert member instance to dictionary for API responses
- `__repr__()`: String representation for debugging

**Relationships:**
- Has many SavingsTransaction records
- Has many Loan records

### 2. SavingsTransaction Class
**Purpose:** Records all savings-related transactions (deposits, subscriptions).

**Attributes:**
- `id`: Primary key (Integer)
- `member_id`: Foreign key to Member (Integer, indexed)
- `amount`: Transaction amount (Decimal, 10.2 precision)
- `transaction_type`: Type of transaction (String, 50 chars)
  - Types: 'initial_deposit', 'monthly_subscription'
- `description`: Transaction description (Text)
- `transaction_date`: Timestamp of transaction (DateTime, indexed)

**Relationships:**
- Belongs to one Member

### 3. Loan Class
**Purpose:** Represents a loan issued to a member.

**Attributes:**
- `id`: Primary key (Integer)
- `member_id`: Foreign key to Member (Integer, indexed)
- `principal_amount`: Original loan amount before interest (Decimal, 10.2)
- `interest_rate`: Interest rate (Decimal, 5.4 precision, e.g., 0.2000 for 20%)
- `interest_amount`: Total interest calculated at issue (Decimal, 10.2)
- `total_amount`: Principal + interest (Decimal, 10.2)
- `current_balance`: Current outstanding balance (Decimal, 10.2)
  - Decreases with payments
  - Increases with overdue interest
- `issue_date`: Date when loan was issued (Date, indexed)
- `next_due_date`: Next payment due date - always 5th of month (Date, indexed)
- `is_active`: Whether loan is still active/not fully repaid (Boolean, indexed)

**Methods:**
- `to_dict()`: Convert loan instance to dictionary for API responses
- `__repr__()`: String representation for debugging

**Relationships:**
- Belongs to one Member
- Has many LoanTransaction records

### 4. LoanTransaction Class
**Purpose:** Records all loan-related transactions (issuance, repayments, interest).

**Attributes:**
- `id`: Primary key (Integer)
- `loan_id`: Foreign key to Loan (Integer, indexed)
- `amount`: Transaction amount (Decimal, 10.2 precision)
- `transaction_type`: Type of transaction (String, 50 chars)
  - Types: 'loan_issued', 'repayment', 'overdue_interest'
- `description`: Transaction description (Text)
- `transaction_date`: Timestamp of transaction (DateTime, indexed)

**Relationships:**
- Belongs to one Loan

## Business Rules Implementation

### Savings Rules

1. **Initial Deposit (SZL 1,000.00)**
   - Automatically applied when member is registered
   - Implemented in: `add_member()` route
   - Transaction type: 'initial_deposit'

2. **Monthly Subscription (SZL 500.00)**
   - Standard monthly payment amount
   - Can be customized per payment
   - Subscription period: 12 months (tracked via transactions)
   - Implemented in: `pay_savings()` route
   - Transaction type: 'monthly_subscription'

3. **Savings Balance Tracking**
   - Updated automatically on each transaction
   - Maintains historical record via SavingsTransaction model
   - Balance increases with each payment

### Loan Rules

1. **Interest Rate (20%)**
   - Constant: `LOAN_INTEREST_RATE = Decimal('0.20')`
   - Applied to principal amount at loan issue
   - Calculation: `interest_amount = principal_amount * 0.20`

2. **Initial Interest Calculation**
   - Calculated once at loan issue
   - Added to principal: `total_amount = principal + interest`
   - Stored in `interest_amount` and `total_amount` fields
   - Implemented in: `issue_loan()` route

3. **Loan Due Dates (5th of Every Month)**
   - Constant: `LOAN_DUE_DAY = 5`
   - Calculated based on current date:
     - If today is on or before 5th: due date is 5th of current month
     - If today is after 5th: due date is 5th of next month
   - Updated after each repayment
   - Implemented in: `issue_loan()` and `repay_loan()` routes

4. **Overdue Interest (Compound, 20% per month)**
   - Applied automatically when payment is late
   - Compound calculation: 20% of current balance per overdue month
   - Example: 
     - Month 1 overdue: Balance × 1.20
     - Month 2 overdue: (Balance × 1.20) × 1.20
   - Implemented in: `_apply_overdue_interest()` function
   - Called automatically in: `repay_loan()` and `process_overdue()` routes

### Date Management

- Uses Python's `datetime.date` for date-only fields
- Uses `datetime.datetime` for timestamps
- All calculations use `Decimal` for financial precision

## Calculation Examples

### Example 1: Loan Issuance
```
Principal: SZL 10,000.00
Interest (20%): SZL 2,000.00
Total Amount: SZL 12,000.00
Current Balance: SZL 12,000.00
Next Due Date: 5th of next month
```

### Example 2: On-Time Repayment
```
Current Balance: SZL 12,000.00
Payment: SZL 3,000.00
New Balance: SZL 9,000.00
Next Due Date: Updated to 5th of following month
```

### Example 3: Overdue Loan (2 months late)
```
Original Balance: SZL 9,000.00
Month 1 Interest (20%): SZL 1,800.00
New Balance: SZL 10,800.00
Month 2 Interest (20%): SZL 2,160.00
Final Balance: SZL 12,960.00
```

## Database Schema

### Tables

1. **members**
   - id (INTEGER PRIMARY KEY)
   - full_name (VARCHAR(200))
   - member_id (VARCHAR(50) UNIQUE)
   - date_joined (DATE)
   - savings_balance (NUMERIC(10,2))

2. **savings_transactions**
   - id (INTEGER PRIMARY KEY)
   - member_id (INTEGER, FOREIGN KEY)
   - amount (NUMERIC(10,2))
   - transaction_type (VARCHAR(50))
   - description (TEXT)
   - transaction_date (DATETIME)

3. **loans**
   - id (INTEGER PRIMARY KEY)
   - member_id (INTEGER, FOREIGN KEY)
   - principal_amount (NUMERIC(10,2))
   - interest_rate (NUMERIC(5,4))
   - interest_amount (NUMERIC(10,2))
   - total_amount (NUMERIC(10,2))
   - current_balance (NUMERIC(10,2))
   - issue_date (DATE)
   - next_due_date (DATE)
   - is_active (BOOLEAN)

4. **loan_transactions**
   - id (INTEGER PRIMARY KEY)
   - loan_id (INTEGER, FOREIGN KEY)
   - amount (NUMERIC(10,2))
   - transaction_type (VARCHAR(50))
   - description (TEXT)
   - transaction_date (DATETIME)

### Indexes
- member_id (on members, savings_transactions, loans)
- transaction_date (on savings_transactions, loan_transactions)
- issue_date, next_due_date, is_active (on loans)

## Route Structure

### Main Routes
- `/` - Dashboard (statistics overview)
- `/members` - List all members
- `/members/new` - Register new member
- `/members/<id>` - View member details
- `/members/<id>/savings/pay` - Record savings payment
- `/members/<id>/loan/issue` - Issue loan
- `/members/<id>/loan/repay` - Record loan repayment
- `/process_overdue` - Process overdue interest (admin)

### Export Routes
- `/export/members/csv` - Export members to CSV
- `/export/transactions/csv` - Export all transactions to CSV

### API Routes
- `/api/members/<id>/summary` - Get member summary as JSON

## Key Functions

### `_apply_overdue_interest(loan, current_date)`
**Purpose:** Calculate and apply compound interest for overdue loans.

**Logic:**
1. Check if loan is overdue (next_due_date < current_date)
2. Calculate months overdue
3. Apply 20% interest per month on current balance (compound)
4. Record each interest charge as a transaction
5. Update next_due_date to 5th of current/next month
6. Flash warning message with total interest applied

**Called by:**
- `repay_loan()` - Before processing payment
- `process_overdue()` - For all active loans

## Error Handling

- Member ID uniqueness validation
- Loan amount validation (> 0)
- Payment amount validation (0 < amount <= balance)
- Active loan existence checks
- Flash messages for all user actions
- 404 errors for non-existent resources

## Security Considerations

1. **SECRET_KEY**: Change before production deployment
2. **SQL Injection**: Prevented via SQLAlchemy ORM
3. **Input Validation**: All user inputs validated
4. **CSRF Protection**: Should be added for production
5. **Authentication**: Not implemented (add for production)

## Extension Points

The system is designed to be easily extended:

1. **GUI/Web App**: Already implemented with Flask
2. **Additional Reports**: Add new routes and templates
3. **Email Notifications**: Add to transaction handlers
4. **SMS Alerts**: Add to overdue processing
5. **Multiple Loan Types**: Extend Loan model
6. **Interest Rate Changes**: Add to Loan model as history
7. **Payment Plans**: Add payment plan scheduling
8. **Member Groups**: Add categorization/tags

## Testing Recommendations

1. **Unit Tests**: Test each model method
2. **Integration Tests**: Test routes and database operations
3. **Calculation Tests**: Verify interest calculations
4. **Date Logic Tests**: Verify due date calculations
5. **Overdue Interest Tests**: Verify compound interest
6. **Edge Cases**: Zero amounts, negative balances, etc.

## Performance Considerations

1. **Database Indexes**: Already implemented on key fields
2. **Query Optimization**: Use eager loading for relationships if needed
3. **Caching**: Consider Redis for frequently accessed data
4. **Pagination**: Add for large member lists
5. **Background Jobs**: Move overdue processing to scheduled tasks

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Designer:** Senior Python Software Engineer & Financial Systems Designer
