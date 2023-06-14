"""
References:
    TicketListView based on 'HomeListView', create_ticket_request and set_on_call_request based on 'log_message'
    in 'use the database through the models' section of Django tutorial:

    Visual Studio Code (no date) [online] Python and Django tutorial in Visual Studio Code. Available at:
    https://code.visualstudio.com/docs/python/tutorial-django (Accessed: 13 April 2022).

    TicketDeleteView based on 'DeleteView' in Django documentation:

    Django (no date) [online] Generic editing views | Django documentation. Available at:
    https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-editing/#django.views.generic.edit.DeleteView
    (Accessed: 20 April 2022).

    register_request and login_request based on 'add register/login functions to views' sections of:

    Ordinary Coders (2020) [online] A Guide to User Registration, Login, and Logout in Django. Available at:
    https://ordinarycoders.com/blog/article/django-user-register-login-logout (Accessed: 13 April 2022).

    edit_ticket_request based on Stack overflow comment:

    Roseman, D. (2018) [online] Django, how to include pre-existing data in update form view, Stack Overflow.
    Available at: https://stackoverflow.com/a/52494854 (Accessed: 19 April 2022).
"""
import logging

from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView

from application.forms import TicketCreationForm, EngineerUserCreationForm, OnCallChangeForm, TicketChangeForm
from application.models import Ticket, EngineerUser

# Static message strings
REGISTRATION_SUCCESSFUL = "Registration was successful."
REGISTRATION_UNSUCCESSFUL = "Registration was unsuccessful."
INVALID_CREDENTIALS = "Invalid username or password."
INVALID_FORM = "Invalid form."
LOGGED_IN = "You are now logged in."
LOGGED_OUT = "You are now logged out."
TICKET_MISSING = "Ticket does not exist."

logger = logging.getLogger()


class TicketListView(LoginRequiredMixin, ListView):
    login_url = "login"
    model = Ticket
    context_object_name = "ticket_list"

    def get_context_data(self, **kwargs):
        context = super(TicketListView, self).get_context_data(**kwargs)
        context["on_call"] = EngineerUser.objects.filter(is_on_call=True)
        return context

    def get_queryset(self):
        if self.request.path == "/user_tickets/":
            user = get_user(self.request)
            return Ticket.objects.filter(reporter=user)
        return Ticket.objects.all()


class TicketDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "user.is_superuser"
    model = Ticket
    context_object_name = "delete_ticket_form"

    def get_success_url(self):
        ticket = self.get_object()
        message = f"Ticket deleted: [{ticket.title}]."
        messages.info(self.request, message)
        logger.info(message, extra={'username': self.request.user.username})
        return reverse_lazy("tickets")


def home_request(request):
    return render(request=request, template_name="application/home.html")


def register_request(request):
    form = EngineerUserCreationForm(request.POST or None)
    if request.method == "POST":
        form = EngineerUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, REGISTRATION_SUCCESSFUL)
            logger.info(REGISTRATION_SUCCESSFUL, extra={'username': user.username})
            return redirect("tickets")
        messages.error(request, REGISTRATION_UNSUCCESSFUL)
        logger.error(REGISTRATION_UNSUCCESSFUL)
    return render(request=request, template_name="application/register.html", context={"register_form": form})


def login_request(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, LOGGED_IN)
                logger.info(LOGGED_IN, extra={'username': username})
                return redirect("tickets")
        messages.error(request, INVALID_CREDENTIALS)
        logger.error(INVALID_CREDENTIALS)
    return render(request=request, template_name="application/login.html", context={"login_form": form})


@login_required(login_url="login")
def logout_request(request):
    logout(request)
    messages.info(request, LOGGED_OUT)
    logger.info(LOGGED_OUT, extra={'username': request.user.username})
    return redirect("login")


@login_required(login_url="login")
def create_ticket_request(request):
    form = TicketCreationForm(request.POST or None, user=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            message = f"Ticket created: [{form.cleaned_data['title']}]."
            messages.info(request, message)
            logger.info(message, extra={'username': request.user.username})
            return redirect("tickets")
        messages.error(request, INVALID_FORM)
        logger.error(INVALID_FORM, extra={'username': request.user.username})
    return render(request=request, template_name="application/ticket_form.html", context={"ticket_form": form})


@login_required(login_url="login")
def edit_ticket_request(request, pk):
    try:
        instance = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        messages.error(request, TICKET_MISSING)
        logger.exception(TICKET_MISSING, extra={'username': request.user.username})
        return render(request=request, template_name="application/tickets.html")
    form = TicketChangeForm(data=request.POST or None, instance=instance, user=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            message = f"Ticket updated: [{instance.title}]."
            messages.info(request, message)
            logger.info(message, extra={'username': request.user.username})
            return redirect("tickets")
        messages.error(request, INVALID_FORM)
        logger.error(INVALID_FORM, extra={'username': request.user.username})
    return render(request=request, template_name="application/edit_ticket_form.html",
                  context={"edit_ticket_form": form, "instance": instance})


@login_required(login_url="login")
def set_on_call_request(request):
    form = OnCallChangeForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            engineer_id = form.cleaned_data.get("engineer").id
            EngineerUser.objects.filter(is_on_call=True).update(is_on_call=False)
            engineer = EngineerUser.objects.get(pk=engineer_id)
            engineer.is_on_call = True
            engineer.save(update_fields=["is_on_call"])
            message = f"On call changed to: {engineer}."
            messages.info(request, message)
            logger.info(message, extra={'username': request.user.username})
            return redirect("tickets")
    return render(request=request, template_name="application/set_on_call.html", context={"set_on_call": form})
