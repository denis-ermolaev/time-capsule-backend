from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Capsules

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    remember_me = forms.BooleanField(required=False)
    
    
class CapsulesForm(forms.ModelForm):
    opening_after_date = forms.DateTimeField(widget=forms.TextInput(attrs={"type": "datetime-local"}))
    text = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Capsules # Указание модели
        fields = ['title', 'opening_after_date']
