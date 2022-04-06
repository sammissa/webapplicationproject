from django.urls import path
from application import views
from application.models import Ticket


tickets_list_view = views.TicketListView.as_view(
    queryset=Ticket.objects.order_by("-created")[:5],  # :5 limits the results to the five most recent
    context_object_name="ticket_list",
    template_name="application/tickets.html",
)

urlpatterns = [
    path("", tickets_list_view, name="tickets"),
    path("tickets/", tickets_list_view, name="tickets"),
    path("ticket-form/", views.create_ticket, name="ticket-form"),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
]