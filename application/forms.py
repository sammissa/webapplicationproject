"""
References:
    EngineerUserCreationForm class is based on 'create the register form' found at:

    Ordinary Coders (2020) [online] A Guide to User Registration, Login, and Logout in Django.
    Available at: https://ordinarycoders.com/blog/article/django-user-register-login-logout (Accessed: 13 April 2022).

    EngineerUserCreationForm __init__ is based on code in 'fundamentals' section of django crispy forms documentation:

    Araujo, M. (2021) [online] django-crispy-forms Documentation.
    Available at: https://readthedocs.org/projects/django-crispy-forms/downloads/pdf/latest/ (Accessed: 13 April 2022).

    EngineerUserChangeForm class is based on 'CustomUserChangeForm' found at:

    Learn Django (2022) [online] Django Best Practices: Custom User Model.
    Available at: https://learndjango.com/tutorials/django-custom-user-model (Accessed: 20 June 2023).

    TicketCreationForm class is based on 'LogMessageForm' in 'use the database through the models' section of Django
    tutorial found at:

    Visual Studio Code (no date) [online] Python and Django tutorial in Visual Studio Code.
    Available at: https://code.visualstudio.com/docs/python/tutorial-django (Accessed: 13 April 2022).

    OnCallChangeForm class is based on the comment by Chad on Stack Overflow:

    Chad (2021) [online] ‘Django dropdown menu/form based on model entries’, Stack Overflow.
    Available at: https://stackoverflow.com/questions/66655712/django-dropdown-menu-form-based-on-model-entries
    (Accessed: 13 April 2022).
"""
import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
from django.utils.html import escape

from application.models import Ticket, EngineerUser

XSS_MSG = 'Cross-Site Scripting attempt detected'
SQL_MSG = 'SQL Injection attempt detected'

logger = logging.getLogger()


class EngineerUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(50)
        ]
    )
    last_name = forms.CharField(
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(50)
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Register'))

    class Meta:
        model = EngineerUser
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()
        cleaned_first_name = clean_field(self, cleaned_data, "first_name")
        cleaned_last_name = clean_field(self, cleaned_data, "last_name")
        cleaned_data["first_name"] = cleaned_first_name
        cleaned_data["last_name"] = cleaned_last_name

        return cleaned_data


class EngineerUserChangeForm(UserChangeForm):
    first_name = forms.CharField(
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(50)
        ]
    )
    last_name = forms.CharField(
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(50)
        ]
    )

    class Meta:
        model = EngineerUser
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        cleaned_first_name = clean_field(self, cleaned_data, "first_name")
        cleaned_last_name = clean_field(self, cleaned_data, "last_name")
        cleaned_data["first_name"] = cleaned_first_name
        cleaned_data["last_name"] = cleaned_last_name

        return cleaned_data


class TicketCreationForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("title", "priority", "description", "status")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TicketCreationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_title = clean_field(self, cleaned_data, "title", self.user)
        cleaned_description = clean_field(self, cleaned_data, "description", self.user)
        cleaned_data["title"] = cleaned_title
        cleaned_data["description"] = cleaned_description

        return cleaned_data

    def save(self, commit=True):
        ticket = super().save(commit=False)
        ticket.created = timezone.now()
        ticket.reporter = self.user

        if commit:
            ticket.save()

        return ticket


class TicketChangeForm(forms.ModelForm):
    title = forms.CharField(disabled=True)
    created = forms.DateTimeField(disabled=True)

    class Meta:
        model = Ticket
        fields = ("title", "created", "priority", "description", "status")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TicketChangeForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_description = clean_field(self, cleaned_data, "description", self.user)
        cleaned_data["description"] = cleaned_description

        return cleaned_data


class OnCallChangeForm(forms.Form):
    engineer = forms.ModelChoiceField(
        label="Engineer Choices", queryset=EngineerUser.objects.all(), required=True)


def clean_field(self, cleaned_data, field_name, user=None):
    field_data = cleaned_data.get(field_name)

    if field_data:
        is_sql_injection = sql_injection_check(field_data, user)
        is_cross_site_scripting = cross_site_scripting_check(field_data, user)
        if is_sql_injection or is_cross_site_scripting:
            self.add_error(field_name, f'Invalid {field_name.replace("_", " ")}')

    field_data = escape(field_data)

    return field_data


def sql_injection_check(input_string, user):
    sql_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "SELECT"]

    for keyword in sql_keywords:
        if keyword in input_string:
            logger.warning(SQL_MSG, extra={'username': get_username(user)})
            return True
    return False


def cross_site_scripting_check(input_string, user):
    if '<script>' in input_string:
        logger.warning(XSS_MSG, extra={'username': get_username(user)})
        return True
    return False


def get_username(user):
    if user:
        return user.username
    return "Anonymous"
