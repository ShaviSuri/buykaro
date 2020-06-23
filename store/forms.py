from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='username',widget=forms.TextInput(attrs={'placeholder':'Username..','class':'form-control'}))
    email = forms.CharField(label='email',widget=forms.EmailInput(attrs={'placeholder':'Email..','class':'form-control'}))
    password1 = forms.CharField(label='password1',widget=forms.PasswordInput(attrs={'placeholder':'Enter password...','class':'form-control'}))
    password2 = forms.CharField(label='password2',widget=forms.PasswordInput(attrs={'placeholder':'Re-enter','class':'form-control'}))

class CreateUserForm(LoginForm,UserCreationForm):
	class Meta:
		model = User
		fields = ['username','email','password1','password2']

