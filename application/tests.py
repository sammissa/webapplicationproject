"""
References:
    TicketCreationFormTestCase, EngineerUserCreationFormTestCase, and OnCallChangeFormTestCase based on tests in 'Forms'
    section and ViewsTestCase based on 'Views' section of:

    MDN Contributors (2022) [online] Django Tutorial Part 10.
    Available at: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing (Accessed: 14 April 2022).

    EngineerUserTestCase and TicketTestCase were based on the following:

    Django (no date) [online] Writing and running tests | Django documentation.
    Available at: https://docs.djangoproject.com/en/4.0/topics/testing/overview/ (Accessed: 13 April 2022).

    Message response testing based on Stack overflow answer:

    Moppag (2017) [online] python - How can I unit test django messages?, Stack Overflow.
    Available at: https://stackoverflow.com/a/46865530 (Accessed: 21 April 2022).
"""
import logging

from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from pytz import UTC

from application import views, forms
from application.admin import TicketAdmin
from application.forms import EngineerUserCreationForm, OnCallChangeForm, TicketCreationForm, TicketChangeForm
from application.models import EngineerUser, Ticket
from logger.models import CustomStatusLog

# Test values for Register form fields
FIRST_NAME = "John"
LAST_NAME = "Smith"
EMAIL = "user@qa.com"
USERNAME = "user"
PASSWORD = "123Password789!"

# Test values for Ticket form fields
TITLE = "Test Title"
PRIORITY = Ticket.Priority.LOW
DESCRIPTION = "Test Description"
STATUS = Ticket.Status.TD
TIME = timezone.datetime(year=2023, month=1, day=1, tzinfo=UTC)

# Malicious input for XSS tests
XSS_INPUT = '<script>alert("XSS attack");</script>'

# Malicious input for SQL injection tests
SQL_INPUT = "'; DROP TABLE EngineerUser; --"


class CustomTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create user
        EngineerUser.objects.create_user(username=USERNAME,
                                         email=EMAIL,
                                         password=PASSWORD,
                                         first_name=FIRST_NAME,
                                         last_name=LAST_NAME)

        # Create admin user
        EngineerUser.objects.create_superuser(username="admin",
                                              email="admin@qa.com",
                                              password=PASSWORD,
                                              first_name="Admin",
                                              last_name="User",
                                              is_on_call=True)


class EngineerUserTestCase(CustomTestCase):
    def test_engineer_user(self):
        user = EngineerUser.objects.create_user(username="testuser",
                                                email="testuser@qa.com",
                                                password=PASSWORD,
                                                first_name="test",
                                                last_name="user")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@qa.com")
        self.assertEqual(user.get_full_name(), "test user")
        self.assertEqual(user.is_on_call, False)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_staff, False)

        # Assert that the password is correctly hashed
        self.assertTrue(check_password(PASSWORD, user.password))

    def test_admin_engineer_user(self):
        admin_user = EngineerUser.objects.create_superuser(username="testadmin",
                                                           email="testadmin@qa.com",
                                                           password=PASSWORD,
                                                           first_name="test",
                                                           last_name="admin",
                                                           is_on_call=True)

        self.assertEqual(admin_user.username, "testadmin")
        self.assertEqual(admin_user.email, "testadmin@qa.com")
        self.assertEqual(admin_user.get_full_name(), "test admin")
        self.assertEqual(admin_user.is_on_call, True)
        self.assertEqual(admin_user.is_superuser, True)
        self.assertEqual(admin_user.is_staff, True)

        # Assert that the password is correctly hashed
        self.assertTrue(check_password(PASSWORD, admin_user.password))


class EngineerUserCreationFormTestCase(CustomTestCase):
    def test_empty_form_is_not_valid(self):
        form = EngineerUserCreationForm()

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_first_name(self):
        form = EngineerUserCreationForm(data={"last_name": LAST_NAME,
                                              "username": USERNAME,
                                              "email": EMAIL,
                                              "password1": PASSWORD,
                                              "password2": PASSWORD})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_last_name(self):
        form = EngineerUserCreationForm(data={"first_name": FIRST_NAME,
                                              "username": USERNAME,
                                              "email": EMAIL,
                                              "password1": PASSWORD,
                                              "password2": PASSWORD})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_username(self):
        form = EngineerUserCreationForm(data={"first_name": FIRST_NAME,
                                              "last_name": LAST_NAME,
                                              "email": EMAIL,
                                              "password1": PASSWORD,
                                              "password2": PASSWORD})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_email(self):
        form = EngineerUserCreationForm(data={"first_name": FIRST_NAME,
                                              "last_name": LAST_NAME,
                                              "username": USERNAME,
                                              "password1": PASSWORD,
                                              "password2": PASSWORD})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_password1(self):
        form = EngineerUserCreationForm(data={"first_name": FIRST_NAME,
                                              "last_name": LAST_NAME,
                                              "username": USERNAME,
                                              "email": EMAIL,
                                              "password2": PASSWORD})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_password2(self):
        form = EngineerUserCreationForm(data={"first_name": FIRST_NAME,
                                              "last_name": LAST_NAME,
                                              "username": USERNAME,
                                              "email": EMAIL,
                                              "password1": PASSWORD})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_matching_passwords(self):
        form = EngineerUserCreationForm(data={"first_name": FIRST_NAME,
                                              "last_name": LAST_NAME,
                                              "username": USERNAME,
                                              "email": EMAIL,
                                              "password1": PASSWORD,
                                              "password2": "123testpassword"})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        form = EngineerUserCreationForm(data={"first_name": FIRST_NAME,
                                              "last_name": LAST_NAME,
                                              "username": "Test",
                                              "email": "test@qa.com",
                                              "password1": PASSWORD,
                                              "password2": PASSWORD})

        self.assertTrue(form.is_valid())

    def test_form_first_name_against_xss(self):
        form = EngineerUserCreationForm(data={"first_name": XSS_INPUT,
                                              "last_name": LAST_NAME,
                                              "username": USERNAME,
                                              "email": EMAIL,
                                              "password1": PASSWORD,
                                              "password2": PASSWORD})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the title field in the form has a validation error
        self.assertTrue('first_name' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid first name'
        self.assertEqual(form.errors['first_name'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.XSS_MSG)

    def test_form_first_name_against_sql_injection(self):
        form = EngineerUserCreationForm(data={"first_name": SQL_INPUT,
                                              "last_name": LAST_NAME,
                                              "username": USERNAME,
                                              "email": EMAIL,
                                              "password1": PASSWORD,
                                              "password2": PASSWORD})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the title field in the form has a validation error
        self.assertTrue('first_name' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid first name'
        self.assertEqual(form.errors['first_name'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.SQL_MSG)

    def test_form_last_name_against_xss(self):
        form = EngineerUserCreationForm(data={"first_name": FIRST_NAME,
                                              "last_name": XSS_INPUT,
                                              "username": USERNAME,
                                              "email": EMAIL,
                                              "password1": PASSWORD,
                                              "password2": PASSWORD})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the title field in the form has a validation error
        self.assertTrue('last_name' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid last name'
        self.assertEqual(form.errors['last_name'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.XSS_MSG)

    def test_form_last_name_against_sql_injection(self):
        form = EngineerUserCreationForm(data={"first_name": FIRST_NAME,
                                              "last_name": SQL_INPUT,
                                              "username": USERNAME,
                                              "email": EMAIL,
                                              "password1": PASSWORD,
                                              "password2": PASSWORD})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the title field in the form has a validation error
        self.assertTrue('last_name' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid last name'
        self.assertEqual(form.errors['last_name'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.SQL_MSG)


class EngineerUserAdminTestCase(CustomTestCase):
    def test_save_model(self):
        user = EngineerUser.objects.get(pk=1)
        admin_user = EngineerUser.objects.get(pk=2)
        self.assertEqual(user.is_on_call, False)
        self.assertEqual(admin_user.is_on_call, True)

        self.client.login(username='admin', password=PASSWORD)
        change_url = reverse('admin:application_engineeruser_change', args=[user.id])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)

        updated_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_on_call': True,
            '_save': 'Save',
        }
        response = self.client.post(change_url, updated_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check that the user's on call status has been updated
        updated_user = EngineerUser.objects.get(pk=user.id)
        self.assertEqual(updated_user.is_on_call, True)

        # Check that the admin user's on call status has been updated
        updated_admin_user = EngineerUser.objects.get(pk=admin_user.id)
        self.assertEqual(updated_admin_user.is_on_call, False)

    def test_save_model_first_name_against_xss(self):
        user = EngineerUser.objects.get(pk=1)
        admin_user = EngineerUser.objects.get(pk=2)
        self.assertEqual(user.is_on_call, False)
        self.assertEqual(admin_user.is_on_call, True)

        self.client.login(username='admin', password=PASSWORD)
        change_url = reverse('admin:application_engineeruser_change', args=[user.id])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)

        updated_data = {
            'username': user.username,
            'email': user.email,
            'first_name': XSS_INPUT,
            'last_name': user.last_name,
            'is_on_call': False,
            '_save': 'Save',
        }
        response = self.client.post(change_url, updated_data, follow=True)
        self.assertEqual(response.status_code, 200)

        updated_user = EngineerUser.objects.get(pk=user.id)
        self.assertEqual(updated_user.first_name, user.first_name)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.XSS_MSG)

    def test_save_model_first_name_against_sql_injection(self):
        user = EngineerUser.objects.get(pk=1)
        admin_user = EngineerUser.objects.get(pk=2)
        self.assertEqual(user.is_on_call, False)
        self.assertEqual(admin_user.is_on_call, True)

        self.client.login(username='admin', password=PASSWORD)
        change_url = reverse('admin:application_engineeruser_change', args=[user.id])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)

        updated_data = {
            'username': user.username,
            'email': user.email,
            'first_name': SQL_INPUT,
            'last_name': user.last_name,
            'is_on_call': False,
            '_save': 'Save',
        }
        response = self.client.post(change_url, updated_data, follow=True)
        self.assertEqual(response.status_code, 200)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.SQL_MSG)

    def test_save_model_last_name_against_xss(self):
        user = EngineerUser.objects.get(pk=1)
        admin_user = EngineerUser.objects.get(pk=2)
        self.assertEqual(user.is_on_call, False)
        self.assertEqual(admin_user.is_on_call, True)

        self.client.login(username='admin', password=PASSWORD)
        change_url = reverse('admin:application_engineeruser_change', args=[user.id])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)

        updated_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': XSS_INPUT,
            'is_on_call': False,
            '_save': 'Save',
        }
        response = self.client.post(change_url, updated_data, follow=True)
        self.assertEqual(response.status_code, 200)

        updated_user = EngineerUser.objects.get(pk=user.id)
        self.assertEqual(updated_user.last_name, user.last_name)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.XSS_MSG)

    def test_save_model_last_name_against_sql_injection(self):
        user = EngineerUser.objects.get(pk=1)
        admin_user = EngineerUser.objects.get(pk=2)
        self.assertEqual(user.is_on_call, False)
        self.assertEqual(admin_user.is_on_call, True)

        self.client.login(username='admin', password=PASSWORD)
        change_url = reverse('admin:application_engineeruser_change', args=[user.id])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)

        updated_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': SQL_INPUT,
            'is_on_call': False,
            '_save': 'Save',
        }
        response = self.client.post(change_url, updated_data, follow=True)
        self.assertEqual(response.status_code, 200)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.SQL_MSG)


class TicketTestCase(CustomTestCase):
    def test_ticket(self):
        user = EngineerUser.objects.get(pk=1)
        ticket = Ticket.objects.create(title=TITLE,
                                       created=TIME,
                                       priority=PRIORITY,
                                       description=DESCRIPTION,
                                       status=STATUS,
                                       reporter=user)

        self.assertEqual(ticket.title, TITLE)
        self.assertEqual(ticket.created, TIME)
        self.assertEqual(ticket.priority, PRIORITY)
        self.assertEqual(ticket.description, DESCRIPTION)
        self.assertEqual(ticket.status, STATUS)
        self.assertEqual(ticket.reporter.get_full_name(), "John Smith")
        self.assertEqual(ticket.reporter.is_on_call, False)


class TicketCreationFormTestCase(CustomTestCase):
    def test_empty_form_is_not_valid(self):
        form = TicketCreationForm()

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_title(self):
        form = TicketCreationForm(
            data={"priority": PRIORITY, "description": DESCRIPTION, "status": STATUS})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_description(self):
        form = TicketCreationForm(data={"title": TITLE, "priority": PRIORITY, "status": STATUS})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_priority(self):
        form = TicketCreationForm(data={"title": TITLE,
                                        "description": DESCRIPTION,
                                        "status": STATUS})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        form = TicketCreationForm(data={"title": TITLE,
                                        "priority": PRIORITY,
                                        "description": DESCRIPTION,
                                        "status": STATUS})

        self.assertTrue(form.is_valid())

    def test_form_is_not_valid_if_title_exists(self):
        user = EngineerUser.objects.get(pk=1)
        Ticket.objects.create(title=TITLE,
                              created=TIME,
                              priority=PRIORITY,
                              description=DESCRIPTION,
                              status=STATUS,
                              reporter=user)

        form = TicketCreationForm(data={"title": TITLE,
                                        "priority": PRIORITY,
                                        "description": DESCRIPTION,
                                        "status": STATUS,
                                        "reporter": user})

        self.assertFalse(form.is_valid())

    def test_form_title_against_xss(self):
        form = TicketCreationForm(data={"title": XSS_INPUT,
                                        "priority": PRIORITY,
                                        "description": DESCRIPTION,
                                        "status": STATUS})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the title field in the form has a validation error
        self.assertTrue('title' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid title'
        self.assertEqual(form.errors['title'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.XSS_MSG)

    def test_form_title_against_sql_injection(self):
        form = TicketCreationForm(data={"title": SQL_INPUT,
                                        "priority": PRIORITY,
                                        "description": DESCRIPTION,
                                        "status": STATUS})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the title field in the form has a validation error
        self.assertTrue('title' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid title'
        self.assertEqual(form.errors['title'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.SQL_MSG)

    def test_form_description_against_xss(self):
        form = TicketCreationForm(data={"title": TITLE,
                                        "priority": PRIORITY,
                                        "description": XSS_INPUT,
                                        "status": STATUS})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the description field in the form has a validation error
        self.assertTrue('description' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid description'
        self.assertEqual(form.errors['description'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.XSS_MSG)

    def test_form_description_against_sql_injection(self):
        form = TicketCreationForm(data={"title": TITLE,
                                        "priority": PRIORITY,
                                        "description": SQL_INPUT,
                                        "status": STATUS})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the description field in the form has a validation error
        self.assertTrue('description' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid description'
        self.assertEqual(form.errors['description'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.SQL_MSG)


class TicketChangeFormTestCase(CustomTestCase):
    def test_form_is_not_valid_without_description(self):
        user = EngineerUser.objects.get(pk=1)
        ticket = Ticket.objects.create(title=TITLE,
                                       created=TIME,
                                       priority=PRIORITY,
                                       description=DESCRIPTION,
                                       status=STATUS,
                                       reporter=user)
        form = TicketChangeForm(instance=ticket, data={"priority": PRIORITY, "status": STATUS})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        user = EngineerUser.objects.get(pk=1)
        ticket = Ticket.objects.create(title=TITLE,
                                       created=TIME,
                                       priority=PRIORITY,
                                       description=DESCRIPTION,
                                       status=STATUS,
                                       reporter=user)
        form = TicketChangeForm(instance=ticket, data={"priority": PRIORITY,
                                                       "description": "New Description",
                                                       "status": STATUS})

        self.assertTrue(form.is_valid())

    def test_form_description_against_xss(self):
        user = EngineerUser.objects.get(pk=1)
        ticket = Ticket.objects.create(title=TITLE,
                                       created=TIME,
                                       priority=PRIORITY,
                                       description=DESCRIPTION,
                                       status=STATUS,
                                       reporter=user)
        form = TicketChangeForm(instance=ticket, data={"priority": PRIORITY,
                                                       "description": XSS_INPUT,
                                                       "status": STATUS})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the description field in the form has a validation error
        self.assertTrue('description' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid description'
        self.assertEqual(form.errors['description'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.XSS_MSG)

    def test_form_description_against_sql_injection(self):
        user = EngineerUser.objects.get(pk=1)
        ticket = Ticket.objects.create(title=TITLE,
                                       created=TIME,
                                       priority=PRIORITY,
                                       description=DESCRIPTION,
                                       status=STATUS,
                                       reporter=user)
        form = TicketChangeForm(instance=ticket, data={"priority": PRIORITY,
                                                       "description": SQL_INPUT,
                                                       "status": STATUS})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the description field in the form has a validation error
        self.assertTrue('description' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid description'
        self.assertEqual(form.errors['description'][0], expected_error_message)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.SQL_MSG)


class TicketAdminTestCase(CustomTestCase):
    def test_get_form(self):
        request_factory = RequestFactory()
        request = request_factory.get('/admin/application/ticket/add/')
        ticket_admin = TicketAdmin(Ticket, AdminSite())

        form = ticket_admin.get_form(request, obj=None)
        self.assertTrue(issubclass(form, TicketCreationForm))

        user = EngineerUser.objects.get(pk=1)
        ticket = Ticket.objects.create(title=TITLE,
                                       created=TIME,
                                       priority=PRIORITY,
                                       description=DESCRIPTION,
                                       status=STATUS,
                                       reporter=user)

        form = ticket_admin.get_form(request, obj=ticket)
        self.assertTrue(issubclass(form, TicketChangeForm))

    def test_save_model(self):
        admin_user = EngineerUser.objects.get(pk=2)
        self.client.login(username='admin', password=PASSWORD)
        data = {
            'title': 'test title',
            'priority': PRIORITY,
            'description': DESCRIPTION,
            'status': STATUS
        }

        self.client.post('/admin/application/ticket/add/', data=data)
        ticket = Ticket.objects.get(title='test title')

        self.assertEqual(ticket.title, 'test title')
        self.assertEqual(ticket.priority, PRIORITY)
        self.assertEqual(ticket.reporter, admin_user)
        self.assertIsNotNone(ticket.created)
        self.assertEqual(ticket.created.date(), timezone.now().date())


class OnCallChangeFormTestCase(CustomTestCase):
    def test_form_is_not_valid_without_choice(self):
        form = OnCallChangeForm()

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_when_choice_is_not_valid(self):
        form = OnCallChangeForm(data={"engineer": 3})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        form = OnCallChangeForm(data={"engineer": 1})

        self.assertTrue(form.is_valid())


class ViewsTestCase(CustomTestCase):
    def test_home_view(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/home.html")

    def test_register_view(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/register.html")

    def test_register_with_valid_details(self):
        response = self.client.post(reverse("register"), data={
            "username": "register",
            "first_name": "reg",
            "last_name": "ister",
            "email": "register@test.com",
            "password1": "567SEAreg!",
            "password2": "567SEAreg!",
            "is_superuser": False
        })
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(views.REGISTRATION_SUCCESSFUL, messages)
        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 3)

        log_entry = CustomStatusLog.objects.get(level=logging.INFO)
        self.assertEqual(log_entry.msg, views.REGISTRATION_SUCCESSFUL)

    def test_register_with_invalid_details(self):
        response = self.client.post(reverse("register"), data={})
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(views.REGISTRATION_UNSUCCESSFUL, messages)

        log_entry = CustomStatusLog.objects.get(level=logging.ERROR)
        self.assertEqual(log_entry.msg, views.REGISTRATION_UNSUCCESSFUL)

    def test_login_view(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/login.html")

    def test_login_with_valid_details(self):
        response = self.login_helper()
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(views.LOGGED_IN, messages)

        log_entry = CustomStatusLog.objects.get(level=logging.INFO)
        self.assertEqual(log_entry.msg, views.LOGGED_IN)

    def test_login_with_invalid_details(self):
        response = self.client.post(reverse("login"), data={})
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Invalid username or password.", messages)

        log_entry = CustomStatusLog.objects.get(level=logging.ERROR)
        self.assertEqual(log_entry.msg, views.INVALID_CREDENTIALS)

    def test_logout(self):
        self.login_helper()
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("You are now logged out.", messages)

        log_entry = CustomStatusLog.objects.get(msg=views.LOGGED_OUT)
        self.assertEqual(log_entry.level, logging.INFO)

    def test_create_ticket_view(self):
        response = self.client.get("/ticket_form/")
        self.assertEqual(response.status_code, 302)

        self.login_helper()
        response = self.client.get("/ticket_form/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/ticket_form.html")

    def test_create_ticket_with_valid_details(self):
        self.login_helper()
        response = self.client.post(reverse("ticket_form"), data={
            "title": "Title",
            "priority": PRIORITY,
            "description": DESCRIPTION,
            "status": STATUS
        })
        self.assertEqual(response.status_code, 302)
        expected_message = "Ticket created: [Title]."
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(expected_message, messages)

        log_entry = CustomStatusLog.objects.get(msg=expected_message)
        self.assertEqual(log_entry.level, logging.INFO)

    def test_create_ticket_with_invalid_details(self):
        self.login_helper()
        response = self.client.post(reverse("ticket_form"), data={})
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(views.INVALID_FORM, messages)

        log_entry = CustomStatusLog.objects.get(level=logging.ERROR)
        self.assertEqual(log_entry.msg, views.INVALID_FORM)

    def test_set_on_call_view(self):
        response = self.client.get("/set_on_call/")
        self.assertEqual(response.status_code, 302)

        self.login_helper()
        response = self.client.get("/set_on_call/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/set_on_call.html")

    def test_set_on_call(self):
        self.login_helper()
        engineer = EngineerUser.objects.get(pk=1)
        self.assertFalse(engineer.is_on_call)
        response = self.client.post(reverse("set_on_call"), data={
            "engineer": engineer.pk
        })
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        message = "On call changed: [John Smith]."
        self.assertIn(message, messages)
        engineer = EngineerUser.objects.get(pk=1)
        self.assertTrue(engineer.is_on_call)

        log_entry = CustomStatusLog.objects.get(msg=message)
        self.assertEqual(log_entry.level, logging.INFO)

    def test_tickets_view(self):
        user = EngineerUser.objects.get(pk=1)
        Ticket.objects.create(title=TITLE,
                              created=TIME,
                              priority=PRIORITY,
                              description=DESCRIPTION,
                              status=STATUS,
                              reporter=user)

        response = self.client.get("/tickets/")
        self.assertEqual(response.status_code, 302)

        self.login_helper()
        response = self.client.get("/tickets/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/tickets.html")

        self.assertTrue("ticket_list" in response.context)
        self.assertTrue("on_call" in response.context)

        ticket_list = response.context["ticket_list"]
        self.assertEqual(len(ticket_list), 1)

        ticket = ticket_list[0]
        self.assertEqual(TITLE, ticket.title)

        on_call = response.context["on_call"]
        self.assertEqual(len(on_call), 1)
        self.assertEqual("Admin User", on_call[0].get_full_name())

    def test_user_tickets_view(self):
        response = self.client.get("/user_tickets/")
        self.assertEqual(response.status_code, 302)

        self.login_helper()
        response = self.client.get("/user_tickets/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/user_tickets.html")

    def test_edit_ticket_view(self):
        user = EngineerUser.objects.get(pk=1)
        Ticket.objects.create(title=TITLE,
                              created=TIME,
                              priority=PRIORITY,
                              description=DESCRIPTION,
                              status=STATUS,
                              reporter=user)

        self.login_helper()
        response = self.client.get("/tickets/")
        self.assertEqual(response.status_code, 200)

        ticket_list = response.context["ticket_list"]
        ticket = ticket_list[0]
        response = self.client.get(reverse("edit_ticket", args=(ticket.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/edit_ticket_form.html")
        self.assertTrue("instance" in response.context)
        instance = response.context["instance"]
        self.assertEqual(TITLE, instance.title)
        response = self.client.post(reverse("edit_ticket", args=(ticket.id,)), data={
            "priority": Ticket.Priority.MED,
            "description": "Edited Description",
            "status": Ticket.Status.IP,

        })
        self.assertEqual(response.status_code, 302)
        expected_message = "Ticket updated: [Test Title]."
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(expected_message, messages)

        response = self.client.get(reverse("tickets"))
        edited_ticket_list = response.context["ticket_list"]
        edited_ticket = edited_ticket_list[0]
        self.assertEqual(Ticket.Priority.MED, edited_ticket.priority)
        self.assertEqual("Edited Description", edited_ticket.description)
        self.assertEqual(Ticket.Status.IP, edited_ticket.status)

        log_entry = CustomStatusLog.objects.get(msg=expected_message)
        self.assertEqual(log_entry.level, logging.INFO)

    def test_edit_ticket_view_on_invalid_ticket_id(self):
        self.login_helper()
        response = self.client.get("/tickets/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("edit_ticket", args=(0,)))
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(views.TICKET_MISSING, messages)

        log_entry = CustomStatusLog.objects.get(level=logging.ERROR)
        self.assertEqual(log_entry.msg, views.TICKET_MISSING)

    def test_edit_ticket_view_against_xss(self):
        user = EngineerUser.objects.get(pk=1)
        Ticket.objects.create(title=TITLE,
                              created=TIME,
                              priority=PRIORITY,
                              description=DESCRIPTION,
                              status=STATUS,
                              reporter=user)

        self.login_helper()
        response = self.client.get("/tickets/")
        self.assertEqual(response.status_code, 200)

        ticket_list = response.context["ticket_list"]
        ticket = ticket_list[0]
        response = self.client.get(reverse("edit_ticket", args=(ticket.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/edit_ticket_form.html")
        self.assertTrue("instance" in response.context)
        instance = response.context["instance"]
        self.assertEqual(TITLE, instance.title)
        response = self.client.post(reverse("edit_ticket", args=(ticket.id,)), data={
            "priority": Ticket.Priority.MED,
            "description": XSS_INPUT,
            "status": Ticket.Status.IP,

        })
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(views.INVALID_FORM, messages)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.XSS_MSG)

    def test_edit_ticket_view_against_sql_injection(self):
        user = EngineerUser.objects.get(pk=1)
        Ticket.objects.create(title=TITLE,
                              created=TIME,
                              priority=PRIORITY,
                              description=DESCRIPTION,
                              status=STATUS,
                              reporter=user)

        self.login_helper()
        response = self.client.get("/tickets/")
        self.assertEqual(response.status_code, 200)

        ticket_list = response.context["ticket_list"]
        ticket = ticket_list[0]
        response = self.client.get(reverse("edit_ticket", args=(ticket.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/edit_ticket_form.html")
        self.assertTrue("instance" in response.context)
        instance = response.context["instance"]
        self.assertEqual(TITLE, instance.title)
        response = self.client.post(reverse("edit_ticket", args=(ticket.id,)), data={
            "priority": Ticket.Priority.MED,
            "description": SQL_INPUT,
            "status": Ticket.Status.IP,

        })
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(views.INVALID_FORM, messages)

        log_entry = CustomStatusLog.objects.get(level=logging.WARNING)
        self.assertEqual(log_entry.msg, forms.SQL_MSG)

    def test_delete_ticket_view(self):
        user = EngineerUser.objects.get(pk=1)
        Ticket.objects.create(title=TITLE,
                              created=TIME,
                              priority=PRIORITY,
                              description=DESCRIPTION,
                              status=STATUS,
                              reporter=user)

        self.client.post(reverse("login"), data={
            "username": "admin",
            "password": PASSWORD
        })
        response = self.client.get("/tickets/")
        self.assertEqual(response.status_code, 200)

        ticket_list = response.context["ticket_list"]
        ticket = ticket_list[0]
        response = self.client.get(reverse("delete_ticket", args=(ticket.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/delete_ticket_form.html")
        self.assertTrue("delete_ticket_form" in response.context)

        response = self.client.post(reverse("delete_ticket", args=(ticket.id,)))
        self.assertEqual(response.status_code, 302)
        expected_message = "Ticket deleted: [Test Title]."
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(expected_message, messages)

        response = self.client.get(reverse("tickets"))
        ticket_list = response.context["ticket_list"]
        self.assertEqual(len(ticket_list), 0)

        log_entry = CustomStatusLog.objects.get(msg=expected_message)
        self.assertEqual(log_entry.level, logging.INFO)

    def login_helper(self):
        response = self.client.post(reverse("login"), data={
            "username": USERNAME,
            "password": PASSWORD
        })

        return response
