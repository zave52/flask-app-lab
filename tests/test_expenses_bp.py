import unittest
from datetime import datetime, timezone, timedelta

from app import app, db
from app.expenses.models import Expense, ExpenseCategory
from app.users.models import User


class ExpensesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and database before each test"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['LOGIN_DISABLED'] = False

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        self.test_user = User(username='testuser')
        self.test_user.set_password('testpass')
        db.session.add(self.test_user)

        category1 = ExpenseCategory(
            name='Food',
            description='Groceries'
        )
        category2 = ExpenseCategory(name='Transport', description='Fare')
        db.session.add(category1)
        db.session.add(category2)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        db.session.rollback()
        db.session.close()
        db.drop_all()

        db.engine.dispose()

        self.app_context.pop()

    def login(self):
        """Helper method to simulate user login"""
        return self.client.post(
            '/users/login', data={
                'username': 'testuser',
                'password': 'testpass'
            }, follow_redirects=True
        )

    def test_index_redirect_without_login(self):
        """Test: redirect to login when accessing without authentication"""
        response = self.client.get('/expenses/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_index_with_login(self):
        """Test: access to main page with authentication"""
        self.login()
        response = self.client.get('/expenses/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b'expenses' in response.data or b'expense' in response.data.lower()
        )

    def test_create_expense_get(self):
        """Test: display expense creation form"""
        self.login()
        response = self.client.get('/expenses/create')
        self.assertEqual(response.status_code, 200)

    def test_create_expense_post(self):
        """Test: create new expense via POST"""
        self.login()
        category = ExpenseCategory.query.first()

        data = {
            'title': 'Test Expense',
            'description': 'Test expense description',
            'amount': 100.50,
            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'category_id': category.id
        }

        response = self.client.post(
            '/expenses/create',
            data=data,
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

        expense = Expense.query.filter_by(title='Test Expense').first()
        self.assertIsNotNone(expense)
        self.assertEqual(expense.amount, 100.50)
        self.assertEqual(expense.owner_username, 'testuser')

    def test_expense_detail(self):
        """Test: display detailed expense information"""
        self.login()
        category = ExpenseCategory.query.first()
        expense = Expense(
            title='Test',
            description='Description',
            amount=50.0,
            date=datetime.now(timezone.utc),
            category_id=category.id,
            owner_username='testuser'
        )
        db.session.add(expense)
        db.session.commit()
        expense_id = expense.id

        response = self.client.get(f'/expenses/{expense_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Test' in response.data or b'Test' in response.data)

    def test_edit_expense_own(self):
        """Test: edit own expense"""
        self.login()
        category = ExpenseCategory.query.first()
        expense = Expense(
            title='Old Title',
            description='Old Description',
            amount=75.0,
            date=datetime.now(timezone.utc),
            category_id=category.id,
            owner_username='testuser'
        )
        db.session.add(expense)
        db.session.commit()
        expense_id = expense.id

        data = {
            'title': 'New Title',
            'description': 'New Description',
            'amount': 100.0,
            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'category_id': category.id
        }

        response = self.client.post(
            f'/expenses/{expense_id}/edit',
            data=data,
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

        expense = db.session.get(Expense, expense_id)
        self.assertEqual(expense.title, 'New Title')
        self.assertEqual(expense.amount, 100.0)

    def test_edit_expense_not_owner(self):
        """Test: prevent editing someone else's expense"""
        self.login()
        category = ExpenseCategory.query.first()
        expense = Expense(
            title='Other User Expense',
            description='Description',
            amount=50.0,
            date=datetime.now(timezone.utc),
            category_id=category.id,
            owner_username='otheruser'
        )
        db.session.add(expense)
        db.session.commit()
        expense_id = expense.id

        data = {
            'title': 'Attempted Change',
            'description': 'No permission',
            'amount': 999.0,
            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'category_id': category.id
        }

        response = self.client.post(
            f'/expenses/{expense_id}/edit',
            data=data,
            follow_redirects=True
        )

        expense = db.session.get(Expense, expense_id)
        self.assertEqual(expense.title, 'Other User Expense')
        self.assertEqual(expense.amount, 50.0)

    def test_delete_expense_own(self):
        """Test: delete own expense"""
        self.login()
        category = ExpenseCategory.query.first()
        expense = Expense(
            title='To be deleted',
            description='Will be deleted',
            amount=25.0,
            date=datetime.now(timezone.utc),
            category_id=category.id,
            owner_username='testuser'
        )
        db.session.add(expense)
        db.session.commit()
        expense_id = expense.id

        response = self.client.post(
            f'/expenses/{expense_id}/delete',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

        expense = db.session.get(Expense, expense_id)
        self.assertIsNone(expense)

    def test_delete_expense_not_owner(self):
        """Test: prevent deleting someone else's expense"""
        self.login()
        category = ExpenseCategory.query.first()
        expense = Expense(
            title='Other User Expense',
            description='Will not be deleted',
            amount=50.0,
            date=datetime.now(timezone.utc),
            category_id=category.id,
            owner_username='otheruser'
        )
        db.session.add(expense)
        db.session.commit()
        expense_id = expense.id

        response = self.client.post(
            f'/expenses/{expense_id}/delete',
            follow_redirects=True
        )

        expense = db.session.get(Expense, expense_id)
        self.assertIsNotNone(expense)
        self.assertEqual(expense.title, 'Other User Expense')

    def test_search_expenses(self):
        """Test: search expenses by title"""
        self.login()
        category = ExpenseCategory.query.first()
        expense1 = Expense(
            title='Grocery Purchase',
            amount=100.0,
            date=datetime.now(timezone.utc),
            category_id=category.id,
            owner_username='testuser'
        )
        expense2 = Expense(
            title='Transport Payment',
            amount=50.0,
            date=datetime.now(timezone.utc),
            category_id=category.id,
            owner_username='testuser'
        )
        db.session.add(expense1)
        db.session.add(expense2)
        db.session.commit()

        response = self.client.get('/expenses/?search=grocery')
        self.assertEqual(response.status_code, 200)

    def test_sort_expenses(self):
        """Test: sort expenses"""
        self.login()
        category = ExpenseCategory.query.first()

        for i in range(3):
            expense = Expense(
                title=f'Expense {i}',
                amount=100.0 * (i + 1),
                date=datetime.now(timezone.utc) - timedelta(days=i),
                category_id=category.id,
                owner_username='testuser'
            )
            db.session.add(expense)
        db.session.commit()

        response = self.client.get('/expenses/?sort_by=date&order=desc')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/expenses/?sort_by=amount&order=asc')
        self.assertEqual(response.status_code, 200)

    def test_categories_page(self):
        """Test: categories page"""
        self.login()
        response = self.client.get('/expenses/categories')
        self.assertEqual(response.status_code, 200)

    def test_my_expenses_page(self):
        """Test: "My expenses" page"""
        self.login()
        response = self.client.get('/expenses/my-expenses')
        self.assertEqual(response.status_code, 200)

    def test_expense_category_relationship(self):
        """Test: relationship between expenses and categories"""
        self.login()
        category = ExpenseCategory.query.filter_by(name='Food').first()

        expense = Expense(
            title='Test relationship',
            amount=150.0,
            date=datetime.now(timezone.utc),
            category_id=category.id,
            owner_username='testuser'
        )
        db.session.add(expense)
        db.session.commit()

        self.assertEqual(expense.category.name, 'Food')
        self.assertIn(expense, category.expenses)


if __name__ == '__main__':
    unittest.main(verbosity=2)
