from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _
from .forms import user_creation_form, user_change_form

from .models import User


class UserAdmin(BaseUserAdmin):
    add_form = user_creation_form
    form = user_change_form
    model = User
    list_display = ['phone', 'is_active', 'is_admin', 'viber_is_active', 'vbid', 'telegram_is_active', 'tgid', 'whatsapp_is_active', 'wtid',  'q_of_reminders', 'const_reminders', 'already_set_reminders', 'viber_check', 'whatsapp_check', 'telegram_check']
    list_filter = ('is_admin', 'is_active', 'is_admin','viber_is_active', 'vbid', 'telegram_is_active', 'tgid', 'whatsapp_is_active', 'wtid', 'q_of_reminders', 'const_reminders', 'already_set_reminders', 'viber_check', 'whatsapp_check', 'telegram_check')
    ordering = ('phone', 'is_active', 'is_admin', 'viber_is_active', 'vbid', 'telegram_is_active','tgid', 'whatsapp_is_active', 'wtid', 'q_of_reminders', 'const_reminders', 'already_set_reminders', 'viber_check', 'whatsapp_check', 'telegram_check')


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, error_messages = {
        'password_mismatch': _("Пароли не совпадают."),
    }
)


    class Meta:
        model = User
        fields = ('phone', )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Password don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_admin = True
        user.is_staff = True
        if commit:
            user.save()
        return user


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)

