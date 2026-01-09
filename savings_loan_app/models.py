"""
Database models for the Member Savings and Loan Scheme Management System.

This module defines all database tables and their relationships using SQLAlchemy ORM.
Note: The db instance is imported from app module to avoid circular imports.
"""

from datetime import datetime, date
from decimal import Decimal

# Import db from app - this will be set up in app.py
# We'll handle this import properly in app.py
def init_models(db_instance):
    """Initialize models with the database instance from app."""
    global db
    db = db_instance
    return db

# Temporary placeholder - will be replaced when imported in app.py
try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
except:
    db = None


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
