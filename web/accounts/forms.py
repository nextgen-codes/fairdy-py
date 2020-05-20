from django import forms
from django.contrib.auth import validators
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class FairdyRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self:
            # Add Bootstrap classes to all the form's elements except the 'agree to conditions' checkbox
            if field.name != 'agree_to_conditions':
                field.field.widget.attrs.update({'class': 'form-control'})
                field.field.widget.attrs.update({'placeholder': field.label})

        self.fields['username'].widget.attrs.update({'autofocus': False})
        self.fields['email'].widget.attrs.update({'autofocus': True})

    email = forms.EmailField(max_length=254, help_text='You must enter a valid email address.')
    agree_to_conditions = forms.BooleanField(required=True, widget=forms.CheckboxInput, label='I agree to the terms and conditions above.')

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(required=True, validators={validators.UnicodeUsernameValidator}, label='New Username')


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(required=True, label='New Email Address')


class DeleteUserForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)


class ChangePasswordForm(forms.Form):
    password_old = forms.CharField(widget=forms.PasswordInput)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


class ResetPasswordForm(forms.Form):
    user_id = forms.IntegerField(required=True, widget=forms.HiddenInput)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(required=True)


class AdminEditUserForm(forms.Form):
    user_id = forms.IntegerField()
    block_cycle_limit = forms.IntegerField()
    is_staff = forms.BooleanField(required=False)

