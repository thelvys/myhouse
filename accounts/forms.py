from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class StyleFormMixin:
    def style_fields(self):
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 text-[#1E283D] border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4B49AC] focus:border-transparent',
                'style': 'border-color: #E5E5E5;'
            })

class CustomUserCreationForm(UserCreationForm, StyleFormMixin):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')
        labels = {
            'email': _('Email'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Choose a password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already in use. Please try another one.'))
        return email

class CustomUserChangeForm(UserChangeForm, StyleFormMixin):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')
        labels = {
            'email': _('Email'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()

class CustomAuthenticationForm(AuthenticationForm, StyleFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()

class CustomPasswordResetForm(PasswordResetForm, StyleFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()

class CustomSetPasswordForm(SetPasswordForm, StyleFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()