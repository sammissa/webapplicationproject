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

from application.models import Engineer, Ticket


class CreateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("title", "priority", "description", "status")


class EditTicketForm(forms.ModelForm):
    title = forms.CharField(disabled=True)
    created = forms.DateTimeField(disabled=True)

    class Meta:
        model = Ticket
        fields = ("title", "created", "priority", "description", "status")


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Register'))

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2", "is_superuser")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        engineer = Engineer()
        engineer.name = user.get_full_name()
        if commit:
            engineer.save()
            user.save()
        return user


class SetOnCallForm(forms.Form):
    engineer = forms.ModelChoiceField(
        label="Engineer Choices", queryset=Engineer.objects.all(), required=True)
