"""
References:
    EngineerUserAdmin class is based on 'CustomUserAdmin' found at:

    Learn Django (2022) [online] Django Best Practices: Custom User Model.
    Available at: https://learndjango.com/tutorials/django-custom-user-model (Accessed: 20 June 2023).

    EngineerUserAdmin save_model is based on 'Ordering Logic' found at:

    Wiles, F. (2018) [online] Keeping Django Models Ordered.
    Available at: https://www.revsys.com/tidbits/keeping-django-model-objects-ordered/ (Accessed: 27 June 2023).

    TicketAdmin class is based on 'PersonAdmin' found at:

    Trudeau, C. (no date) [online] Customize the Django Admin With Python – Real Python.
    Available at: https://realpython.com/customize-django-admin-python/ (Accessed: 20 June 2023).

    TicketAdmin get_form is based on Django UserAdmin 'get_form' found at:

    Django (2023) [online] Django UserAdmin get form method.
    Available at: https://github.com/django/django/blob/main/django/contrib/auth/admin.py#L90 (Accessed: 20 June 2023).
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from application.forms import EngineerUserCreationForm, EngineerUserChangeForm, TicketCreationForm, TicketChangeForm
from application.models import EngineerUser, Ticket


@admin.register(EngineerUser)
class EngineerUserAdmin(UserAdmin):
    """
    Admin panel configuration for EngineerUser model.

    Attributes:
        add_form: Form to add a new EngineerUser instance.
        form: Form to change an existing EngineerUser instance.
        model: The model associated with this admin configuration (EngineerUser).
        list_display (tuple): Fields to display in the list view.
        list_filter (tuple): Fields to use for filtering in the list view.
        fieldsets (tuple): Fieldsets for grouping fields in the change view.
        add_fieldsets (tuple): Fieldsets for grouping fields in the add view.
    """

    add_form = EngineerUserCreationForm
    form = EngineerUserChangeForm
    model = EngineerUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_on_call')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'is_on_call')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'email', 'password1', 'password2',),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Save an EngineerUser instance in the admin panel.

        If the 'is_on_call' status has changed to True, update other users to set it to False.

        Parameters:
            request: The HTTP request object.
            obj: The EngineerUser instance being saved.
            form: The form used for changing the EngineerUser instance.
            change: A boolean indicating if this is a change to an existing instance.

        Returns:
            None
        """
        super().save_model(request, obj, form, change)

        if change and form.instance.is_on_call and not form.initial['is_on_call']:
            EngineerUser.objects.exclude(pk=obj.pk).update(is_on_call=False)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Ticket model.

    Attributes:
        add_form: Form to add a new Ticket instance.
        form: Form to change an existing Ticket instance.
        list_display (tuple): Fields to display in the list view.
        list_filter (tuple): Fields to use for filtering in the list view.
        search_fields (tuple): Fields to use for searching in the list view.
    """

    add_form = TicketCreationForm
    form = TicketChangeForm
    list_display = ('title', 'priority', 'status', 'reporter')
    list_filter = ('priority', 'status', 'reporter')
    search_fields = ('title', 'reporter__first_name', 'reporter__last_name', 'reporter__username')

    def get_form(self, request, obj=None, **kwargs):
        """
        Get the form for adding or changing a Ticket instance.

        Parameters:
            request: The HTTP request object.
            obj: The Ticket instance being changed (or None for adding).

        Returns:
            form: The appropriate form for adding or changing a Ticket instance.
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def save_model(self, request, obj, form, change):
        """
        Save a Ticket instance in the admin panel.

        If this is a new instance, set the reporter to the current user.

        Parameters:
            request: The HTTP request object.
            obj: The Ticket instance being saved.
            form: The form used for changing the Ticket instance.
            change: A boolean indicating if this is a change to an existing instance.

        Returns:
            None
        """
        if not change:
            obj.reporter = request.user

        super().save_model(request, obj, form, change)
