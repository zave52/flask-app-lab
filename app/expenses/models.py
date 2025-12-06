from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        db.String(100),
        nullable=False,
        unique=True
    )
    description: Mapped[Optional[str]] = mapped_column(db.String(255))

    expenses: Mapped[List["Expense"]] = relationship(
        "Expense",
        backref="category",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'


class Expense(db.Model):
    __tablename__ = 'expenses'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(db.Text)
    amount: Mapped[float] = mapped_column(db.Float, nullable=False)
    date: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey('expense_categories.id'),
        nullable=False,
    )

    owner_username: Mapped[str] = mapped_column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Expense {self.title}>'
