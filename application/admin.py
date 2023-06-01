from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from application.models import EngineerUser, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'reporter')
    list_filter = ('priority', 'status')
    search_fields = ('title', 'reporter__name')


class EngineerUserAdminCreationForm(UserCreationForm):
    class Meta:
        model = EngineerUser
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")


class EngineerUserAdminChangeForm(UserChangeForm):
    class Meta:
        model = EngineerUser
        fields = '__all__'


class EngineerUserAdmin(UserAdmin):
    add_form = EngineerUserAdminCreationForm
    form = EngineerUserAdminChangeForm
    model = EngineerUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_on_call')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'is_on_call')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj:
            # Create the dropdown select field for is_on_call
            form.base_fields['is_on_call'] = forms.ChoiceField(
                choices=[(True, 'Yes'), (False, 'No')],
                label='Is On Call',
                required=False,
                widget=forms.Select(attrs={'class': 'admin-lookup'}),
            )

        return form

    def save_model(self, request, obj, form, change):
        # Get the initial value of is_on_call
        try:
            old_obj = self.model.objects.get(pk=obj.pk)
            initial_is_on_call = old_obj.is_on_call
        except self.model.DoesNotExist:
            initial_is_on_call = False

        # Save the user model
        super().save_model(request, obj, form, change)

        # If the is_on_call status has changed to True, update other users
        if change and obj.is_on_call and not initial_is_on_call:
            EngineerUser.objects.exclude(pk=obj.pk).update(is_on_call=False)


admin.site.register(EngineerUser, EngineerUserAdmin)
