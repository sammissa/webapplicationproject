"""
References:
    CreateTicketForm based on 'LogMessageForm' in 'use the database through the models' section of Django tutorial:

    Visual Studio Code (no date) [online] Python and Django tutorial in Visual Studio Code. Available at:
    https://code.visualstudio.com/docs/python/tutorial-django (Accessed: 13 April 2022).

    RegisterForm based on 'create the register form' found at:

    Ordinary Coders (2020) [online] A Guide to User Registration, Login, and Logout in Django. Available at:
    https://ordinarycoders.com/blog/article/django-user-register-login-logout (Accessed: 13 April 2022).

    RegisterForm __init__ based on code in 'fundamentals' section of django crispy forms documentation:

    Araujo, M. (2021) [online] django-crispy-forms Documentation. Available at:
    https://readthedocs.org/projects/django-crispy-forms/downloads/pdf/latest/ (Accessed: 13 April 2022).

    SetOnCallForm based on the comment by Chad on Stack Overflow:

    Chad (2021) [online] ‘Django dropdown menu/form based on model entries’, Stack Overflow. Available at:
    https://stackoverflow.com/questions/66655712/django-dropdown-menu-form-based-on-model-entries
    (Accessed: 13 April 2022).
"""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinLengthValidator, MaxLengthValidator, EmailValidator
from django.utils.html import escape

from application.models import Ticket, EngineerUser


class CreateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("title", "priority", "description", "status")

    def clean(self):
        cleaned_data = super().clean()
        cleaned_title = clean_field(self, "title")
        cleaned_description = clean_field(self, "description")
        cleaned_data["title"] = cleaned_title
        cleaned_data["description"] = cleaned_description

        return cleaned_data


class EditTicketForm(forms.ModelForm):
    title = forms.CharField(disabled=True)
    created = forms.DateTimeField(disabled=True)

    class Meta:
        model = Ticket
        fields = ("title", "created", "priority", "description", "status")

    def clean(self):
        cleaned_data = super().clean()
        cleaned_description = clean_field(self, "description")
        cleaned_data["description"] = cleaned_description

        return cleaned_data


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(50)
        ]
    )
    last_name = forms.CharField(
        required=True,
        validators=[
            MinLengthValidator(2),
            MaxLengthValidator(50)
        ]
    )
    email = forms.EmailField(
        required=True,
        validators=[
            EmailValidator()
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
        cleaned_first_name = clean_field(self, "first_name")
        cleaned_last_name = clean_field(self, "last_name")
        cleaned_email = clean_field(self, "email")
        cleaned_data["first_name"] = cleaned_first_name
        cleaned_data["last_name"] = cleaned_last_name
        cleaned_data["email"] = cleaned_email

        return cleaned_data


class SetOnCallForm(forms.Form):
    engineer = forms.ModelChoiceField(
        label="Engineer Choices", queryset=EngineerUser.objects.all(), required=True)


def clean_field(self, field_name):
    field_data = self.cleaned_data.get(field_name)
    if field_data and '<script>' in field_data:
        self.add_error(field_name, f'Invalid {field_name.replace("_", " ")}')

    # Perform HTML escaping on the field value
    field_data = escape(field_data)

    return field_data
