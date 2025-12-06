from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    FloatField,
    DateField,
    SelectField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ExpenseForm(FlaskForm):
    title = StringField(
        'Expense Title',
        validators=[
            DataRequired(message='This field is required'),
            Length(
                min=3,
                max=200,
                message='Title must be between 3 and 200 characters'
            )
        ]
    )

    description = TextAreaField(
        'Description',
        validators=[
            Optional(),
            Length(
                max=1000,
                message='Description cannot exceed 1000 characters'
            )
        ]
    )

    amount = FloatField(
        'Amount (UAH)',
        validators=[
            DataRequired(message='This field is required'),
            NumberRange(min=0.01, message='Amount must be greater than 0')
        ]
    )

    date = DateField(
        'Expense Date',
        format='%Y-%m-%d',
        default=date.today,
        validators=[DataRequired(message='This field is required')]
    )

    category_id = SelectField(
        'Category',
        coerce=int,
        validators=[DataRequired(message='Select a category')]
    )

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)


class SearchForm(FlaskForm):
    search = StringField(
        'Search by title',
        validators=[Optional()]
    )
