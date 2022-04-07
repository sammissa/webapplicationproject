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
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from pytz import UTC

from application.forms import CreateTicketForm, RegisterForm, SetOnCallForm
from application.models import Engineer, Ticket


class CreateTicketFormTestCase(TestCase):
    def setUp(self):
        self.title = "testTitle"
        self.priority = Ticket.Priority.LOW
        self.description = "testDescription"
        self.status = Ticket.Status.TD

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
        form = CreateTicketForm(data={"title": self.title, "description": self.description, "status": self.status})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        form = CreateTicketForm(data={"title": self.title, "priority": self.priority, "description": self.description,
                                      "status": self.status})

        self.assertTrue(form.is_valid())

    def test_form_is_not_valid_if_title_exists(self):
        Engineer.objects.create(name="reporter", is_on_call=True)
        reporter = Engineer.objects.get(name="reporter")
        created = timezone.datetime(year=2022, month=1, day=1, tzinfo=UTC)
        Ticket.objects.create(title="test",
                              created=created,
                              priority=self.priority,
                              description=self.description,
                              status=self.status,
                              reporter=reporter)
        form = CreateTicketForm(
            data={"title": "test", "priority": self.priority, "description": self.description, "status": self.status})

        self.assertFalse(form.is_valid())


class RegisterFormTestCase(TestCase):
    def setUp(self):
        self.first_name = "testFirst"
        self.last_name = "testLast"
        self.username = "testUser"
        self.email = "test@email.com"
        self.password = "123Testpassword"

    def test_empty_form_is_not_valid(self):
        form = RegisterForm()

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_first_name(self):
        form = RegisterForm(data={"last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password,
                                  "is_superuser": False})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_last_name(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password,
                                  "is_superuser": False})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_username(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password,
                                  "is_superuser": False})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_email(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "password1": self.password,
                                  "password2": self.password,
                                  "is_superuser": False})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_password1(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password2": self.password,
                                  "is_superuser": False})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_password2(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "is_superuser": False})

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_without_matching_passwords(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": "123testpassword",
                                  "is_superuser": False})

        self.assertFalse(form.is_valid())

    def test_form_is_valid_without_is_staff(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password})

        self.assertTrue(form.is_valid())

    def test_form_is_valid(self):
        form = RegisterForm(data={"first_name": self.first_name,
                                  "last_name": self.last_name,
                                  "username": self.username,
                                  "email": self.email,
                                  "password1": self.password,
                                  "password2": self.password,
                                  "is_superuser": False})

        self.assertTrue(form.is_valid())


class SetOnCallFormTestCase(TestCase):
    def setUp(self):
        Engineer.objects.create(name="test", is_on_call=False)

    def test_form_is_not_valid_without_choice(self):
        form = SetOnCallForm()

        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_when_choice_is_not_valid(self):
        form = SetOnCallForm(data={"engineer": 2})

        self.assertFalse(form.is_valid())

    def test_form_is_valid(self):
        form = SetOnCallForm(data={"engineer": 1})

        self.assertTrue(form.is_valid())


class EngineerTestCase(TestCase):
    def setUp(self):
        Engineer.objects.create(name="first", is_on_call=True)
        Engineer.objects.create(name="second", is_on_call=False)

    def test_engineer(self):
        first = Engineer.objects.get(name="first")
        second = Engineer.objects.get(name="second")

        self.assertEqual(first.__str__(), "first")
        self.assertEqual(first.is_on_call, True)
        self.assertEqual(second.__str__(), "second")
        self.assertEqual(second.is_on_call, False)


class TicketTestCase(TestCase):
    def setUp(self):
        engineer = Engineer.objects.create(name="reporter", is_on_call=True)
        created = timezone.datetime(year=2022, month=1, day=1, tzinfo=UTC)
        Ticket.objects.create(title="title",
                              created=created,
                              priority=Ticket.Priority.LOW,
                              description="description",
                              status=Ticket.Status.TD,
                              reporter=engineer)

    def test_ticket(self):
        ticket = Ticket.objects.get(title="title")

        self.assertEqual(ticket.title, "title")
        self.assertEqual(ticket.created, timezone.datetime(year=2022, month=1, day=1, tzinfo=UTC))
        self.assertEqual(ticket.priority, Ticket.Priority.LOW)
        self.assertEqual(ticket.description, "description")
        self.assertEqual(ticket.status, Ticket.Status.TD)
        self.assertEqual(ticket.reporter.name, "reporter")
        self.assertEqual(ticket.reporter.is_on_call, True)


class ViewsTestCase(TestCase):
    def setUp(self):
        self.user_name = "user"
        self.user_password = "012SEAview!"
        self.admin_name = "admin"
        self.admin_pass = "901viewSEA!"
        test_user = User.objects.create_user(username=self.user_name,
                                             email="user@test.com",
                                             password=self.user_password,
                                             first_name="first_name",
                                             last_name="last_name",
                                             is_superuser=False)

        test_admin = User.objects.create_user(username=self.admin_name,
                                              email="admin@test.com",
                                              password=self.admin_pass,
                                              first_name="admin_first_name",
                                              last_name="admin_last_name",
                                              is_superuser=True)
        test_user.save()
        test_admin.save()

        engineer = Engineer.objects.create(name="first_name last_name", is_on_call=False)
        admin = Engineer.objects.create(name="admin_first_name admin_last_name", is_on_call=True)
        created = timezone.datetime(year=2022, month=1, day=1, tzinfo=UTC)
        Ticket.objects.create(title="test",
                              created=created,
                              priority=Ticket.Priority.LOW,
                              description="test",
                              status=Ticket.Status.TD,
                              reporter=engineer)

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
        response = self.client.post(reverse("login"), data={
            "username": self.user_name,
            "password": self.user_password
        })
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
            "title": "test title",
            "priority": "L",
            "description": "some description",
            "status": "TD"
        })
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Ticket: [test title] has been added.", messages)

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
        engineer = Engineer.objects.get(pk=1)
        self.assertFalse(engineer.is_on_call)
        response = self.client.post(reverse("set_on_call"), data={
            "engineer": engineer.pk
        })
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("On call changed to: first_name last_name.", messages)
        engineer = Engineer.objects.get(pk=1)
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
        self.assertEqual("test", ticket.title)

        on_call = response.context["on_call"]
        self.assertEqual(len(on_call), 1)
        self.assertEqual("admin_first_name admin_last_name", on_call[0].name)

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
        self.assertEqual("test", instance.title)
        response = self.client.post(reverse("edit_ticket", args=(ticket.id,)), data={
            "priority": Ticket.Priority.MED,
            "description": "edited",
            "status": Ticket.Status.IP,

        })
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Ticket updated successfully.", messages)

        response = self.client.get(reverse("tickets"))
        edited_ticket_list = response.context["ticket_list"]
        edited_ticket = edited_ticket_list[0]
        self.assertEqual(Ticket.Priority.MED, edited_ticket.priority)
        self.assertEqual("edited", edited_ticket.description)
        self.assertEqual(Ticket.Status.IP, edited_ticket.status)

    def test_delete_ticket_view(self):
        self.client.post(reverse("login"), data={
            "username": self.admin_name,
            "password": self.admin_pass
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

    """Helper function for login"""
    def login_helper(self):
        self.client.post(reverse("login"), data={
            "username": self.user_name,
            "password": self.user_password
        })
