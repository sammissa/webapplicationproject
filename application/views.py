from django.contrib.auth import login, authenticate, get_user, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import ListView
from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required
from application.models import Ticket, Engineer
from application.forms import CreateTicketForm, RegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin


def register_request(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            engineer = Engineer()
            engineer.name = "{} {}".format(user.first_name, user.last_name)
            engineer.save()
            return redirect("tickets")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = RegisterForm()
    return render(request=request, template_name="application/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("tickets")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="application/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    return redirect("login")


class TicketListView(LoginRequiredMixin, ListView):
    login_url = "login"
    """Renders the home page, with a list of all messages."""
    model = Ticket

    def get_context_data(self, **kwargs):
        context = super(TicketListView, self).get_context_data(**kwargs)
        return context


@login_required(login_url="login")
def create_ticket(request):
    form = CreateTicketForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created = timezone.now()
            user = get_user(request)
            ticket.reporter = user
            ticket.save()
            return redirect("tickets")
    else:
        return render(request, "application/ticket_form.html", {"form": form})
