from datetime import datetime, timezone

from flask import (
    request,
    redirect,
    url_for,
    render_template,
    flash,
    session,
    abort
)

from sqlalchemy import select, func, desc, asc, literal_column

from app import db
from . import expenses_bp
from .forms import ExpenseForm, SearchForm
from .models import Expense, ExpenseCategory


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to continue', 'warning')
            return redirect(url_for('users_bp.login'))
        return f(*args, **kwargs)

    return decorated_function


@expenses_bp.route('/')
@login_required
def index():
    search_form = SearchForm()

    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'date')
    order = request.args.get('order', 'desc')

    stmt = select(Expense)

    if search_query:
        stmt = stmt.where(Expense.title.ilike(f'%{search_query}%'))

    if sort_by == 'date':
        stmt = stmt.order_by(
            Expense.date.desc() if order == 'desc' else Expense.date.asc()
        )
    elif sort_by == 'amount':
        stmt = stmt.order_by(
            Expense.amount.desc() if order == 'desc' else Expense.amount.asc()
        )
    elif sort_by == 'title':
        stmt = stmt.order_by(
            Expense.title.desc() if order == 'desc' else Expense.title.asc()
        )

    expenses = db.session.execute(stmt).scalars().all()

    total_amount = sum(expense.amount for expense in expenses)

    return render_template(
        'expenses/index.html',
        expenses=expenses,
        search_form=search_form,
        search_query=search_query,
        sort_by=sort_by,
        order=order,
        total_amount=total_amount
    )


@expenses_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ExpenseForm()

    categories = db.session.execute(
        select(ExpenseCategory).order_by(ExpenseCategory.name)
    ).scalars().all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if not categories:
        flash('Please create expense categories first', 'warning')
        return redirect(url_for('expenses_bp.index'))

    if form.validate_on_submit():
        expense = Expense(
            title=form.title.data,
            description=form.description.data,
            amount=form.amount.data,
            date=datetime.combine(form.date.data, datetime.min.time()),
            category_id=form.category_id.data,
            owner_username=session['username']
        )

        db.session.add(expense)
        db.session.commit()

        flash('Expense created successfully!', 'success')
        return redirect(url_for('expenses_bp.detail', id=expense.id))

    return render_template('expenses/create.html', form=form)


@expenses_bp.route('/<int:id>')
@login_required
def detail(id):
    expense = db.session.get(Expense, id)
    if expense is None:
        abort(404)

    is_owner = session['username'] == expense.owner_username

    return render_template(
        'expenses/detail.html',
        expense=expense,
        is_owner=is_owner
    )


@expenses_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    expense = db.session.get(Expense, id)
    if expense is None:
        abort(404)

    if session['username'] != expense.owner_username:
        flash('You do not have permission to edit this expense', 'error')
        return redirect(url_for('expenses_bp.detail', id=id))

    form = ExpenseForm(obj=expense)

    categories = db.session.execute(
        select(ExpenseCategory).order_by(ExpenseCategory.name)
    ).scalars().all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        expense.title = form.title.data
        expense.description = form.description.data
        expense.amount = form.amount.data
        expense.date = datetime.combine(form.date.data, datetime.min.time())
        expense.category_id = form.category_id.data
        expense.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses_bp.detail', id=expense.id))

    if request.method == 'GET':
        form.date.data = expense.date.date()

    return render_template('expenses/edit.html', form=form, expense=expense)


@expenses_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    expense = db.session.get(Expense, id)
    if expense is None:
        abort(404)

    if session['username'] != expense.owner_username:
        flash('You do not have permission to delete this expense', 'error')
        return redirect(url_for('expenses_bp.detail', id=id))

    db.session.delete(expense)
    db.session.commit()

    flash('Expense deleted successfully!', 'info')
    return redirect(url_for('expenses_bp.index'))


@expenses_bp.route('/categories')
@login_required
def categories():
    categories = db.session.execute(
        select(ExpenseCategory).order_by(ExpenseCategory.name)
    ).scalars().all()

    categories_with_counts = []
    for category in categories:
        count = db.session.execute(
            select(func.count()).select_from(Expense).where(
                Expense.category_id == category.id
                )
        ).scalar() or 0
        total = db.session.execute(
            select(
                func.coalesce(func.sum(Expense.amount), literal_column("0"))
            ).select_from(Expense).where(Expense.category_id == category.id)
        ).scalar() or 0
        categories_with_counts.append(
            {
                'category': category,
                'count': int(count),
                'total': float(total)
            }
        )

    return render_template(
        'expenses/categories.html',
        categories=categories_with_counts
    )


@expenses_bp.route('/my-expenses')
@login_required
def my_expenses():
    username = session['username']

    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'date')
    order = request.args.get('order', 'desc')

    stmt = select(Expense).where(Expense.owner_username == username)

    if search_query:
        stmt = stmt.where(Expense.title.ilike(f'%{search_query}%'))

    if sort_by == 'date':
        stmt = stmt.order_by(
            Expense.date.desc() if order == 'desc' else Expense.date.asc()
        )
    elif sort_by == 'amount':
        stmt = stmt.order_by(
            Expense.amount.desc() if order == 'desc' else Expense.amount.asc()
        )
    elif sort_by == 'title':
        stmt = stmt.order_by(
            Expense.title.desc() if order == 'desc' else Expense.title.asc()
        )

    expenses = db.session.execute(stmt).scalars().all()
    total_amount = sum(expense.amount for expense in expenses)

    search_form = SearchForm()

    return render_template(
        'expenses/my_expenses.html',
        expenses=expenses,
        search_form=search_form,
        search_query=search_query,
        sort_by=sort_by,
        order=order,
        total_amount=total_amount
    )
