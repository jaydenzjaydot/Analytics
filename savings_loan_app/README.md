# Member Savings & Loan Management System

A comprehensive web-based Python application for managing member savings and loan schemes, built with Flask and SQLAlchemy.

## 🎯 Overview

This system manages a member savings and loan scheme with the following features:
- Member registration and management
- Savings account tracking (initial deposits and monthly subscriptions)
- Loan management with interest calculations
- Automatic overdue interest calculations
- CSV export functionality for members and transactions
- Web-based interface for easy management

## ✨ Features

### Member Management
- Register new members with automatic initial deposit (SZL 1,000.00)
- View member details, savings balance, and loan information
- Track payment history for both savings and loans

### Savings Management
- Initial deposit: **SZL 1,000.00** (automatically applied on registration)
- Monthly subscription: **SZL 500.00** per month
- Subscription period: **12 months**
- Full transaction history tracking

### Loan Management
- Loan issuance with **20% interest rate**
- Interest calculated on principal amount at issue
- Repayments due on the **5th of every month**
- Automatic compound interest for overdue loans (**20% per month** on outstanding balance)
- Full loan transaction history

### Reporting & Export
- Dashboard with system statistics
- CSV export for member data
- CSV export for all transactions (savings and loans)
- JSON API endpoint for member summaries

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone/Navigate to the Application Directory

```bash
cd savings_loan_app
```

### Step 2: Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000` or `http://127.0.0.1:5000`

### Step 5: Access the Web Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

## 📖 Usage Guide

### Registering a New Member

1. Click **"Register Member"** in the navigation menu
2. Enter:
   - **Member ID**: Unique identifier (e.g., MEM001)
   - **Full Name**: Member's complete name
3. Click **"Register Member"**
4. The member will automatically receive an initial deposit of SZL 1,000.00

### Recording Savings Payments

1. Navigate to the member's detail page
2. Click **"Record Savings Payment"**
3. Enter the payment amount (default: SZL 500.00 for monthly subscription)
4. Click **"Record Payment"**

### Issuing a Loan

1. Navigate to the member's detail page
2. Click **"Issue Loan"** (only visible if member has no active loan)
3. Enter the principal loan amount
4. The system will automatically calculate:
   - Interest (20% of principal)
   - Total amount (principal + interest)
   - Next due date (5th of next month)
5. Click **"Issue Loan"**

### Recording Loan Repayments

1. Navigate to the member's detail page
2. Click **"Record Loan Repayment"**
3. Enter the payment amount (must not exceed current balance)
4. The system will:
   - Automatically apply overdue interest if payment is late
   - Update the loan balance
   - Set next due date to 5th of following month
   - Close the loan if balance reaches zero
5. Click **"Record Repayment"**

### Processing Overdue Interest

1. From the dashboard, click **"Process Overdue Interest"**
2. This will calculate and apply compound interest for all overdue loans
3. Interest is calculated as 20% of the outstanding balance per overdue month

### Exporting Data

**Export Members:**
- Click **"Export"** → **"Export Members"** in the navigation menu
- Download CSV file with all member information

**Export Transactions:**
- Click **"Export"** → **"Export Transactions"** in the navigation menu
- Download CSV file with all savings and loan transactions

## 🏗️ System Architecture

### Database Models

**Member**
- `id`: Primary key
- `full_name`: Member's full name
- `member_id`: Unique member identifier
- `date_joined`: Registration date
- `savings_balance`: Current savings balance

**SavingsTransaction**
- `id`: Primary key
- `member_id`: Foreign key to Member
- `amount`: Transaction amount
- `transaction_type`: Type of transaction (initial_deposit, monthly_subscription)
- `description`: Transaction description
- `transaction_date`: Timestamp

**Loan**
- `id`: Primary key
- `member_id`: Foreign key to Member
- `principal_amount`: Original loan amount
- `interest_rate`: Interest rate (0.20 for 20%)
- `interest_amount`: Total interest at issue
- `total_amount`: Principal + interest
- `current_balance`: Current outstanding balance
- `issue_date`: Loan issue date
- `next_due_date`: Next payment due date (5th of month)
- `is_active`: Whether loan is still active

**LoanTransaction**
- `id`: Primary key
- `loan_id`: Foreign key to Loan
- `amount`: Transaction amount
- `transaction_type`: Type (loan_issued, repayment, overdue_interest)
- `description`: Transaction description
- `transaction_date`: Timestamp

### Business Logic

**Interest Calculation:**
- Initial interest: 20% of principal amount (calculated at loan issue)
- Overdue interest: 20% compound interest per month on outstanding balance
- Applied automatically when payment is late (after the 5th of the month)

**Due Date Management:**
- All loans are due on the 5th of every month
- If payment is made on or before the 5th, next due date is 5th of current month
- If payment is made after the 5th, next due date is 5th of next month

## 🔧 API Endpoints

### Web Routes
- `GET /` - Dashboard
- `GET /members` - List all members
- `GET /members/new` - Registration form
- `POST /members/new` - Create new member
- `GET /members/<member_id>` - View member details
- `GET /members/<member_id>/savings/pay` - Savings payment form
- `POST /members/<member_id>/savings/pay` - Record savings payment
- `GET /members/<member_id>/loan/issue` - Loan issue form
- `POST /members/<member_id>/loan/issue` - Issue loan
- `GET /members/<member_id>/loan/repay` - Loan repayment form
- `POST /members/<member_id>/loan/repay` - Record loan repayment
- `GET /process_overdue` - Process overdue interest for all loans
- `GET /export/members/csv` - Export members to CSV
- `GET /export/transactions/csv` - Export transactions to CSV

### API Endpoints
- `GET /api/members/<member_id>/summary` - Get member summary as JSON

## 📊 Example Usage

### Example Scenario: Member Registration and Loan

1. **Register Member:**
   - Member ID: MEM001
   - Name: John Doe
   - Result: Account created with SZL 1,000.00 initial deposit

2. **Record Monthly Subscription:**
   - Amount: SZL 500.00
   - Result: Savings balance now SZL 1,500.00

3. **Issue Loan:**
   - Principal: SZL 10,000.00
   - Interest (20%): SZL 2,000.00
   - Total: SZL 12,000.00
   - Due Date: 5th of next month

4. **Record Loan Repayment (on time):**
   - Payment: SZL 3,000.00
   - Result: Balance reduced to SZL 9,000.00
   - Next due date: 5th of following month

5. **Late Payment Scenario:**
   - Loan overdue by 2 months
   - Original balance: SZL 9,000.00
   - Month 1 interest (20%): SZL 1,800.00 → New balance: SZL 10,800.00
   - Month 2 interest (20%): SZL 2,160.00 → New balance: SZL 12,960.00
   - Total balance after 2 months overdue: SZL 12,960.00

## 🔒 Security Notes

- **Change the SECRET_KEY** in `app.py` before deploying to production
- Consider using environment variables for sensitive configuration
- Implement authentication/authorization for production use
- Use HTTPS in production environments
- Consider using PostgreSQL or MySQL for production instead of SQLite

## 🛠️ Technical Details

### Technologies Used
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Database (can be easily switched to PostgreSQL/MySQL)
- **Bootstrap 5**: Frontend styling
- **Python 3.8+**: Programming language

### File Structure
```
savings_loan_app/
├── app.py                 # Main application file with routes and models
├── models.py             # Database models (currently inline in app.py)
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Dashboard
│   ├── members.html     # Members list
│   ├── add_member.html  # Member registration
│   ├── member_detail.html # Member details
│   ├── pay_savings.html # Savings payment form
│   ├── issue_loan.html  # Loan issue form
│   └── repay_loan.html  # Loan repayment form
└── savings_loan.db      # SQLite database (created on first run)
```

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors:
1. Delete `savings_loan.db` if it exists
2. Restart the application
3. Tables will be recreated automatically

### Port Already in Use
If port 5000 is already in use:
```python
# Edit app.py, change the port in the last line:
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## 📝 License

This project is open-source and available for use and modification.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue in the repository or contact the development team.

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Author:** Senior Python Software Engineer & Financial Systems Designer
