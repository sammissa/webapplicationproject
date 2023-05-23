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
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator, EmailValidator
from django.utils.html import escape

from application.models import Engineer, Ticket


class CreateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("title", "priority", "description", "status")

    def clean_title(self):
        return clean_field(self, field_name="title")

    def clean_description(self):
        return clean_field(self, field_name="description")


class EditTicketForm(forms.ModelForm):
    title = forms.CharField(disabled=True)
    created = forms.DateTimeField(disabled=True)

    class Meta:
        model = Ticket
        fields = ("title", "created", "priority", "description", "status")

    def clean_description(self):
        return clean_field(self, field_name="description")


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
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2", "is_superuser")

    def clean_first_name(self):
        return clean_field(self, field_name="first_name")

    def clean_last_name(self):
        return clean_field(self, field_name="last_name")

    def clean_email(self):
        return clean_field(self, field_name="email")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        engineer = Engineer()
        engineer.name = user.get_full_name()
        if commit:
            engineer.save()
            user.save()
        return user


class SetOnCallForm(forms.Form):
    engineer = forms.ModelChoiceField(
        label="Engineer Choices", queryset=Engineer.objects.all(), required=True)


def clean_field(self, field_name):
    field_value = self.cleaned_data.get(field_name)
    if field_value and '<script>' in field_value:
        self.add_error(field_name, f'Invalid {field_name.replace("_", " ")}')

    # Perform HTML escaping on the field value
    field_value = escape(field_value)

    return field_value
