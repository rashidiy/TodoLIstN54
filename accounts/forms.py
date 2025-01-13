from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:  # define a metadata related to this class
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',

        )
