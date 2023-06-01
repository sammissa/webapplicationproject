"""
References:
    CreateTicketFormTestCase, RegisterFormTestCase, and SetOnCallFormTestCase based on tests in 'Forms' section and
    ViewsTestCase based on 'Views' section of:

    MDN Contributors (2022) [online] Django Tutorial Part 10. Available at:
    https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing (Accessed: 14 April 2022).

    EngineerTestCase and TicketTestCase were based on the following:

    Django (no date) [online] Writing and running tests | Django documentation. Available at:
    https://docs.djangoproject.com/en/4.0/topics/testing/overview/ (Accessed: 13 April 2022).

    Message response testing based on Stack overflow answer:

    Moppag (2017) [online] python - How can I unit test django messages?, Stack Overflow. Available at:
    https://stackoverflow.com/a/46865530 (Accessed: 21 April 2022).
"""
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from pytz import UTC

from application.forms import CreateTicketForm, EditTicketForm, RegisterForm, SetOnCallForm
from application.models import EngineerUser, Ticket


class CustomTestCase(TestCase):
    def setUp(self):
        # Test values for Register form fields
        self.first_name = "John"
        self.last_name = "Smith"
        self.email = "user@qa.com"
        self.username = "user"
        self.password = "123Password789!"

        # Test values for Ticket form fields
        self.title = "Test Title"
        self.priority = Ticket.Priority.LOW
        self.description = "Test Description"
        self.status = Ticket.Status.TD
        self.time = timezone.datetime(year=2023, month=1, day=1, tzinfo=UTC)

        # Malicious input for XSS tests
        self.malicious_input = '<script>alert("XSS attack");</script>'

        # Create user
        user = EngineerUser.objects.create_user(username=self.username,
                                                email=self.email,
                                                password=self.password,
                                                first_name=self.first_name,
                                                last_name=self.last_name)

        # Create admin user
        EngineerUser.objects.create_superuser(username="admin",
                                              email="admin@qa.com",
                                              password=self.password,
                                              first_name="Admin",
                                              last_name="User",
                                              is_on_call=True)

        # Create ticket
        Ticket.objects.create(title=self.title,
                              created=self.time,
                              priority=self.priority,
                              description=self.description,
                              status=self.status,
                              reporter=user)


class CreateTicketFormTestCase(CustomTestCase):
    def test_empty_form_is_not_valid(self):
        form = CreateTicketForm()

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_title(self):
        form = CreateTicketForm(
            data={"priority": self.priority, "description": self.description, "status": self.status})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_description(self):
        form = CreateTicketForm(data={"title": self.title, "priority": self.priority, "status": self.status})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_priority(self):
        form = CreateTicketForm(data={"title": self.title,
                                      "description": self.description,
                                      "status": self.status})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        form = CreateTicketForm(data={"title": "Title",
                                      "priority": self.priority,
                                      "description": self.description,
                                      "status": self.status})

        self.assertTrue(form.is_valid())

    def test_form_is_not_valid_if_title_exists(self):
        reporter = EngineerUser.objects.get(pk=1)
        form = CreateTicketForm(data={"title": self.title,
                                      "priority": self.priority,
                                      "description": self.description,
                                      "status": self.status,
                                      "reporter": reporter})

        self.assertFalse(form.is_valid())

    def test_form_title_against_xss(self):
        form = CreateTicketForm(data={"title": self.malicious_input,
                                      "priority": self.priority,
                                      "description": self.description,
                                      "status": self.status})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the title field in the form has a validation error
        self.assertTrue('title' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid title'
        self.assertEqual(form.errors['title'][0], expected_error_message)

    def test_form_description_against_xss(self):
        form = CreateTicketForm(data={"title": self.title,
                                      "priority": self.priority,
                                      "description": self.malicious_input,
                                      "status": self.status})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the description field in the form has a validation error
        self.assertTrue('description' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid description'
        self.assertEqual(form.errors['description'][0], expected_error_message)


class EditTicketFormTestCase(CustomTestCase):
    def test_form_is_not_valid_without_description(self):
        ticket = Ticket.objects.get(pk=1)
        form = EditTicketForm(instance=ticket, data={"priority": self.priority, "status": self.status})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        ticket = Ticket.objects.get(pk=1)
        form = EditTicketForm(instance=ticket, data={"priority": self.priority,
                                                     "description": "New Description",
                                                     "status": self.status})

        self.assertTrue(form.is_valid())

    def test_form_description_against_xss(self):
        ticket = Ticket.objects.get(pk=1)
        form = EditTicketForm(instance=ticket, data={"priority": self.priority,
                                                     "description": self.malicious_input,
                                                     "status": self.status})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the description field in the form has a validation error
        self.assertTrue('description' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid description'
        self.assertEqual(form.errors['description'][0], expected_error_message)


class RegisterFormTestCase(CustomTestCase):
    def test_empty_form_is_not_valid(self):
        form = RegisterForm()

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_first_name(self):
        form = RegisterForm(data={"last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_last_name(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_username(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_email(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "password1": self.password,
                                  "password2": self.password})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_password1(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password2": self.password})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_password2(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_matching_passwords(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": "123testpassword"})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": "Test",
                                  "email": "test@qa.com",
                                  "password1": self.password,
                                  "password2": self.password})

        self.assertTrue(form.is_valid())

    def test_form_first_name_against_xss(self):
        form = RegisterForm(data={"first_name": self.malicious_input,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the title field in the form has a validation error
        self.assertTrue('first_name' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid first name'
        self.assertEqual(form.errors['first_name'][0], expected_error_message)

    def test_form_last_name_against_xss(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.malicious_input,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password})

        # Check that the form is not valid
        self.assertFalse(form.is_valid())

        # Check that the title field in the form has a validation error
        self.assertTrue('last_name' in form.errors)

        # Check that the error message is as expected
        expected_error_message = 'Invalid last name'
        self.assertEqual(form.errors['last_name'][0], expected_error_message)


class SetOnCallFormTestCase(CustomTestCase):
    def test_form_is_not_valid_without_choice(self):
        form = SetOnCallForm()

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_when_choice_is_not_valid(self):
        form = SetOnCallForm(data={"engineer": 3})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        form = SetOnCallForm(data={"engineer": 1})

        self.assertTrue(form.is_valid())


class TicketTestCase(CustomTestCase):
    def test_ticket(self):
        ticket = Ticket.objects.get(pk=1)

        self.assertEqual(ticket.title, self.title)
        self.assertEqual(ticket.created, self.time)
        self.assertEqual(ticket.priority, self.priority)
        self.assertEqual(ticket.description, self.description)
        self.assertEqual(ticket.status, self.status)
        self.assertEqual(ticket.reporter.get_full_name(), "John Smith")
        self.assertEqual(ticket.reporter.is_on_call, False)


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
        self.assertIn("Registration successful.", messages)
        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 3)

    def test_register_with_invalid_details(self):
        response = self.client.post(reverse("register"), data={})
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Unsuccessful registration. Invalid information.", messages)

    def test_login_view(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "application/login.html")

    def test_login_with_valid_details(self):
        response = self.login_helper()
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("You are now logged in as user.", messages)

    def test_login_with_invalid_details(self):
        response = self.client.post(reverse("login"), data={})
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Invalid username or password.", messages)

    def test_logout(self):
        self.login_helper()
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("You are now logged out.", messages)

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
            "priority": self.priority,
            "description": self.description,
            "status": self.status
        })
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Ticket: [Title] has been added.", messages)

    def test_create_ticket_with_invalid_details(self):
        self.login_helper()
        response = self.client.post(reverse("ticket_form"), data={})
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Form is not valid.", messages)

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
        self.assertIn("On call changed to: John Smith.", messages)
        engineer = EngineerUser.objects.get(pk=1)
        self.assertTrue(engineer.is_on_call)

    def test_tickets_view(self):
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
        self.assertEqual(self.title, ticket.title)

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
        self.assertEqual(self.title, instance.title)
        response = self.client.post(reverse("edit_ticket", args=(ticket.id,)), data={
            "priority": Ticket.Priority.MED,
            "description": "Edited Description",
            "status": Ticket.Status.IP,

        })
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Ticket updated successfully.", messages)

        response = self.client.get(reverse("tickets"))
        edited_ticket_list = response.context["ticket_list"]
        edited_ticket = edited_ticket_list[0]
        self.assertEqual(Ticket.Priority.MED, edited_ticket.priority)
        self.assertEqual("Edited Description", edited_ticket.description)
        self.assertEqual(Ticket.Status.IP, edited_ticket.status)

    def test_delete_ticket_view(self):
        self.client.post(reverse("login"), data={
            "username": "admin",
            "password": self.password
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
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Ticket deleted successfully.", messages)

        response = self.client.get(reverse("tickets"))
        ticket_list = response.context["ticket_list"]
        self.assertEqual(len(ticket_list), 0)

    def login_helper(self):
        response = self.client.post(reverse("login"), data={
            "username": self.username,
            "password": self.password
        })

        return response
