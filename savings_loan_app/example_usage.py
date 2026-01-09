"""
Example usage script for the Member Savings & Loan Management System.

This script demonstrates how to interact with the system programmatically
(useful for testing or batch operations).

Note: This requires the Flask app to be running or uses the database directly.
"""

from app import app, db, Member, SavingsTransaction, Loan, LoanTransaction, INITIAL_DEPOSIT, MONTHLY_SUBSCRIPTION, LOAN_INTEREST_RATE
from datetime import date, datetime
from decimal import Decimal


def example_create_member():
    """Example: Create a new member."""
    with app.app_context():
        member = Member(
            full_name="John Doe",
            member_id="MEM001",
            date_joined=date.today(),
            savings_balance=INITIAL_DEPOSIT
        )
        db.session.add(member)
        
        # Record initial deposit transaction
        transaction = SavingsTransaction(
            member_id=member.id,
            amount=INITIAL_DEPOSIT,
            transaction_type='initial_deposit',
            description=f'Initial deposit of SZL {INITIAL_DEPOSIT}'
        )
        db.session.add(transaction)
        db.session.commit()
        
        print(f"Created member: {member.full_name} ({member.member_id}) with initial deposit of SZL {INITIAL_DEPOSIT}")
        return member


def example_record_savings_payment(member_id, amount=None):
    """Example: Record a savings payment."""
    with app.app_context():
        member = Member.query.get(member_id)
        if not member:
            print(f"Member {member_id} not found")
            return
        
        payment_amount = amount or MONTHLY_SUBSCRIPTION
        
        # Update savings balance
        member.savings_balance += payment_amount
        
        # Record transaction
        transaction = SavingsTransaction(
            member_id=member_id,
            amount=payment_amount,
            transaction_type='monthly_subscription',
            description=f'Monthly subscription payment of SZL {payment_amount}'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        print(f"Recorded savings payment of SZL {payment_amount} for {member.full_name}")
        print(f"New savings balance: SZL {member.savings_balance}")


def example_issue_loan(member_id, principal_amount):
    """Example: Issue a loan to a member."""
    with app.app_context():
        member = Member.query.get(member_id)
        if not member:
            print(f"Member {member_id} not found")
            return
        
        # Check for existing active loan
        existing_loan = Loan.query.filter_by(member_id=member_id, is_active=True).first()
        if existing_loan:
            print(f"Member {member.full_name} already has an active loan")
            return
        
        # Calculate interest
        interest_amount = principal_amount * LOAN_INTEREST_RATE
        total_amount = principal_amount + interest_amount
        
        # Calculate due date (5th of next month)
        today = date.today()
        LOAN_DUE_DAY = 5
        if today.day <= LOAN_DUE_DAY:
            due_date = date(today.year, today.month, LOAN_DUE_DAY)
        else:
            if today.month == 12:
                due_date = date(today.year + 1, 1, LOAN_DUE_DAY)
            else:
                due_date = date(today.year, today.month + 1, LOAN_DUE_DAY)
        
        # Create loan
        loan = Loan(
            member_id=member_id,
            principal_amount=principal_amount,
            interest_rate=LOAN_INTEREST_RATE,
            interest_amount=interest_amount,
            total_amount=total_amount,
            current_balance=total_amount,
            issue_date=date.today(),
            next_due_date=due_date,
            is_active=True
        )
        
        db.session.add(loan)
        
        # Record loan transaction
        transaction = LoanTransaction(
            loan_id=loan.id,
            amount=principal_amount,
            transaction_type='loan_issued',
            description=f'Loan issued: Principal SZL {principal_amount}, Interest SZL {interest_amount}'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        print(f"Issued loan of SZL {principal_amount} to {member.full_name}")
        print(f"Interest: SZL {interest_amount} (20%)")
        print(f"Total amount due: SZL {total_amount}")
        print(f"Next due date: {due_date}")


def example_repay_loan(member_id, payment_amount):
    """Example: Record a loan repayment."""
    with app.app_context():
        member = Member.query.get(member_id)
        if not member:
            print(f"Member {member_id} not found")
            return
        
        loan = Loan.query.filter_by(member_id=member_id, is_active=True).first()
        if not loan:
            print(f"Member {member.full_name} has no active loan")
            return
        
        if payment_amount > loan.current_balance:
            print(f"Payment amount (SZL {payment_amount}) exceeds balance (SZL {loan.current_balance})")
            return
        
        # Update loan balance
        loan.current_balance -= payment_amount
        
        # Record transaction
        transaction = LoanTransaction(
            loan_id=loan.id,
            amount=payment_amount,
            transaction_type='repayment',
            description=f'Loan repayment of SZL {payment_amount}'
        )
        
        db.session.add(transaction)
        
        # Check if loan is fully paid
        if loan.current_balance <= Decimal('0.01'):
            loan.is_active = False
            loan.current_balance = Decimal('0.00')
            print(f"Loan fully repaid and closed for {member.full_name}")
        else:
            # Update next due date
            today = date.today()
            LOAN_DUE_DAY = 5
            if today.day <= LOAN_DUE_DAY:
                next_due = date(today.year, today.month, LOAN_DUE_DAY)
            else:
                if today.month == 12:
                    next_due = date(today.year + 1, 1, LOAN_DUE_DAY)
                else:
                    next_due = date(today.year, today.month + 1, LOAN_DUE_DAY)
            loan.next_due_date = next_due
            print(f"Recorded payment of SZL {payment_amount} for {member.full_name}")
            print(f"Remaining balance: SZL {loan.current_balance}")
            print(f"Next due date: {next_due}")
        
        db.session.commit()


def example_view_member_summary(member_id):
    """Example: View member summary."""
    with app.app_context():
        member = Member.query.get(member_id)
        if not member:
            print(f"Member {member_id} not found")
            return
        
        active_loan = Loan.query.filter_by(member_id=member_id, is_active=True).first()
        
        print("\n" + "="*50)
        print(f"MEMBER SUMMARY: {member.full_name}")
        print("="*50)
        print(f"Member ID: {member.member_id}")
        print(f"Date Joined: {member.date_joined}")
        print(f"Savings Balance: SZL {member.savings_balance:,.2f}")
        
        if active_loan:
            print(f"\nLOAN INFORMATION:")
            print(f"  Principal Amount: SZL {active_loan.principal_amount:,.2f}")
            print(f"  Interest Rate: {active_loan.interest_rate*100:.0f}%")
            print(f"  Current Balance: SZL {active_loan.current_balance:,.2f}")
            print(f"  Next Due Date: {active_loan.next_due_date}")
            today = date.today()
            if active_loan.next_due_date < today:
                days_overdue = (today - active_loan.next_due_date).days
                print(f"  Status: OVERDUE ({days_overdue} days)")
            else:
                print(f"  Status: Active")
        else:
            print(f"\nLOAN INFORMATION: No active loan")
        
        print("="*50 + "\n")


if __name__ == '__main__':
    print("Example Usage Script for Savings & Loan Management System")
    print("="*60)
    print("\nNote: This script requires the database to be initialized.")
    print("Run the Flask app first to create the database tables.")
    print("\nTo use these functions:")
    print("1. Uncomment the function calls below")
    print("2. Ensure the Flask app has created the database")
    print("3. Run: python example_usage.py")
    
    # Example usage (uncomment to run):
    # with app.app_context():
    #     db.create_all()  # Create tables if they don't exist
    
    # # Create a member
    # member = example_create_member()
    
    # # Record savings payments
    # example_record_savings_payment(member.id, MONTHLY_SUBSCRIPTION)
    # example_record_savings_payment(member.id, MONTHLY_SUBSCRIPTION)
    
    # # Issue a loan
    # example_issue_loan(member.id, Decimal('10000.00'))
    
    # # View member summary
    # example_view_member_summary(member.id)
    
    # # Repay loan
    # example_repay_loan(member.id, Decimal('3000.00'))
    
    # # View updated summary
    # example_view_member_summary(member.id)
