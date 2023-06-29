"""
References:
    urlpatterns was based on 'create a django app' section, ticket_list_view and user_ticket_list_view were based on
    'use the database through the models' section:

    Visual Studio Code (no date) [online] Python and Django tutorial in Visual Studio Code.
    Available at: https://code.visualstudio.com/docs/python/tutorial-django (Accessed: 13 April 2022).

    edit_ticket_request url based on section 1 in:

    Dev 2 Qa (2019) [online] ‘How To Pass Parameters To View Via Url In Django’.
    Available at: https://www.dev2qa.com/how-to-pass-parameters-to-view-via-url-in-django/ (Accessed: 19 April 2022).
"""
from django.urls import path

from application import views

ticket_list_view = views.TicketListView.as_view(template_name="application/tickets.html")
user_ticket_list_view = views.TicketListView.as_view(template_name="application/user_tickets.html")
delete_ticket_list_view = views.TicketDeleteView.as_view(template_name="application/delete_ticket_form.html")

urlpatterns = [
    path("", views.home_request, name="home"),
    path("tickets/", ticket_list_view, name="tickets"),
    path('tickets/update/<int:pk>/', views.edit_ticket_request, name="edit_ticket"),
    path('tickets/delete/<int:pk>/', delete_ticket_list_view, name="delete_ticket"),
    path("user_tickets/", user_ticket_list_view, name="user_tickets"),
    path("set_on_call/", views.set_on_call_request, name="set_on_call"),
    path("ticket_form/", views.create_ticket_request, name="ticket_form"),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
]
