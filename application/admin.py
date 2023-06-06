from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from application.forms import EngineerUserCreationForm, EngineerUserChangeForm, TicketCreationForm
from application.models import EngineerUser, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    form = TicketCreationForm
    list_display = ('title', 'priority', 'status', 'reporter')
    list_filter = ('priority', 'status')
    search_fields = ('title', 'reporter__name')


@admin.register(EngineerUser)
class EngineerUserAdmin(UserAdmin):
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
        initial_user = EngineerUser.objects.get(pk=obj.pk)

        # Save the user model
        super().save_model(request, obj, form, change)

        # If the is_on_call status has changed to True, update other users
        if change and form.instance.is_on_call and not initial_user.is_on_call:
            EngineerUser.objects.exclude(pk=obj.pk).update(is_on_call=False)
