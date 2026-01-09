"""
Flask application for Member Savings and Loan Scheme Management System.

This application provides a web-based interface for managing member savings,
loans, payments, and generating reports with CSV export functionality.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from decimal import Decimal
import csv
import io
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///savings_loan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)


# ============================================================================
# DATABASE MODELS
# ============================================================================

class Member(db.Model):
    """
    Member model representing a registered member of the savings and loan scheme.
    
    Attributes:
        id: Primary key
        full_name: Member's full name
        member_id: Unique member identifier
        date_joined: Date when member joined the scheme
        savings_balance: Current savings balance
    """
    
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    member_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_joined = db.Column(db.Date, nullable=False, default=date.today)
    savings_balance = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    
    # Relationships
    savings_transactions = db.relationship('SavingsTransaction', backref='member', lazy=True, cascade='all, delete-orphan')
    loans = db.relationship('Loan', backref='member', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Member {self.member_id}: {self.full_name}>'
    
    def to_dict(self):
        """Convert member instance to dictionary."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'member_id': self.member_id,
            'date_joined': self.date_joined.isoformat(),
            'savings_balance': float(self.savings_balance)
        }


class SavingsTransaction(db.Model):
    """
    Savings transaction model for recording all savings-related transactions.
    
    Attributes:
        id: Primary key
        member_id: Foreign key to Member
        amount: Transaction amount
        transaction_type: Type of transaction (initial_deposit, monthly_subscription, etc.)
        description: Transaction description
        transaction_date: Timestamp of the transaction
    """
    
    __tablename__ = 'savings_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<SavingsTransaction {self.id}: Member {self.member_id}, Amount {self.amount}>'


class Loan(db.Model):
    """
    Loan model representing a loan issued to a member.
    
    Attributes:
        id: Primary key
        member_id: Foreign key to Member
        principal_amount: Original loan amount (before interest)
        interest_rate: Interest rate (e.g., 0.20 for 20%)
        interest_amount: Total interest calculated at issue
        total_amount: Principal + interest
        current_balance: Current outstanding balance (decreases with payments, increases with overdue interest)
        issue_date: Date when loan was issued
        next_due_date: Next payment due date (5th of month)
        is_active: Whether the loan is still active (not fully repaid)
    """
    
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False, index=True)
    principal_amount = db.Column(db.Numeric(10, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 4), nullable=False)  # e.g., 0.2000 for 20%
    interest_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    current_balance = db.Column(db.Numeric(10, 2), nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    next_due_date = db.Column(db.Date, nullable=False, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    
    # Relationships
    loan_transactions = db.relationship('LoanTransaction', backref='loan', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Loan {self.id}: Member {self.member_id}, Balance {self.current_balance}>'
    
    def to_dict(self):
        """Convert loan instance to dictionary."""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'principal_amount': float(self.principal_amount),
            'interest_rate': float(self.interest_rate),
            'interest_amount': float(self.interest_amount),
            'total_amount': float(self.total_amount),
            'current_balance': float(self.current_balance),
            'issue_date': self.issue_date.isoformat(),
            'next_due_date': self.next_due_date.isoformat(),
            'is_active': self.is_active
        }


class LoanTransaction(db.Model):
    """
    Loan transaction model for recording all loan-related transactions.
    
    Attributes:
        id: Primary key
        loan_id: Foreign key to Loan
        amount: Transaction amount
        transaction_type: Type of transaction (loan_issued, repayment, overdue_interest)
        description: Transaction description
        transaction_date: Timestamp of the transaction
    """
    
    __tablename__ = 'loan_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<LoanTransaction {self.id}: Loan {self.loan_id}, Amount {self.amount}, Type {self.transaction_type}>'


# ============================================================================
# BUSINESS RULES CONSTANTS
# ============================================================================

# Constants for business rules
INITIAL_DEPOSIT = Decimal('1000.00')
MONTHLY_SUBSCRIPTION = Decimal('500.00')
LOAN_INTEREST_RATE = Decimal('0.20')  # 20%
LOAN_DUE_DAY = 5  # 5th of every month


# Initialize database tables on startup
def init_db():
    """Create all database tables."""
    with app.app_context():
        db.create_all()


@app.route('/')
def index():
    """Home page displaying dashboard overview."""
    total_members = Member.query.count()
    total_savings = db.session.query(db.func.sum(Member.savings_balance)).scalar() or Decimal('0.00')
    total_loans = db.session.query(db.func.sum(Loan.current_balance)).filter(
        Loan.is_active == True
    ).scalar() or Decimal('0.00')
    
    # Calculate overdue loans
    today = date.today()
    overdue_loans = Loan.query.filter(
        Loan.is_active == True,
        Loan.next_due_date < today
    ).count()
    
    return render_template('index.html', 
                         total_members=total_members,
                         total_savings=total_savings,
                         total_loans=total_loans,
                         overdue_loans=overdue_loans)


@app.route('/members')
def list_members():
    """Display all members."""
    members = Member.query.all()
    today = date.today()
    
    # Get active loans for each member for display
    member_loans = {}
    for member in members:
        active_loan = Loan.query.filter_by(member_id=member.id, is_active=True).first()
        if active_loan:
            member_loans[member.id] = active_loan
    
    return render_template('members.html', members=members, today=today, member_loans=member_loans)


@app.route('/members/new', methods=['GET', 'POST'])
def add_member():
    """Add a new member with initial deposit."""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        member_id = request.form.get('member_id')
        
        # Check if member ID already exists
        if Member.query.filter_by(member_id=member_id).first():
            flash('Member ID already exists. Please use a different ID.', 'error')
            return render_template('add_member.html')
        
        # Create new member
        member = Member(
            full_name=full_name,
            member_id=member_id,
            date_joined=date.today(),
            savings_balance=INITIAL_DEPOSIT
        )
        
        db.session.add(member)
        db.session.flush()  # Flush to get member.id assigned
        
        # Record initial deposit transaction
        savings_transaction = SavingsTransaction(
            member_id=member.id,
            amount=INITIAL_DEPOSIT,
            transaction_type='initial_deposit',
            description=f'Initial deposit of SZL {INITIAL_DEPOSIT}'
        )
        
        db.session.add(savings_transaction)
        db.session.commit()
        
        flash(f'Member {full_name} registered successfully with initial deposit of SZL {INITIAL_DEPOSIT}.', 'success')
        return redirect(url_for('view_member', member_id=member.id))
    
    return render_template('add_member.html')


@app.route('/members/<int:member_id>')
def view_member(member_id):
    """View member details, savings, and loan information."""
    member = Member.query.get_or_404(member_id)
    
    # Get active loan if exists
    active_loan = Loan.query.filter_by(member_id=member_id, is_active=True).first()
    
    # Get all savings transactions
    savings_transactions = SavingsTransaction.query.filter_by(
        member_id=member_id
    ).order_by(SavingsTransaction.transaction_date.desc()).all()
    
    # Get all loan transactions
    loan_transactions = []
    if active_loan:
        loan_transactions = LoanTransaction.query.filter_by(
            loan_id=active_loan.id
        ).order_by(LoanTransaction.transaction_date.desc()).all()
        
        # Check if loan is overdue
        today = date.today()
        if active_loan.next_due_date < today:
            days_overdue = (today - active_loan.next_due_date).days
        else:
            days_overdue = 0
    else:
        days_overdue = 0
    
    return render_template('member_detail.html',
                         member=member,
                         active_loan=active_loan,
                         savings_transactions=savings_transactions,
                         loan_transactions=loan_transactions,
                         days_overdue=days_overdue,
                         INITIAL_DEPOSIT=INITIAL_DEPOSIT,
                         MONTHLY_SUBSCRIPTION=MONTHLY_SUBSCRIPTION)


@app.route('/members/<int:member_id>/savings/pay', methods=['GET', 'POST'])
def pay_savings(member_id):
    """Record a savings payment (monthly subscription)."""
    member = Member.query.get_or_404(member_id)
    
    if request.method == 'POST':
        amount = Decimal(request.form.get('amount', '0'))
        
        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
            return redirect(url_for('pay_savings', member_id=member_id))
        
        # Update member savings balance
        member.savings_balance += amount
        
        # Record transaction
        transaction = SavingsTransaction(
            member_id=member_id,
            amount=amount,
            transaction_type='monthly_subscription',
            description=f'Monthly subscription payment of SZL {amount}'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Savings payment of SZL {amount} recorded successfully.', 'success')
        return redirect(url_for('view_member', member_id=member_id))
    
    return render_template('pay_savings.html', member=member, MONTHLY_SUBSCRIPTION=MONTHLY_SUBSCRIPTION)


@app.route('/members/<int:member_id>/loan/issue', methods=['GET', 'POST'])
def issue_loan(member_id):
    """Issue a new loan to a member."""
    member = Member.query.get_or_404(member_id)
    
    # Check if member already has an active loan
    existing_loan = Loan.query.filter_by(member_id=member_id, is_active=True).first()
    if existing_loan:
        flash('Member already has an active loan. Please settle it first.', 'error')
        return redirect(url_for('view_member', member_id=member_id))
    
    if request.method == 'POST':
        loan_amount = Decimal(request.form.get('loan_amount', '0'))
        
        if loan_amount <= 0:
            flash('Loan amount must be greater than zero.', 'error')
            return redirect(url_for('issue_loan', member_id=member_id))
        
        # Calculate interest (20% of loan amount)
        interest_amount = loan_amount * LOAN_INTEREST_RATE
        total_amount = loan_amount + interest_amount
        
        # Calculate due date (5th of next month)
        today = date.today()
        if today.day <= LOAN_DUE_DAY:
            # If before or on 5th, due date is 5th of this month
            due_date = date(today.year, today.month, LOAN_DUE_DAY)
        else:
            # If after 5th, due date is 5th of next month
            if today.month == 12:
                due_date = date(today.year + 1, 1, LOAN_DUE_DAY)
            else:
                due_date = date(today.year, today.month + 1, LOAN_DUE_DAY)
        
        # Create loan
        loan = Loan(
            member_id=member_id,
            principal_amount=loan_amount,
            interest_rate=LOAN_INTEREST_RATE,
            interest_amount=interest_amount,
            total_amount=total_amount,
            current_balance=total_amount,
            issue_date=date.today(),
            next_due_date=due_date,
            is_active=True
        )
        
        db.session.add(loan)
        db.session.flush()  # Flush to get loan.id assigned
        
        # Record loan transaction
        loan_transaction = LoanTransaction(
            loan_id=loan.id,
            amount=loan_amount,
            transaction_type='loan_issued',
            description=f'Loan issued: Principal SZL {loan_amount}, Interest SZL {interest_amount}'
        )
        
        db.session.add(loan_transaction)
        db.session.commit()
        
        flash(f'Loan of SZL {loan_amount} issued successfully. Total amount due: SZL {total_amount}.', 'success')
        return redirect(url_for('view_member', member_id=member_id))
    
    return render_template('issue_loan.html', member=member)


@app.route('/members/<int:member_id>/loan/repay', methods=['GET', 'POST'])
def repay_loan(member_id):
    """Record a loan repayment."""
    member = Member.query.get_or_404(member_id)
    loan = Loan.query.filter_by(member_id=member_id, is_active=True).first()
    
    if not loan:
        flash('Member has no active loan.', 'error')
        return redirect(url_for('view_member', member_id=member_id))
    
    # Check and apply overdue interest if payment is late
    today = date.today()
    _apply_overdue_interest(loan, today)
    
    if request.method == 'POST':
        payment_amount = Decimal(request.form.get('payment_amount', '0'))
        
        if payment_amount <= 0:
            flash('Payment amount must be greater than zero.', 'error')
            return redirect(url_for('repay_loan', member_id=member_id))
        
        if payment_amount > loan.current_balance:
            flash(f'Payment amount (SZL {payment_amount}) exceeds outstanding balance (SZL {loan.current_balance}).', 'error')
            return redirect(url_for('repay_loan', member_id=member_id))
        
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
        
        # If loan is fully paid, mark as inactive
        if loan.current_balance <= Decimal('0.01'):  # Small tolerance for rounding
            loan.is_active = False
            loan.current_balance = Decimal('0.00')
            flash('Loan fully repaid and closed.', 'success')
        else:
            # Update next due date to 5th of next month
            if today.day <= LOAN_DUE_DAY:
                next_due = date(today.year, today.month, LOAN_DUE_DAY)
            else:
                if today.month == 12:
                    next_due = date(today.year + 1, 1, LOAN_DUE_DAY)
                else:
                    next_due = date(today.year, today.month + 1, LOAN_DUE_DAY)
            loan.next_due_date = next_due
            flash(f'Payment of SZL {payment_amount} recorded. Remaining balance: SZL {loan.current_balance}.', 'success')
        
        db.session.commit()
        return redirect(url_for('view_member', member_id=member_id))
    
    # Calculate days overdue
    today = date.today()
    if loan.next_due_date < today:
        days_overdue = (today - loan.next_due_date).days
    else:
        days_overdue = 0
    
    return render_template('repay_loan.html', member=member, loan=loan, days_overdue=days_overdue)


@app.route('/process_overdue')
def process_overdue():
    """Process overdue interest for all active loans (admin function)."""
    today = date.today()
    overdue_count = 0
    
    active_loans = Loan.query.filter_by(is_active=True).all()
    
    for loan in active_loans:
        if loan.next_due_date < today:
            _apply_overdue_interest(loan, today)
            overdue_count += 1
    
    db.session.commit()
    
    flash(f'Processed overdue interest for {overdue_count} loan(s).', 'success')
    return redirect(url_for('index'))


def _apply_overdue_interest(loan, current_date):
    """
    Apply compound interest for overdue loans.
    
    Interest compounds monthly (20% on remaining balance) if payment is overdue.
    This function should be called before processing any loan-related operations.
    """
    if loan.next_due_date >= current_date:
        return  # Not overdue yet
    
    # Calculate number of months overdue
    months_overdue = ((current_date.year - loan.next_due_date.year) * 12 + 
                      (current_date.month - loan.next_due_date.month))
    
    if months_overdue <= 0:
        return  # Should not happen, but safety check
    
    # Apply compound interest for each overdue month
    original_balance = loan.current_balance
    for month in range(months_overdue):
        # 20% interest on current balance
        interest = loan.current_balance * LOAN_INTEREST_RATE
        loan.current_balance += interest
        
        # Record the interest charge
        transaction = LoanTransaction(
            loan_id=loan.id,
            amount=interest,
            transaction_type='overdue_interest',
            description=f'Overdue interest (month {month + 1}): SZL {interest:.2f}'
        )
        db.session.add(transaction)
    
    # Update next due date to 5th of current or next month
    if current_date.day <= LOAN_DUE_DAY:
        next_due = date(current_date.year, current_date.month, LOAN_DUE_DAY)
    else:
        if current_date.month == 12:
            next_due = date(current_date.year + 1, 1, LOAN_DUE_DAY)
        else:
            next_due = date(current_date.year, current_date.month + 1, LOAN_DUE_DAY)
    
    loan.next_due_date = next_due
    
    # Flash message about interest applied
    total_interest = loan.current_balance - original_balance
    flash(f'Applied overdue interest: SZL {total_interest:.2f} ({months_overdue} month(s) overdue)', 'warning')


@app.route('/export/members/csv')
def export_members_csv():
    """Export all members data to CSV."""
    members = Member.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Member ID', 'Full Name', 'Date Joined', 'Savings Balance', 
                     'Loan Balance', 'Active Loan', 'Loan Issue Date', 'Next Due Date'])
    
    # Write data
    for member in members:
        active_loan = Loan.query.filter_by(member_id=member.id, is_active=True).first()
        writer.writerow([
            member.member_id,
            member.full_name,
            member.date_joined.strftime('%Y-%m-%d'),
            f'{member.savings_balance:.2f}',
            f'{active_loan.current_balance:.2f}' if active_loan else '0.00',
            'Yes' if active_loan else 'No',
            active_loan.issue_date.strftime('%Y-%m-%d') if active_loan else '',
            active_loan.next_due_date.strftime('%Y-%m-%d') if active_loan else ''
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'members_export_{date.today().strftime("%Y%m%d")}.csv'
    )


@app.route('/export/transactions/csv')
def export_transactions_csv():
    """Export all transactions (savings and loans) to CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Member ID', 'Member Name', 'Transaction Type', 
                     'Category', 'Amount', 'Description', 'Loan Balance (if applicable)'])
    
    # Get all savings transactions
    savings_transactions = db.session.query(SavingsTransaction, Member).join(
        Member, SavingsTransaction.member_id == Member.id
    ).order_by(SavingsTransaction.transaction_date.desc()).all()
    
    for trans, member in savings_transactions:
        writer.writerow([
            trans.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            member.member_id,
            member.full_name,
            trans.transaction_type,
            'Savings',
            f'{trans.amount:.2f}',
            trans.description,
            ''
        ])
    
    # Get all loan transactions
    loan_transactions = db.session.query(LoanTransaction, Loan, Member).join(
        Loan, LoanTransaction.loan_id == Loan.id
    ).join(Member, Loan.member_id == Member.id).order_by(
        LoanTransaction.transaction_date.desc()
    ).all()
    
    for trans, loan, member in loan_transactions:
        writer.writerow([
            trans.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            member.member_id,
            member.full_name,
            trans.transaction_type,
            'Loan',
            f'{trans.amount:.2f}',
            trans.description,
            f'{loan.current_balance:.2f}'
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'transactions_export_{date.today().strftime("%Y%m%d")}.csv'
    )


@app.route('/api/members/<int:member_id>/summary')
def member_summary_api(member_id):
    """API endpoint to get member summary as JSON."""
    member = Member.query.get_or_404(member_id)
    active_loan = Loan.query.filter_by(member_id=member_id, is_active=True).first()
    
    return jsonify({
        'member_id': member.member_id,
        'full_name': member.full_name,
        'date_joined': member.date_joined.isoformat(),
        'savings_balance': float(member.savings_balance),
        'loan': {
            'has_active_loan': active_loan is not None,
            'principal_amount': float(active_loan.principal_amount) if active_loan else 0,
            'current_balance': float(active_loan.current_balance) if active_loan else 0,
            'next_due_date': active_loan.next_due_date.isoformat() if active_loan else None,
            'is_overdue': active_loan.next_due_date < date.today() if active_loan else False
        } if active_loan else None
    })


if __name__ == '__main__':
    init_db()  # Create tables on startup
    app.run(debug=True, host='0.0.0.0', port=5000)
