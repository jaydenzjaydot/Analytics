# Quick Start Guide

## Installation & Running

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Open Browser
Navigate to: `http://localhost:5000`

## Quick Test Scenario

### 1. Register a Member
- Click **"Register Member"**
- Member ID: `MEM001`
- Full Name: `John Doe`
- Click **"Register Member"**
- **Result:** Member created with SZL 1,000.00 initial deposit

### 2. Record Savings Payment
- Go to member's detail page
- Click **"Record Savings Payment"**
- Amount: `500.00` (or use default)
- Click **"Record Payment"**
- **Result:** Savings balance now SZL 1,500.00

### 3. Issue a Loan
- On member's detail page, click **"Issue Loan"**
- Loan Amount: `10000.00`
- Click **"Issue Loan"**
- **Result:** 
  - Principal: SZL 10,000.00
  - Interest (20%): SZL 2,000.00
  - Total: SZL 12,000.00
  - Due Date: 5th of next month

### 4. Record Loan Repayment
- On member's detail page, click **"Record Loan Repayment"**
- Payment Amount: `3000.00`
- Click **"Record Repayment"**
- **Result:** 
  - Balance reduced to SZL 9,000.00
  - Next due date updated

### 5. Export Data
- Click **"Export"** → **"Export Members CSV"**
- Click **"Export"** → **"Export Transactions CSV"**

## Key Features Demonstrated

✅ Member Registration with automatic initial deposit  
✅ Savings payment recording  
✅ Loan issuance with 20% interest calculation  
✅ Loan repayment processing  
✅ CSV export functionality  
✅ Dashboard statistics  
✅ Transaction history  

## Business Rules Verified

- ✅ Initial deposit: SZL 1,000.00 (automatically applied)
- ✅ Monthly subscription: SZL 500.00
- ✅ Loan interest: 20% of principal
- ✅ Due dates: 5th of every month
- ✅ Overdue interest: 20% compound per month (test by setting a past due date)

## Testing Overdue Interest

To test overdue interest calculation:

1. Issue a loan to a member
2. Manually update the `next_due_date` in the database to a past date
   - Or wait until after the 5th of the month
3. Go to Dashboard and click **"Process Overdue Interest"**
4. View the member's loan - interest should be applied
5. Try recording a repayment - overdue interest will be calculated automatically

## Common Issues

**Port 5000 already in use:**
- Edit `app.py`, change port in last line: `port=5001`

**Database errors:**
- Delete `savings_loan.db` and restart app

**Import errors:**
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

---

For detailed documentation, see `README.md` and `SYSTEM_DESIGN.md`
